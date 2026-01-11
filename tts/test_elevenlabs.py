#!/usr/bin/env python3
"""
Test ElevenLabs TTS - wybór głosu i benchmark opóźnień.

Uruchomienie:
    python tts/test_elevenlabs.py
    python tts/test_elevenlabs.py --model eleven_flash_v2_5
    python tts/test_elevenlabs.py --model eleven_v3

Wymagania:
    - pip install elevenlabs simpleaudio
    - Zmienna ELEVENLABS_API_KEY lub plik .env
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts.elevenlabs_tts import (
    ElevenLabsTTS,
    get_tts,
    generate_fillers,
    play_filler,
    get_filler_files,
)

from typing import Optional

TEST_MODEL = "eleven_multilingual_v2"


def test_list_voices():
    print("\n" + "=" * 60)
    print("TEST 1: LISTOWANIE GŁOSÓW")
    print("=" * 60)

    tts = get_tts()
    tts.list_voices(filter_multilingual=True)


def test_voice_selection():
    print("\n" + "=" * 60)
    print("TEST 2: WYBÓR GŁOSU")
    print("=" * 60)

    tts = get_tts()

    test_voices = ["Brian", "Daniel", "Alice", "Lily", "Matilda"]
    for voice_name in test_voices:
        try:
            voice_id = tts.select_voice(voice_name)
            print(f"✅ {voice_name}: {voice_id}")
        except ValueError as e:
            print(f"❌ {voice_name}: {e}")


def test_speak(model_id: Optional[str] = None):
    model = model_id or TEST_MODEL

    print("\n" + "=" * 60)
    print(f"TEST 3: SYNTEZA I ODTWARZANIE (model: {model})")
    print("=" * 60)

    tts = get_tts(voice_name="Brian", model_id=model)

    test_texts = [
        "Dzień dobry, witamy w Hotelu Aurora.",
        "Mamy wolne pokoje dwuosobowe w cenie dwieście czterdzieści złotych za dobę.",
        "Czy mogę prosić o Pana nazwisko do rezerwacji?",
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n🔊 Test {i}: {text}")
        tts.speak(text)
        print("   ✅ Zakończono")


def test_latency_benchmark():
    print("\n" + "=" * 60)
    print("TEST 4: BENCHMARK OPÓŹNIEŃ")
    print("=" * 60)

    tts = get_tts(voice_name="Brian")

    results = tts.benchmark_latency(
        test_text="Dzień dobry, witamy w Hotelu Aurora. Jak mogę pomóc?",
        models=["eleven_flash_v2_5", "eleven_turbo_v2_5", "eleven_multilingual_v2"],
    )

    print("\n📊 REKOMENDACJA:")
    if results:
        best = min(results, key=lambda x: x.time_to_first_byte_ms)
        print(f"   Najszybszy model: {best.model_id}")
        print(f"   TTFB: {best.time_to_first_byte_ms:.0f}ms")


def test_fillers():
    print("\n" + "=" * 60)
    print("TEST 5: FILLERY (DŹWIĘKI OCZEKIWANIA)")
    print("=" * 60)

    existing = get_filler_files()
    if not existing:
        print("\n🔧 Generuję fillery (jednorazowo)...")
        generate_fillers(voice_name="Brian")
    else:
        print(f"\n📁 Znaleziono {len(existing)} istniejących fillerów")

    print("\n🔊 Odtwarzam 3 losowe fillery:")
    for i in range(3):
        print(f"   Filler {i + 1}...")
        play_filler()

    print("   ✅ Zakończono")


def main():
    parser = argparse.ArgumentParser(description="Test ElevenLabs TTS")
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="eleven_multilingual_v2",
        help="Model TTS (np. eleven_v3, eleven_flash_v2_5, eleven_multilingual_v2)",
    )
    parser.add_argument(
        "--only-speak",
        action="store_true",
        help="Uruchom tylko test syntezy i odtwarzania",
    )
    args = parser.parse_args()

    global TEST_MODEL
    TEST_MODEL = args.model

    print("\n" + "🎤 " * 20)
    print("       ELEVENLABS TTS - TESTY")
    print("🎤 " * 20)

    if not os.getenv("ELEVENLABS_API_KEY"):
        print("\n❌ BRAK KLUCZA API!")
        print("   Ustaw zmienną środowiskową ELEVENLABS_API_KEY")
        print("   Przykład: export ELEVENLABS_API_KEY='twój_klucz'")
        sys.exit(1)

    try:
        if args.only_speak:
            test_speak(model_id=args.model)
        else:
            test_list_voices()
            test_voice_selection()
            test_speak(model_id=args.model)
            test_fillers()
            test_latency_benchmark()

        print("\n" + "=" * 60)
        print("✅ WSZYSTKIE TESTY ZAKOŃCZONE")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
