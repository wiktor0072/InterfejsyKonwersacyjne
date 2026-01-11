## Funkcjonalności modułu TTS

1. **Listowanie głosów**  
   `tts.list_voices()` — pokazuje dostępne głosy z oznaczeniem rekomendowanych dla języka polskiego

2. **Wybór głosu**  
   `tts.select_voice("George")` — ustawienie aktywnego głosu

3. **Synteza ze streamingiem**  
   `tts.speak(text)` — używa strumieniowania dla niskich opóźnień

4. **Benchmark opóźnień**  
   `tts.benchmark_latency()` — testuje TTFB (time to first byte) różnych modeli

---

### Uruchomienie testów

```bash
export ELEVENLABS_API_KEY='twój_klucz_api'
python tts/test_elevenlabs.py

python tts/test_elevenlabs.py --model eleven_v3 --only-speak
```

---

### Rekomendowane głosy dla języka polskiego

-   **George** (męski, spokojny) — ⭐ domyślny
-   **Charlotte** (żeński, profesjonalny)
-   **Aria** (żeński, naturalny)

---

### Dostępne modele (od najszybszego)

-   `eleven_flash_v2_5` — najniższa latencja
-   `eleven_turbo_v2_5` — balans szybkość/jakość
-   `eleven_multilingual_v2` — najwyższa jakość _(domyślny)_
