"""
Webowy interface Gradio dla recepcjonisty Hotel Aurora z TTS (ElevenLabs).
Automatyczne nagrywanie z detekcją ciszy + synteza mowy.

Uruchom: python gradio_app.py
Następnie otwórz http://localhost:7860 w przeglądarce.
"""

import sys
import os
import json
import threading
from datetime import date
from typing import List, Tuple, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from groq import Groq

# Importy z istniejących modułów
from llm.main import (
    init_db,
    check_availability,
    make_reservation,
    available_functions,
    hotel_tools,
    hotel_system_prompt,
    DB_PATH,
    ROOMS,
)

try:
    from tts.elevenlabs_tts import get_tts, ElevenLabsTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("[UWAGA] Brak modułu TTS ElevenLabs")

try:
    from google.cloud import speech
    import pyaudio
    import struct
    import time
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    pyaudio = None
    speech = None
    print("[UWAGA] Brak modułu Google Cloud Speech - nagrywanie głosowe niedostępne")

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch.nn.functional as F
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("[UWAGA] Brak modułu analizy sentymentu")


# --- GLOBALNE ZMIENNE ---
conversation_history: List[dict] = []
groq_client = Groq()
MODEL = "llama-3.3-70b-versatile"

# Model sentymentu
sentiment_model = None
sentiment_tokenizer = None

if SENTIMENT_AVAILABLE:
    try:
        print("⏳ Ładowanie modelu sentymentu...")
        sentiment_tokenizer = AutoTokenizer.from_pretrained("Voicelab/herbert-base-cased-sentiment")
        sentiment_model = AutoModelForSequenceClassification.from_pretrained("Voicelab/herbert-base-cased-sentiment")
        print("✅ Model sentymentu załadowany")
    except Exception as e:
        print(f"[UWAGA] Nie udało się załadować modelu sentymentu: {e}")
        SENTIMENT_AVAILABLE = False


# --- FUNKCJE POMOCNICZE ---

def analyze_sentiment(text: str) -> Tuple[str, float]:
    """Analizuje sentyment tekstu."""
    if not SENTIMENT_AVAILABLE or sentiment_model is None or sentiment_tokenizer is None:
        return ("NEUTRALNY", 0.0)
    
    try:
        LABELS = {0: "NEGATYWNY", 1: "NEUTRALNY", 2: "POZYTYWNY"}
        inputs = sentiment_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            logits = sentiment_model(**inputs).logits
        
        scores = F.softmax(logits, dim=-1)[0]
        best_idx = scores.argmax().item()
        
        return (LABELS[best_idx], scores[best_idx].item())
    except Exception as e:
        print(f"[SENTIMENT] Błąd: {e}")
        return ("NEUTRALNY", 0.0)


def record_with_silence_detection() -> Optional[str]:
    """Nagrywa głos z automatyczną detekcją ciszy (3 sekundy)."""
    if not SPEECH_AVAILABLE or speech is None or pyaudio is None:
        return None
    
    try:
        speech_client = speech.SpeechClient.from_service_account_file("llm/gcp_key.json")
        
        RATE = 16000
        CHUNK = int(RATE / 10)
        SILENCE_THRESHOLD = 500
        SILENCE_DURATION = 3.0
        MAX_RECORDING_TIME = 30
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="pl-PL",
            enable_automatic_punctuation=True,
        )
        
        def get_audio_level(data):
            count = len(data) // 2
            format_str = f"{count}h"
            shorts = struct.unpack(format_str, data)
            return max(abs(s) for s in shorts) if shorts else 0
        
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        
        print("🎤 Nagrywanie...")
        
        audio_frames = []
        last_sound_time = time.time()
        start_time = time.time()
        speech_started = False
        
        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_frames.append(data)
                
                level = get_audio_level(data)
                
                if level > SILENCE_THRESHOLD:
                    last_sound_time = time.time()
                    if not speech_started:
                        speech_started = True
                        print("🔊 Mówisz...")
                
                current_time = time.time()
                
                if speech_started and (current_time - last_sound_time) >= SILENCE_DURATION:
                    print("⏸️ Wykryto pauzę...")
                    break
                
                if (current_time - start_time) >= MAX_RECORDING_TIME:
                    print("⏱️ Maksymalny czas nagrywania")
                    break
                    
            except Exception as e:
                print(f"Błąd nagrywania: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        if not audio_frames or not speech_started:
            return ""
        
        audio_content = b"".join(audio_frames)
        print("⏳ Rozpoznawanie mowy...")
        
        audio = speech.RecognitionAudio(content=audio_content)
        response = speech_client.recognize(config=config, audio=audio)
        
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            print(f"✅ Rozpoznano: {transcript}")
            return transcript
        else:
            return ""
            
    except Exception as e:
        print(f"[STT] Błąd: {e}")
        return None


def process_with_llm(user_text: str, sentiment_label: str = "NEUTRALNY") -> Tuple[str, Optional[str]]:
    """Przetwarza tekst użytkownika przez LLM z narzędziami i generuje TTS."""
    global conversation_history
    
    messages = conversation_history.copy()
    if not messages or messages[0]["role"] != "system":
        system_prompt = hotel_system_prompt
        if sentiment_label != "NEUTRALNY":
            system_prompt += f"\n\n[KONTEKST EMOCJONALNY] Klient wyraża emocje: {sentiment_label}. Dostosuj ton odpowiedzi odpowiednio."
        messages.insert(0, {"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": user_text})
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=messages,  # type: ignore
            tools=hotel_tools,  # type: ignore
            tool_choice="auto",
            temperature=0.1,
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if not tool_calls:
            assistant_reply = response_message.content or ""
            messages.append({"role": "assistant", "content": assistant_reply})
            break
        
        messages.append(response_message.model_dump())
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            function_to_call = available_functions.get(function_name)
            if function_to_call:
                function_response = function_to_call(**function_args)
            else:
                function_response = json.dumps({"error": f"Nieznane narzędzie: {function_name}"})
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_response,
            })
    
    conversation_history = messages
    
    assistant_reply = next(
        (m["content"] for m in reversed(messages) if m["role"] == "assistant" and "content" in m),
        "Przepraszam, coś poszło nie tak."
    )
    
    # Generuj audio (TTS)
    audio_path = None
    if TTS_AVAILABLE and assistant_reply:
        try:
            tts = get_tts()
            audio_bytes = tts.generate(assistant_reply)
            
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_bytes)
                audio_path = f.name
        except Exception as e:
            print(f"[TTS] Błąd generowania audio: {e}")
    
    return assistant_reply, audio_path


# --- FUNKCJE GRADIO ---

def handle_voice_interaction(history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str, Optional[str]]:
    """Nagrywa głos, przetwarza przez LLM i zwraca odpowiedź z TTS."""
    if not SPEECH_AVAILABLE or speech is None:
        return history, "❌ Rozpoznawanie mowy niedostępne", None
    
    # Nagraj z automatyczną detekcją ciszy
    user_text = record_with_silence_detection()
    
    if not user_text:
        return history, "⚠️ Nie rozpoznano mowy. Spróbuj ponownie.", None
    
    # Analiza sentymentu
    sentiment_label, sentiment_score = analyze_sentiment(user_text)
    sentiment_emoji = {"POZYTYWNY": "👍", "NEUTRALNY": "😐", "NEGATYWNY": "👎"}.get(sentiment_label, "")
    
    # LLM + TTS
    assistant_reply, audio_path = process_with_llm(user_text, sentiment_label)
    
    # Historia
    history.append((f"🎤 {user_text}", assistant_reply))
    
    return history, f"{sentiment_emoji} {sentiment_label} ({sentiment_score*100:.1f}%) | 🎤 Kliknij ponownie aby kontynuować rozmowę", audio_path


def reset_conversation() -> Tuple[List, str]:
    """Resetuje konwersację."""
    global conversation_history
    conversation_history = []
    return [], "Kliknij 'Nagraj i wyślij' aby zacząć rozmowę"


def create_interface():
    """Tworzy interfejs Gradio."""
    init_db()
    
    with gr.Blocks(title="Hotel Aurora - Recepcja") as demo:
        gr.Markdown("""
        # 🏨 Hotel Aurora - Recepcjonista AI (z TTS)
        
        Witaj w systemie rezerwacji Hotel Aurora!
        
        **Jak używać:**
        1. Kliknij **"🎤 Nagraj i wyślij"**
        2. Zacznij mówić do mikrofonu
        3. System automatycznie wykryje koniec wypowiedzi (3 sekundy ciszy)
        4. Otrzymasz odpowiedź tekstową i **audio (odtwarzane automatycznie)**
        5. Kliknij ponownie **"🎤 Nagraj i wyślij"** aby kontynuować rozmowę
        """)
        
        chatbot = gr.Chatbot(
            label="Rozmowa z recepcjonistą",
            height=500
        )
        
        with gr.Row():
            record_btn = gr.Button("🎤 Nagraj i wyślij", variant="primary", size="lg", scale=3)
            clear_btn = gr.Button("🗑️ Nowa rozmowa", size="lg", scale=1)
        
        # Odpowiedź audio - automatyczne odtwarzanie
        audio_output = gr.Audio(
            label="🔊 Odpowiedź recepcjonisty",
            autoplay=True,
            type="filepath",
            visible=True
        )
        
        sentiment_output = gr.Textbox(
            label="Status",
            placeholder="Kliknij 'Nagraj i wyślij' aby zacząć rozmowę",
            interactive=False
        )
        
        # Events
        record_btn.click(
            fn=handle_voice_interaction,
            inputs=[chatbot],
            outputs=[chatbot, sentiment_output, audio_output]
        )
        
        clear_btn.click(
            fn=reset_conversation,
            outputs=[chatbot, sentiment_output]
        )
    
    return demo


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Uruchamianie Hotel Aurora Gradio Interface (z TTS)")
    print("="*60)
    print("🎤 Interfejs głosowy z detekcją ciszy + 🔊 ElevenLabs TTS")
    print("="*60)
    
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft()
    )
