"""
ElevenLabs Text-to-Speech module for Hotel Aurora receptionist.

Moduł obsługujący syntezę mowy przy użyciu ElevenLabs API.
Obsługuje streaming audio dla niskich opóźnień.
"""

import os
import time
import io
import threading
from typing import Optional, Generator, Dict, Any, List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    import pyaudio as pyaudio_type

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import stream as elevenlabs_stream

    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    ElevenLabs = None  # type: ignore
    elevenlabs_stream = None  # type: ignore

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None


@dataclass
class VoiceInfo:
    """Informacje o głosie ElevenLabs."""

    voice_id: str
    name: str
    category: str
    description: str
    labels: Dict[str, str]


@dataclass
class LatencyResult:
    """Wynik testu opóźnień."""

    model_id: str
    text_length: int
    time_to_first_byte_ms: float
    total_generation_ms: float
    audio_duration_ms: float


class ElevenLabsTTS:
    """
    Klasa do syntezy mowy przy użyciu ElevenLabs API.

    Obsługuje:
    - Listowanie dostępnych głosów
    - Generowanie audio (streaming i non-streaming)
    - Bezpośrednie odtwarzanie audio
    - Benchmarking opóźnień
    """

    # Modele ElevenLabs (od najszybszego)
    MODELS = {
        "eleven_flash_v2_5": "Najszybszy, optymalizowany pod kątem latencji",
        "eleven_turbo_v2_5": "Szybki, dobra jakość",
        "eleven_turbo_v2": "Szybki, poprzednia generacja",
        "eleven_multilingual_v2": "Najwyższa jakość, obsługa wielu języków w tym polskiego",
        "eleven_monolingual_v1": "Podstawowy model angielski",
    }

    # Rekomendowane głosy dla języka polskiego (multilingual)
    RECOMMENDED_POLISH_VOICES = [
        "Brian",  # Męski, głęboki, komfortowy - dobry dla recepcjonisty
        "Daniel",  # Męski, brytyjski, stabilny broadcaster
        "Alice",  # Żeński, brytyjski, edukacyjny
        "Lily",  # Żeński, brytyjski, aktorski
        "Matilda",  # Żeński, profesjonalny
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        voice_id: Optional[str] = None,
        optimize_streaming_latency: int = 3,
    ):
        """
        Inicjalizuje klienta ElevenLabs TTS.

        Args:
            api_key: Klucz API ElevenLabs (lub zmienna ELEVENLABS_API_KEY)
            model_id: ID modelu do użycia
            voice_id: ID głosu (jeśli None, zostanie wybrany automatycznie)
            optimize_streaming_latency: Poziom optymalizacji (0-4, wyższy = mniejsze opóźnienia)
        """
        if not ELEVENLABS_AVAILABLE:
            raise ImportError(
                "Brak biblioteki elevenlabs. Zainstaluj: pip install elevenlabs"
            )

        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Brak klucza API ElevenLabs. Ustaw zmienną ELEVENLABS_API_KEY "
                "lub przekaż api_key do konstruktora."
            )

        self.client = ElevenLabs(api_key=self.api_key)  # type: ignore[misc]
        self.model_id = model_id
        self.voice_id = voice_id
        self.optimize_streaming_latency = optimize_streaming_latency

        self._voices_cache: Optional[List[VoiceInfo]] = None
        self._pyaudio: Any = None

        print(f"[TTS] ElevenLabs zainicjalizowany (model: {model_id})")

    def get_voices(self, refresh: bool = False) -> List[VoiceInfo]:
        """
        Pobiera listę dostępnych głosów.

        Args:
            refresh: Wymuś odświeżenie cache

        Returns:
            Lista obiektów VoiceInfo
        """
        if self._voices_cache is not None and not refresh:
            return self._voices_cache

        print("[TTS] Pobieranie listy głosów...")
        response = self.client.voices.get_all()

        voices = []
        for voice in response.voices:
            labels = {}
            if voice.labels:
                labels = dict(voice.labels)

            voices.append(
                VoiceInfo(
                    voice_id=voice.voice_id,
                    name=voice.name or "",
                    category=voice.category or "unknown",
                    description=voice.description or "",
                    labels=labels,
                )
            )

        self._voices_cache = voices
        print(f"[TTS] Znaleziono {len(voices)} głosów")
        return voices

    def list_voices(self, filter_multilingual: bool = True) -> None:
        """
        Wyświetla dostępne głosy w czytelnej formie.

        Args:
            filter_multilingual: Pokaż tylko głosy obsługujące wiele języków
        """
        voices = self.get_voices()

        print("\n" + "=" * 60)
        print("DOSTĘPNE GŁOSY ELEVENLABS")
        print("=" * 60)

        for voice in voices:
            if filter_multilingual and voice.category not in [
                "premade",
                "professional",
            ]:
                continue

            name_parts = voice.name.split(" - ")
            short_name = name_parts[0] if name_parts else voice.name
            recommended = (
                "⭐ " if short_name in self.RECOMMENDED_POLISH_VOICES else "  "
            )

            print(f"\n{recommended}{voice.name}")
            print(f"   ID: {voice.voice_id}")
            print(f"   Kategoria: {voice.category}")
            if voice.labels:
                accent = voice.labels.get("accent", "")
                gender = voice.labels.get("gender", "")
                age = voice.labels.get("age", "")
                print(f"   Cechy: {gender}, {age}, {accent}".strip(", "))

        print("\n" + "=" * 60)
        print("⭐ = Rekomendowane dla języka polskiego")
        print("=" * 60 + "\n")

    def select_voice(self, voice_name: str) -> str:
        """
        Wybiera głos po nazwie i zwraca jego ID.

        Args:
            voice_name: Nazwa głosu (np. "George", "Charlotte")

        Returns:
            voice_id wybranego głosu
        """
        voices = self.get_voices()
        voice_name_lower = voice_name.lower()

        for voice in voices:
            name_parts = voice.name.split(" - ")
            short_name = name_parts[0].lower() if name_parts else voice.name.lower()

            if short_name == voice_name_lower or voice.name.lower() == voice_name_lower:
                self.voice_id = voice.voice_id
                print(f"[TTS] Wybrano głos: {voice.name} ({voice.voice_id})")
                return voice.voice_id

        raise ValueError(f"Nie znaleziono głosu o nazwie: {voice_name}")

    def _ensure_voice_selected(self) -> str:
        """Upewnia się, że głos jest wybrany. Jeśli nie, wybiera domyślny."""
        if self.voice_id:
            return self.voice_id

        voices = self.get_voices()
        for rec_name in self.RECOMMENDED_POLISH_VOICES:
            rec_name_lower = rec_name.lower()
            for voice in voices:
                name_parts = voice.name.split(" - ")
                short_name = name_parts[0].lower() if name_parts else voice.name.lower()
                if short_name == rec_name_lower:
                    self.voice_id = voice.voice_id
                    print(f"[TTS] Auto-wybrano głos: {voice.name}")
                    return self.voice_id

        for voice in voices:
            if voice.category == "premade":
                self.voice_id = voice.voice_id
                print(f"[TTS] Fallback głos: {voice.name}")
                return self.voice_id

        raise RuntimeError("Nie znaleziono żadnego dostępnego głosu")

    def generate(
        self,
        text: str,
        model_id: Optional[str] = None,
        voice_id: Optional[str] = None,
    ) -> bytes:
        voice = voice_id or self._ensure_voice_selected()
        model = model_id or self.model_id

        audio = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice,
            model_id=model,
        )

        if isinstance(audio, bytes):
            return audio
        return b"".join(audio)

    def generate_stream(
        self,
        text: str,
        model_id: Optional[str] = None,
        voice_id: Optional[str] = None,
    ) -> Generator[bytes, None, None]:
        """
        Generuje audio z tekstu (streaming).

        Args:
            text: Tekst do syntezy
            model_id: Opcjonalnie inny model
            voice_id: Opcjonalnie inny głos

        Yields:
            Chunki audio (MP3)
        """
        voice = voice_id or self._ensure_voice_selected()
        model = model_id or self.model_id

        audio_stream = self.client.text_to_speech.stream(
            text=text,
            voice_id=voice,
            model_id=model,
            optimize_streaming_latency=self.optimize_streaming_latency,
        )

        for chunk in audio_stream:
            if isinstance(chunk, bytes):
                yield chunk

    def speak(self, text: str, blocking: bool = True) -> None:
        if not text or not text.strip():
            return

        print(f"[TTS] Mówię: {text[:50]}{'...' if len(text) > 50 else ''}")
        self._speak_with_playback(text)

    def _speak_with_playback(self, text: str) -> None:
        import tempfile
        import subprocess

        audio_bytes = self.generate(text)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        try:
            subprocess.run(
                ["mpv", "--no-terminal", "--no-video", "--keep-open=no", temp_path],
                timeout=60,
                check=False,
            )
        except FileNotFoundError:
            try:
                subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_path],
                    timeout=60,
                    check=False,
                )
            except FileNotFoundError:
                try:
                    import simpleaudio as sa

                    wav_path = temp_path.replace(".mp3", ".wav")
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            temp_path,
                            wav_path,
                            "-loglevel",
                            "quiet",
                        ],
                        timeout=30,
                        check=False,
                    )

                    if os.path.exists(wav_path):
                        wave_obj = sa.WaveObject.from_wave_file(wav_path)
                        play_obj = wave_obj.play()
                        play_obj.wait_done()
                        os.unlink(wav_path)
                except Exception as e:
                    print(f"[TTS] Błąd odtwarzania: {e}")
        except subprocess.TimeoutExpired:
            print("[TTS] Timeout odtwarzania")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _speak_fallback(self, text: str) -> None:
        self._speak_with_playback(text)

    def benchmark_latency(
        self,
        test_text: str = "Dzień dobry, witamy w Hotelu Aurora.",
        models: Optional[List[str]] = None,
    ) -> List[LatencyResult]:
        """
        Testuje opóźnienia dla różnych modeli.

        Args:
            test_text: Tekst testowy
            models: Lista modeli do przetestowania (domyślnie wszystkie)

        Returns:
            Lista wyników LatencyResult
        """
        if models is None:
            models = list(self.MODELS.keys())

        results = []
        voice = self._ensure_voice_selected()

        print("\n" + "=" * 60)
        print("BENCHMARK OPÓŹNIEŃ ELEVENLABS TTS")
        print(f'Tekst testowy ({len(test_text)} znaków): "{test_text}"')
        print("=" * 60)

        for model in models:
            print(f"\n🔄 Testuję model: {model}...")

            try:
                # Test streaming - mierzymy czas do pierwszego bajtu
                start_time = time.time()
                first_byte_time = None
                total_bytes = 0

                audio_stream = self.client.text_to_speech.stream(
                    text=test_text,
                    voice_id=voice,
                    model_id=model,
                    optimize_streaming_latency=self.optimize_streaming_latency,
                )

                for chunk in audio_stream:
                    if isinstance(chunk, bytes):
                        if first_byte_time is None:
                            first_byte_time = time.time()
                        total_bytes += len(chunk)

                end_time = time.time()

                if first_byte_time is None:
                    print(f"   ❌ Brak danych audio")
                    continue

                ttfb_ms = (first_byte_time - start_time) * 1000
                total_ms = (end_time - start_time) * 1000

                # Szacowanie długości audio (MP3 ~128kbps = 16KB/s)
                estimated_audio_ms = (total_bytes / 16000) * 1000

                result = LatencyResult(
                    model_id=model,
                    text_length=len(test_text),
                    time_to_first_byte_ms=ttfb_ms,
                    total_generation_ms=total_ms,
                    audio_duration_ms=estimated_audio_ms,
                )
                results.append(result)

                print(
                    f"   ✅ TTFB: {ttfb_ms:.0f}ms | Total: {total_ms:.0f}ms | Audio: ~{estimated_audio_ms:.0f}ms"
                )

            except Exception as e:
                print(f"   ❌ Błąd: {e}")

        # Podsumowanie
        print("\n" + "-" * 60)
        print("PODSUMOWANIE (posortowane wg TTFB):")
        print("-" * 60)

        for r in sorted(results, key=lambda x: x.time_to_first_byte_ms):
            print(f"  {r.model_id:30} TTFB: {r.time_to_first_byte_ms:6.0f}ms")

        print("=" * 60 + "\n")

        return results

    def close(self) -> None:
        """Zwalnia zasoby."""
        if self._pyaudio:
            self._pyaudio.terminate()
            self._pyaudio = None


# Singleton dla łatwego użycia
_tts_instance: Optional[ElevenLabsTTS] = None


def get_tts(
    api_key: Optional[str] = None,
    model_id: str = "eleven_multilingual_v2",
    voice_name: Optional[str] = "Brian",
) -> ElevenLabsTTS:
    """
    Zwraca singleton instancji ElevenLabsTTS.

    Args:
        api_key: Klucz API (lub z env ELEVENLABS_API_KEY)
        model_id: Model do użycia
        voice_name: Nazwa głosu do użycia

    Returns:
        Skonfigurowana instancja ElevenLabsTTS
    """
    global _tts_instance

    if _tts_instance is None:
        _tts_instance = ElevenLabsTTS(
            api_key=api_key,
            model_id=model_id,
        )
    else:
        if model_id and _tts_instance.model_id != model_id:
            _tts_instance.model_id = model_id
            print(f"[TTS] Zmieniono model na: {model_id}")

    if voice_name:
        try:
            _tts_instance.select_voice(voice_name)
        except ValueError:
            print(f"[TTS] Głos '{voice_name}' niedostępny, używam domyślnego")

    return _tts_instance


def speak(text: str) -> None:
    tts = get_tts()
    tts.speak(text)


FILLERS_DIR = os.path.join(os.path.dirname(__file__), "fillers")

FILLER_TEXTS = [
    "Chwileczkę...",
    "Moment...",
    "Już sprawdzam...",
    "Proszę chwilę poczekać...",
    "Sekundkę...",
]


def generate_fillers(voice_name: str = "Brian", force: bool = False) -> List[str]:
    os.makedirs(FILLERS_DIR, exist_ok=True)

    tts = get_tts(voice_name=voice_name)
    generated = []

    for i, text in enumerate(FILLER_TEXTS):
        filename = f"filler_{i:02d}.mp3"
        filepath = os.path.join(FILLERS_DIR, filename)

        if os.path.exists(filepath) and not force:
            print(f"[FILLER] Pominięto (istnieje): {filename}")
            generated.append(filepath)
            continue

        print(f"[FILLER] Generuję: '{text}' -> {filename}")
        audio_bytes = tts.generate(text)

        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        generated.append(filepath)

    print(f"[FILLER] Gotowe: {len(generated)} plików w {FILLERS_DIR}")
    return generated


def get_filler_files() -> List[str]:
    if not os.path.exists(FILLERS_DIR):
        return []

    files = [
        os.path.join(FILLERS_DIR, f)
        for f in os.listdir(FILLERS_DIR)
        if f.endswith(".mp3")
    ]
    return sorted(files)


def play_filler() -> bool:
    import random
    import subprocess

    files = get_filler_files()
    if not files:
        print("[FILLER] Brak plików fillerów. Uruchom generate_fillers() najpierw.")
        return False

    filler_path = random.choice(files)

    try:
        subprocess.run(
            ["mpv", "--no-terminal", "--no-video", "--keep-open=no", filler_path],
            timeout=10,
            check=False,
        )
        return True
    except FileNotFoundError:
        try:
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filler_path],
                timeout=10,
                check=False,
            )
            return True
        except FileNotFoundError:
            print("[FILLER] Brak mpv/ffplay do odtwarzania")
            return False
    except subprocess.TimeoutExpired:
        return False
