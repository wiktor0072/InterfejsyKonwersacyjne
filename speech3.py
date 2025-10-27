import pyaudio
from google.cloud import speech
import queue


client = speech.SpeechClient.from_service_account_file("gcp_key.json")


RATE = 16000
CHUNK = int(RATE / 10)  # 100 ms


audio_q = queue.Queue()

def callback(in_data, frame_count, time_info, status_flags):
    audio_q.put(in_data)
    return (None, pyaudio.paContinue)

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback
)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code="pl-PL",
    enable_automatic_punctuation=True,
)

streaming_config = speech.StreamingRecognitionConfig(
    config=config,
    interim_results=True  # pokazuj wyniki częściowe
)

def request_generator():
    while True:
        data = audio_q.get()
        if data is None:
            break
        yield speech.StreamingRecognizeRequest(audio_content=data)

# 🚀 Uruchom strumieniowe rozpoznawanie
print("🎤 Nasłuchiwanie (powiedz coś po polsku)... Ctrl+C aby zakończyć")

responses = client.streaming_recognize(streaming_config, request_generator())
try:
    for response in responses:
        for result in response.results:
            if result.is_final:
                print(f"✅ {result.alternatives[0].transcript}")
            else:
                print(f"⏳ {result.alternatives[0].transcript}", end="\r")
except KeyboardInterrupt:
    print("\n🛑 Zakończono nasłuchiwanie.")
    stream.stop_stream()
    stream.close()
    p.terminate()
