import sys
import json
from groq import Groq
import sqlite3
from datetime import date, timedelta
import os
import threading
import io

# Speech recognition imports
try:
    import pyaudio
    from google.cloud import speech

    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("[UWAGA] Brak pyaudio lub google-cloud-speech. Tryb głosowy niedostępny.")

# --- KONFIGURACJA HOTELU ---
# Słownik pokoi: numer -> (pojemność, cena za dobę w PLN)
ROOMS = {
    101: {"capacity": 2, "price": 240},  # Pokój 2-osobowy
    102: {"capacity": 2, "price": 240},  # Pokój 2-osobowy
    103: {"capacity": 2, "price": 240},  # Pokój 2-osobowy
    104: {"capacity": 2, "price": 240},  # Pokój 2-osobowy
    201: {"capacity": 4, "price": 400},  # Pokój 4-osobowy
    202: {"capacity": 4, "price": 400},  # Pokój 4-osobowy
}


# --- 1. BAZA DANYCH I DANE STARTOWE ---

def init_db():
    conn = sqlite3.connect('hotel_aurora.db')
    cursor = conn.cursor()

    # Usuwamy starą tabelę (może mieć inny schemat z poprzednich uruchomień)
    cursor.execute('DROP TABLE IF EXISTS reservations')

    # Tworzymy tabelę od nowa z poprawnym schematem
    cursor.execute('''
                   CREATE TABLE reservations
                   (
                       id          INTEGER PRIMARY KEY AUTOINCREMENT,
                       room_number INTEGER,
                       last_name   TEXT,
                       start_date  TEXT,
                       end_date    TEXT
                   )
                   ''')

    # --- SCENARIUSZ UŻYTKOWNIKA ---
    # Pokoje 101, 102 i 201 są zajęte od dzisiaj przez tydzień.
    # Pozostałe pokoje są wolne.

    today = date.today()
    end_day = today + timedelta(days=7)  # Tydzień = dziś + 7 dni

    print(f"[SYSTEM] Generowanie rezerwacji od {today} do {end_day}...")

    # Pokój 101 (2-os.) zajęty przez Nowaka
    cursor.execute(
        'INSERT INTO reservations (room_number, last_name, start_date, end_date) VALUES (?, ?, ?, ?)',
        (101, "Nowak", today.isoformat(), end_day.isoformat())
    )

    # Pokój 102 (2-os.) zajęty przez Kowalskiego
    cursor.execute(
        'INSERT INTO reservations (room_number, last_name, start_date, end_date) VALUES (?, ?, ?, ?)',
        (102, "Kowalski", today.isoformat(), end_day.isoformat())
    )

    # Pokój 201 (4-os.) zajęty przez Wiśniewskiego
    cursor.execute(
        'INSERT INTO reservations (room_number, last_name, start_date, end_date) VALUES (?, ?, ?, ?)',
        (201, "Wiśniewski", today.isoformat(), end_day.isoformat())
    )

    conn.commit()
    print("[SYSTEM] Baza gotowa. Pokoje 101, 102, 201 są zajęte. Pokoje 103, 104, 202 są wolne.")
    conn.close()


# --- 2. FUNKCJE (NARZĘDZIA) ---

def check_availability(query_date: str, room_type: int = None) -> str:
    """Sprawdza dostępność pokoi w podanym dniu."""
    with sqlite3.connect('hotel_aurora.db') as conn:
        cursor = conn.cursor()

        # Pokój jest zajęty jeśli: start_date <= query_date < end_date
        # (end_date to dzień wymeldowania - pokój jest już wolny tego dnia)
        cursor.execute('''
                       SELECT room_number
                       FROM reservations
                       WHERE start_date <= ?
                         AND end_date > ?
                       ''', (query_date, query_date))
        occupied = {row[0] for row in cursor.fetchall()}

        available_rooms = [
            {"room_number": room, "capacity": info["capacity"], "price_per_night": info["price"]}
            for room, info in ROOMS.items()
            if room not in occupied and (room_type is None or info["capacity"] == room_type)
        ]

        return json.dumps({
            "date": query_date,
            "room_type_filter": room_type,
            "available_rooms": available_rooms,
            "total_available": len(available_rooms)
        }, ensure_ascii=False)


def make_reservation(start_date: str, end_date: str, last_name: str, room_type: int = 2) -> str:
    """Rezerwuje jeden pokój wybranego typu. Dla wielu pokoi wywołaj wielokrotnie."""

    # Walidacja nazwiska - odrzucamy placeholdery i puste wartości
    invalid_keywords = ["podaj", "proszę", "nazwisko", "unknown", "brak", "?", "nie wiem", "nieznane"]
    name_lower = (last_name or "").lower().strip()

    if not name_lower or len(name_lower) < 2 or any(kw in name_lower for kw in invalid_keywords):
        return json.dumps({
            "success": False,
            "error": "Brak nazwiska gościa. Proszę najpierw uzyskać nazwisko od klienta."
        }, ensure_ascii=False)

    # Walidacja typu pokoju
    if room_type not in [2, 4]:
        return json.dumps({
            "success": False,
            "error": f"Nieprawidłowy typ pokoju: {room_type}. Dostępne typy: 2 (dwuosobowy) lub 4 (czteroosobowy)."
        }, ensure_ascii=False)

    with sqlite3.connect('hotel_aurora.db') as conn:
        cursor = conn.cursor()

        # Rezerwacje nachodzą na siebie jeśli: existing_start < new_end AND existing_end > new_start
        cursor.execute('''
                       SELECT DISTINCT room_number
                       FROM reservations
                       WHERE start_date < ?
                         AND end_date > ?
                       ''', (end_date, start_date))
        occupied = {row[0] for row in cursor.fetchall()}

        # Znajdujemy pierwszy wolny pokój o wybranym typie (dokładna pojemność)
        selected_room = next(
            (room for room, info in ROOMS.items()
             if room not in occupied and info["capacity"] == room_type),
            None
        )

        if not selected_room:
            room_name = "dwuosobowych" if room_type == 2 else "czteroosobowych"
            return json.dumps({
                "success": False,
                "error": f"Brak wolnych pokoi {room_name} w terminie {start_date} - {end_date}"
            }, ensure_ascii=False)

        cursor.execute(
            'INSERT INTO reservations (room_number, last_name, start_date, end_date) VALUES (?, ?, ?, ?)',
            (selected_room, last_name, start_date, end_date)
        )

        # Obliczamy liczbę nocy i całkowitą cenę
        from datetime import datetime
        nights = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days
        room_info = ROOMS[selected_room]
        total_price = nights * room_info["price"]

        return json.dumps({
            "success": True,
            "room_number": selected_room,
            "capacity": room_info["capacity"],
            "price_per_night": room_info["price"],
            "nights": nights,
            "total_price": total_price,
            "last_name": last_name,
            "start_date": start_date,
            "end_date": end_date
        }, ensure_ascii=False)


# Mapowanie funkcji po nazwie
available_functions = {
    "check_availability": check_availability,
    "make_reservation": make_reservation,
}

# Schemat narzędzi dla Groq (format JSON Schema)
hotel_tools = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Sprawdza dostępność pokoi hotelowych w podanym dniu. Zwraca listę wolnych pokoi z ich pojemnością i ceną.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_date": {
                        "type": "string",
                        "description": "Data w formacie RRRR-MM-DD, np. 2026-01-05"
                    },
                    "room_type": {
                        "type": ["integer", "null"],
                        "description": "Opcjonalny typ pokoju: 2 (dwuosobowy) lub 4 (czteroosobowy). Bez podania zwraca wszystkie."
                    }
                },
                "required": ["query_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_reservation",
            "description": "Rezerwuje JEDEN pokój wybranego typu. Jeśli klient chce wiele pokoi (np. 2 pokoje dwuosobowe), wywołaj tę funkcję odpowiednią liczbę razy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Data początku rezerwacji w formacie RRRR-MM-DD"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Data końca rezerwacji w formacie RRRR-MM-DD"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Nazwisko gościa dokonującego rezerwacji"
                    },
                    "room_type": {
                        "type": "integer",
                        "description": "Typ pokoju: 2 (dwuosobowy, 240 PLN/noc) lub 4 (czteroosobowy, 400 PLN/noc)"
                    }
                },
                "required": ["start_date", "end_date", "last_name", "room_type"]
            }
        }
    }
]

# --- 3. PROMPT SYSTEMOWY ---

hotel_system_prompt = f"""
ROLA: Jesteś profesjonalnym recepcjonistą w Hotelu Aurora. KLUCZOWE, ZEBYS NIE HALUCYNOWAL I NIE ZMYSLAL. JESLI NIE MASZ JAKIEJS INFORMACJI PO PROSTU POINFORMUJ O TYM KLIENTA I PRZEKIERUJ GO BEZPOSREDNIO DO RECEPCJI.
CEL: Pomagasz gościom i dokonujesz rezerwacji używając dostępnych narzędzi.
DATA DZIŚ: {date.today()}

OFERTA POKOI:
- 4 pokoje dwuosobowe (numery 101-104) - 240 PLN/dobę
- 2 pokoje czteroosobowe (numery 201-202) - 400 PLN/dobę

BAZA WIEDZY (INFORMACYJNA):
- Doba hotelowa: od 14:00 do 11:00 dnia następnego.
- Śniadania: serwowane w godz. 7:00-10:00 w restauracji hotelowej w formie szwedzkiego stołu. Koszt śniadania to 50pln/dobe od osoby. Śniadania nie są wliczone w cenę pokoju.
- Wi-Fi: Sieć "Aurora_Guest", hasło: "hotel2024".
- Basen i SPA: Poziom -1, czynne 8:00-22:00. Wstęp dla gości gratis.
- Zwierzęta: Akceptujemy psy do 10kg (opłata 50 zł/doba).
- Parking: Podziemny, płatny 40 zł/doba.

INSTRUKCJE OBSŁUGI NARZĘDZI:
1. Dzisiejsza data to: {date.today()}. Używaj jej gdy klient mówi "dzisiaj" lub "jutro".
2. Jeśli klient pyta o wolny pokój -> użyj `check_availability`. Możesz podać room_type (2 lub 4) aby filtrować.
3. Jeśli klient chce rezerwować -> zbierz: daty (od-do), TYP POKOJU (2-osobowy lub 4-osobowy), nazwisko. Jeśli nie masz nazwiska klienta - dopytaj o nie. Klient to nie nazwisko!!! Na początku nie znasz nazwiska klienta!!! Ważne, żebyś nie wywoływał tej funkcji dopóki nie znasz nazwiska klienta. To bardzo ważne.
4. WAŻNE: `make_reservation` rezerwuje JEDEN pokój. Dla 2 pokoi dwuosobowych wywołaj funkcję DWA RAZY z room_type=2.
5. Narzędzia zwracają dane JSON - zinterpretuj je i przekaż klientowi w naturalny sposób.
6. UZYSKAJ WSZYSTKIE INFORMACJE. Jeśli klient ich nie poda - DOPYTAJ zanim wywołasz narzędzie. TO KLUCZOWE!!!

ZASADY ODPOWIEDZI:
1. Odpowiadaj krótko (max 2-3 zdania), naturalnie, bez markdowna.
2. TO JEST BARDZO WAZNE!!! Jeśli nie masz informacji - przekieruj do managera lub na stronę internetową.
"""


# --- 4. ROZPOZNAWANIE MOWY ---

def get_voice_input() -> str:
    """Nagrywa głos użytkownika i zwraca rozpoznany tekst.
    Nagrywanie kończy się automatycznie po 3 sekundach ciszy.
    """
    if not SPEECH_AVAILABLE:
        print("\n❌ TRYB GŁOSOWY NIEDOSTĘPNY")
        print("   Brak wymaganych bibliotek: pyaudio i/lub google-cloud-speech")
        print("   Zainstaluj je poleceniem: pip install pyaudio google-cloud-speech")
        return None

    try:
        import struct
        import time

        # Inicjalizacja
        speech_client = speech.SpeechClient.from_service_account_file("gcp_key.json")

        RATE = 16000
        CHUNK = int(RATE / 10)  # 100ms
        SILENCE_THRESHOLD = 500  # Próg głośności (dostosuj w razie potrzeby)
        SILENCE_DURATION = 2.0  # Sekundy ciszy przed zakończeniem
        MAX_RECORDING_TIME = 30  # Maksymalny czas nagrywania (sekundy)

        # Konfiguracja rozpoznawania
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="pl-PL",
            enable_automatic_punctuation=True,
        )

        def get_audio_level(data):
            """Oblicza poziom głośności fragmentu audio."""
            count = len(data) // 2
            format_str = f"{count}h"
            shorts = struct.unpack(format_str, data)
            return max(abs(s) for s in shorts) if shorts else 0

        # Inicjalizacja pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("\n🎤 Mów teraz... (nagrywanie zakończy się po 3 sek. ciszy)")

        audio_frames = []
        last_sound_time = time.time()
        start_time = time.time()
        speech_started = False

        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_frames.append(data)

                level = get_audio_level(data)

                # Sprawdź czy użytkownik zaczął mówić
                if level > SILENCE_THRESHOLD:
                    last_sound_time = time.time()
                    if not speech_started:
                        speech_started = True
                        print("   🔊 Mówisz...")

                current_time = time.time()

                # Jeśli już zaczął mówić i jest cisza przez SILENCE_DURATION
                if speech_started and (current_time - last_sound_time) >= SILENCE_DURATION:
                    print("   ⏸️  Wykryto pauzę - kończę nagrywanie...")
                    break

                # Maksymalny czas nagrywania
                if (current_time - start_time) >= MAX_RECORDING_TIME:
                    print("   ⏱️  Osiągnięto maksymalny czas nagrywania.")
                    break

            except Exception as e:
                print(f"   [Błąd nagrywania: {e}]")
                break

        # Zamknij strumień
        stream.stop_stream()
        stream.close()
        p.terminate()

        if not audio_frames or not speech_started:
            print("[UWAGA] Nie wykryto mowy.")
            return ""

        # Złącz wszystkie fragmenty audio
        audio_content = b''.join(audio_frames)

        print("⏳ Rozpoznaję mowę...")

        # Wyślij do Google Speech API
        audio = speech.RecognitionAudio(content=audio_content)
        response = speech_client.recognize(config=config, audio=audio)

        # Pobierz tekst
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            print(f"✅ Rozpoznano: {transcript}")
            return transcript
        else:
            print("[UWAGA] Nie rozpoznano żadnej mowy.")
            return ""

    except FileNotFoundError:
        print("\n❌ BRAK PLIKU gcp_key.json")
        print("   Aby używać rozpoznawania mowy, potrzebujesz pliku z kluczem Google Cloud.")
        print("   1. Przejdź do console.cloud.google.com")
        print("   2. Utwórz projekt i włącz Cloud Speech-to-Text API")
        print("   3. Utwórz klucz serwisowy (Service Account) i pobierz jako JSON")
        print("   4. Zapisz plik jako 'gcp_key.json' w folderze z aplikacją")
        return None
    except Exception as e:
        print(f"\n❌ BŁĄD ROZPOZNAWANIA MOWY: {e}")
        print("   Sprawdź mikrofon i połączenie internetowe.")
        return None


# --- 5. GŁÓWNA PĘTLA APLIKACJI ---

def reception():
    # Inicjalizacja bazy przy starcie
    init_db()

    # Inicjalizacja klienta Groq
    client = Groq()

    # Model Groq
    MODEL = "llama-3.3-70b-versatile"

    # Historia konwersacji
    messages = [
        {"role": "system", "content": hotel_system_prompt}
    ]

    print("--- HOTEL AURORA RECEPCJA (wersja z Groq/LLaMA + GŁOS) ---")
    print(f"(Data systemowa: {date.today()})")
    print(f"(Model: {MODEL})")
    print("(Oferta: 4 pokoje 2-os. [101-104], 2 pokoje 4-os. [201-202])")
    if not SPEECH_AVAILABLE:
        print("\n❌ TRYB GŁOSOWY NIEDOSTĘPNY - aplikacja wymaga rozpoznawania mowy.")
        print("   Zainstaluj: pip install pyaudio google-cloud-speech")
        return
    print("🎤 TRYB GŁOSOWY: Mów do mikrofonu. Nagrywanie zakończy się automatycznie po 3 sek. ciszy.")
    print("-" * 60)

    try:
        while True:
            user_input = get_voice_input()

            # Jeśli None - błąd krytyczny, kończymy
            if user_input is None:
                print("\n--- Aplikacja zatrzymana z powodu błędu. ---")
                break

            if not user_input.strip():
                continue

            # Dodajemy wiadomość użytkownika do historii
            messages.append({"role": "user", "content": user_input})

            # Pętla agentic - kontynuujemy dopóki model chce wywoływać narzędzia
            max_iterations = 5
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                # Wywołanie API Groq
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=hotel_tools,
                    tool_choice="auto",
                    temperature=0.1  # Niska temperatura dla spójności
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                # Jeśli model nie chce wywoływać narzędzi - wychodzimy z pętli
                if not tool_calls:
                    # Dodajemy odpowiedź asystenta do historii
                    messages.append({
                        "role": "assistant",
                        "content": response_message.content
                    })
                    print(f"RECEPCJONISTA: {response_message.content}")
                    break

                # Model chce wywołać narzędzia
                # Dodajemy odpowiedź asystenta (z tool_calls) do historii
                messages.append(response_message)

                # Wykonujemy każde wywołane narzędzie
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"[DEBUG] Wywołuję narzędzie: {function_name}({function_args})")

                    # Wykonaj funkcję
                    function_to_call = available_functions.get(function_name)
                    if function_to_call:
                        function_response = function_to_call(**function_args)
                    else:
                        function_response = json.dumps({"error": f"Nieznane narzędzie: {function_name}"})

                    print(f"[DEBUG] Wynik narzędzia: {function_response}")

                    # Dodajemy wynik narzędzia do historii
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response
                    })

            # Zabezpieczenie przed nieskończoną pętlą
            if iteration >= max_iterations:
                print("[SYSTEM] Osiągnięto maksymalną liczbę iteracji narzędzi.")

    except KeyboardInterrupt:
        print("\n\n--- Koniec pracy recepcji. Do widzenia! ---")
        sys.exit(0)
    except Exception as e:
        print(f"\nWystąpił błąd: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    reception()
