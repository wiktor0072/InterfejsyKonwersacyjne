from TTS.api import TTS
import simpleaudio as sa  # do odtwarzania

# Wybierz model obsługujący język polski
# Możesz sprawdzić listę modeli: https://huggingface.co/models?search=coqui-tts-polish
model_name = "tts_models/pl/mai_female/vits"

# Załaduj model
tts = TTS(model_name)

# Tekst do przeczytania
text = """Dzień dobry Państwu! Tu Anna Nowicka z redakcji Radio Info 24.
Jest piątek, 7 listopada 2025 roku, godzina 8:45, a to najważniejsze wiadomości dnia.

Według danych GUS-u, w ciągu ostatnich 3 lat liczba nowych firm w Polsce wzrosła o 12,7%, głównie w sektorach IT, e-commerce oraz tzw. green tech.
Ministerstwo Finansów poinformowało, że od 1 stycznia 2026 r. wchodzą w życie nowe przepisy dotyczące podatku VAT, m.in. zmiana stawek dla produktów spożywczych itp.

Tymczasem w branży technologicznej, koncern Tesla Inc. zapowiedział wprowadzenie modelu Cybertruck 2.0, który ma osiągać prędkość 0–100 km/h w 3,2 sekundy.
Warto dodać, że – jak podaje BBC – produkcja ma rozpocząć się w II kwartale 2026 r.

W świecie sportu, polska reprezentacja w piłce siatkowej pokonała wczoraj Francję 3:1, zapewniając sobie awans do półfinału Mistrzostw Europy.
Najlepszym zawodnikiem meczu został Kamil Semeniuk, zdobywając 22 punkty, w tym 5 asów serwisowych.

Jeśli chodzi o pogodę, IMGW prognozuje dziś zachmurzenie umiarkowane, miejscami przelotne opady deszczu, a temperatura maksymalna wyniesie około 10°C.
W górach może spaść pierwszy śnieg – i to już w nocy z soboty na niedzielę.

Na koniec krótka informacja kulturalna: w Krakowie, w dniach 14–17 listopada, odbędzie się Festiwal Filmów Krótkich „MiniFrame”, gdzie pokazanych zostanie ponad 80 produkcji z 22 krajów.

To już wszystko w tym wydaniu.
Dziękujemy za uwagę i zapraszamy ponownie po godzinie 9:00 – szczegóły, komentarze, ciekawostki itd.
"""

# Generuj dźwięk i zapisz do pliku WAV
tts.tts_to_file(text=text, file_path="polish_voice.wav")

# Odtwórz dźwięk (opcjonalnie)
wave_obj = sa.WaveObject.from_wave_file("polish_voice.wav")
play_obj = wave_obj.play()
play_obj.wait_done()