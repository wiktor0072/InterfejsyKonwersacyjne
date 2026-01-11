from vosk import Model, KaldiRecognizer
import pyaudio
import json

model = Model("vosk-model-small-pl-0.22")
recognizer = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

print("Mów teraz... (Ctrl+C, aby przerwać)")

full_text = []

try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                full_text.append(text)
except KeyboardInterrupt:
    print("\nZakończono nagrywanie.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

    final = json.loads(recognizer.FinalResult()).get("text", "").strip()
    if final:
        full_text.append(final)

    print("📄 Pełny wynik końcowy:")
    print(" ".join(full_text))
