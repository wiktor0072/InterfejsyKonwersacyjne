# Hotel Aurora - Nowoczesny Frontend z Wizualizacją Głosu

## Context

### Original Request
Użytkownik chce stworzyć nowoczesny, minimalistyczny frontend dla aplikacji Hotel Aurora (voice assistant do rezerwacji hotelowych) z:
- Wizualizacją głosu za pomocą cząsteczek (particles)
- Animowanymi gradientami w tle
- Wizualizacją mowy użytkownika i asystenta
- Historią czatu

### Interview Summary
**Key Discussions**:
- **Framework**: React (wybór użytkownika)
- **Wizualizacja**: tsParticles reagujące na audio (oba głosy - user + asystent)
- **Backend**: FastAPI wrapper na istniejący CLI (`llm/main.py`)
- **Transkrypcja**: Historia czatu w stylu bąbelków wiadomości
- **Responsywność**: Tylko desktop
- **Kolorystyka**: Dark mode
- **UI**: Minimalistyczny (bez dashboardu hotelowego)
- **Audio streaming**: Pełny plik MP3 (prostsze, rekomendowane)
- **Sesja**: Baza danych SQLite (trwała historia)
- **Deployment**: Localhost (dev)
- **Fallback**: Jeśli TTS nie działa → fallback do tekstu
- **Sentyment**: Zintegrować moduł `Emocje/main.py`
- **Testy**: Manual QA (brak automatycznych)

**Research Findings**:
- Obecnie brak web API - tylko CLI w `llm/main.py`
- Voice pipeline: Google STT → Groq LLM → ElevenLabs TTS
- Zalecane biblioteki: tsParticles, @mesh-gradient/react
- Audio: INPUT LINEAR16 16kHz, OUTPUT MP3

### Metis Review
**Identified Gaps** (addressed):
- Audio streaming strategy → Pełny plik MP3 (prostsze)
- Session persistence → SQLite (trwałe)
- Particles target → Oba głosy (user + asystent)
- Error fallback → Tekst gdy TTS nie działa
- Sentiment integration → TAK, włączyć

---

## Work Objectives

### Core Objective
Stworzyć nowoczesny frontend React z wizualizacją głosu (tsParticles) i animowanymi gradientami, zintegrowany z FastAPI backendem opakowującym istniejącą logikę voice assistant Hotel Aurora.

### Concrete Deliverables
1. **Backend FastAPI** (`backend/main.py`):
   - WebSocket endpoint dla komunikacji real-time
   - Integracja z istniejącą logiką z `llm/main.py`
   - Obsługa audio (WebM → LINEAR16 transcoding)
   - Integracja sentymentu z `Emocje/main.py`
   - Zapis historii sesji do SQLite

2. **Frontend React** (`frontend/`):
   - Aplikacja React z tsParticles
   - Animowane mesh gradienty w tle
   - Panel czatu z historią wiadomości
   - Przycisk push-to-talk + toggle ciągłego słuchania
   - Web Audio API dla wizualizacji w real-time
   - Odtwarzanie audio TTS

### Definition of Done
- [ ] `npm run dev` → frontend działa na `localhost:5173`
- [ ] `uvicorn backend.main:app` → API działa na `localhost:8000`
- [ ] Użytkownik może nagrać głos → widzi transkrypcję → słyszy odpowiedź TTS
- [ ] Particles reagują na oba głosy (user + asystent)
- [ ] Historia czatu zapisuje się w bazie i przetrwa restart

### Must Have
- Dark mode jako jedyny tryb
- Desktop layout (min-width: 1024px)
- Push-to-talk (przytrzymaj przycisk)
- Ciągłe słuchanie (toggle on/off)
- Historia czatu w bąbelkach
- Animowane tło gradient mesh
- tsParticles reagujące na audio
- Fallback do tekstu gdy TTS nie działa
- Integracja analizy sentymentu
- Trwała historia sesji (SQLite)

### Must NOT Have (Guardrails)
- ❌ Dashboard hotelowy (lista pokoi, ceny, kalendarz)
- ❌ System logowania/rejestracji użytkowników
- ❌ Mobile responsywność
- ❌ Light mode
- ❌ Płatności
- ❌ Panel admina bazy danych
- ❌ Analytics/tracking
- ❌ Automatyczne testy
- ❌ Custom audio effects (reverb, noise gate)
- ❌ Edycja promptu LLM w UI
- ❌ Deployment scripts

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: NO
- **User wants tests**: NO (Manual-only)
- **Framework**: Brak (manual QA)

### Manual QA Approach
Każde zadanie zawiera procedury weryfikacji manualnej:
- **Frontend/UI**: Playwright browser automation
- **API/Backend**: curl / httpie
- **Audio**: Mikrofon + głośniki (fizyczna weryfikacja)

---

## Task Flow

```
[Faza 1: Backend Foundation]
    1 (Struktura projektu)
           ↓
    2 (FastAPI + WebSocket)
           ↓
    3 (Integracja llm/main.py)
           ↓
    4 (Audio transcoding)
           ↓
    5 (Sentyment)
           ↓
    6 (Sesje SQLite)

[Faza 2: Frontend Core]
    7 (React setup)
           ↓
    8 (Mesh gradient background)
           ↓
    9 (Chat UI)
           ↓
    10 (WebSocket client)
           ↓
    11 (Audio recording)
           ↓
    12 (Audio playback)

[Faza 3: Wizualizacja]
    13 (tsParticles setup)
           ↓
    14 (Audio reactive particles - user voice)
           ↓
    15 (Audio reactive particles - TTS voice)
           ↓
    16 (Push-to-talk + continuous listening UI)

[Faza 4: Polish & QA]
    17 (Error handling + fallback)
           ↓
    18 (Loading states)
           ↓
    19 (Final QA)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 7, 8 | React setup i gradient mogą być równolegle |
| B | 14, 15 | Dwa rodzaje wizualizacji audio niezależne |

| Task | Depends On | Reason |
|------|------------|--------|
| 2 | 1 | Potrzebna struktura katalogów |
| 3 | 2 | Potrzebny działający FastAPI |
| 10 | 2, 7 | Wymaga backendu i frontendu |
| 11, 12 | 10 | Wymagają działającego WebSocket |
| 14, 15 | 13 | Wymagają podstawowego tsParticles |

---

## TODOs

### Faza 1: Backend Foundation

- [x] 1. Utworzenie struktury katalogów projektu

  **What to do**:
  - Utworzyć katalog `backend/` dla FastAPI
  - Utworzyć katalog `frontend/` dla React
  - Utworzyć `backend/requirements.txt` z zależnościami
  - Utworzyć `backend/__init__.py`

  **Must NOT do**:
  - Nie modyfikować istniejących plików w `llm/`

  **Parallelizable**: NO (to jest pierwszy krok)

  **References**:
  
  **Pattern References**:
  - `llm/main.py` - istniejąca logika do owinięcia w API
  - `Emocje/main.py` - moduł sentymentu do integracji
  
  **Documentation References**:
  - `AGENTS.md:Setup` - aktualne zależności projektu

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] `ls backend/` → pokazuje `__init__.py`, `requirements.txt`
  - [ ] `ls frontend/` → katalog istnieje
  - [ ] `cat backend/requirements.txt` → zawiera: fastapi, uvicorn, websockets, python-multipart, ffmpeg-python

  **Commit**: YES
  - Message: `feat(structure): add backend and frontend directories`
  - Files: `backend/`, `frontend/`

---

- [x] 2. Utworzenie FastAPI z WebSocket endpoint

  **What to do**:
  - Utworzyć `backend/main.py` z podstawową aplikacją FastAPI
  - Dodać endpoint `/ws` dla WebSocket
  - Skonfigurować CORS dla localhost
  - Dodać health check endpoint `/health`

  **Must NOT do**:
  - Nie implementować logiki LLM jeszcze
  - Nie dodawać autentykacji

  **Parallelizable**: NO (zależy od 1)

  **References**:
  
  **External References**:
  - FastAPI WebSocket docs: https://fastapi.tiangolo.com/advanced/websockets/
  
  **Pattern References**:
  - Standardowy wzorzec FastAPI + CORS dla development

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] `cd backend && uvicorn main:app --reload` → serwer startuje na 8000
  - [ ] `curl http://localhost:8000/health` → `{"status": "ok"}`
  - [ ] `websocat ws://localhost:8000/ws` → połączenie nawiązane

  **Commit**: YES
  - Message: `feat(backend): add FastAPI with WebSocket endpoint`
  - Files: `backend/main.py`

---

- [ ] 3. Integracja logiki z llm/main.py

  **What to do**:
  - Zaimportować funkcje z `llm/main.py`: `hotel_tools`, obsługę Groq
  - Utworzyć async wrapper dla synchronicznych funkcji
  - Przenieść `messages` list do sesji
  - Obsłużyć tool calling (check_availability, make_reservation)
  - Zwracać odpowiedź tekstową przez WebSocket

  **Must NOT do**:
  - Nie modyfikować oryginalnego `llm/main.py`
  - Nie zmieniać promptu systemowego
  - Nie dodawać nowych narzędzi LLM

  **Parallelizable**: NO (zależy od 2)

  **References**:
  
  **Pattern References**:
  - `llm/main.py:45-150` - logika Groq client i tool calling
  - `llm/main.py:hotel_tools` - definicja narzędzi
  - `llm/main.py:check_availability()` - sprawdzanie dostępności
  - `llm/main.py:make_reservation()` - tworzenie rezerwacji
  
  **API/Type References**:
  - `llm/hotel_aurora.db` - schemat bazy (tabela reservations)

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] WebSocket client wysyła: `{"type": "text", "content": "Czy macie wolne pokoje?"}`
  - [ ] Serwer odpowiada JSON z tekstem odpowiedzi LLM
  - [ ] Odpowiedź zawiera informacje o pokojach z bazy

  **Commit**: YES
  - Message: `feat(backend): integrate LLM logic from llm/main.py`
  - Files: `backend/main.py`, `backend/llm_service.py`

---

- [ ] 4. Obsługa audio - transcoding WebM → LINEAR16

  **What to do**:
  - Dodać endpoint do przyjmowania audio (WebM/Opus z przeglądarki)
  - Użyć ffmpeg do konwersji na LINEAR16 16kHz mono
  - Wysłać do Google Speech-to-Text
  - Zwrócić transkrypcję przez WebSocket

  **Must NOT do**:
  - Nie zmieniać konfiguracji Google Speech
  - Nie dodawać innych języków (tylko pl-PL)

  **Parallelizable**: NO (zależy od 3)

  **References**:
  
  **Pattern References**:
  - `llm/main.py:transcribe_audio()` - istniejąca logika STT
  - `llm/main.py` - konfiguracja Google Speech (pl-PL, LINEAR16)
  
  **External References**:
  - ffmpeg-python docs: https://github.com/kkroening/ffmpeg-python
  - Google Speech streaming: https://cloud.google.com/speech-to-text/docs/streaming-recognize
  
  **Documentation References**:
  - `AGENTS.md:Setup` - wymaga `gcp_key.json`

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Nagrać audio w przeglądarce (WebM)
  - [ ] Wysłać przez WebSocket jako binary
  - [ ] Otrzymać JSON: `{"type": "transcription", "text": "treść..."}`
  - [ ] Tekst poprawnie rozpoznany po polsku

  **Commit**: YES
  - Message: `feat(backend): add audio transcoding and STT integration`
  - Files: `backend/audio_service.py`, `backend/main.py`

---

- [ ] 5. Integracja modułu sentymentu

  **What to do**:
  - Zaimportować model z `Emocje/main.py`
  - Analizować sentyment transkrypcji użytkownika
  - Dołączyć informację o sentymencie do kontekstu LLM
  - Opcjonalnie: dostosować ton odpowiedzi

  **Must NOT do**:
  - Nie modyfikować oryginalnego `Emocje/main.py`
  - Nie zmieniać modelu sentymentu

  **Parallelizable**: NO (zależy od 4)

  **References**:
  
  **Pattern References**:
  - `Emocje/main.py` - model VoiceLab/herbert-base-cased-sentiment
  - `Emocje/main.py:analyze_sentiment()` - funkcja analizy
  
  **External References**:
  - Model HuggingFace: https://huggingface.co/VoiceLab/herbert-base-cased-sentiment

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Wysłać wiadomość negatywną: "Jestem bardzo niezadowolony z obsługi"
  - [ ] Log serwera pokazuje: `sentiment: negative`
  - [ ] Odpowiedź LLM uwzględnia ton empatyczny

  **Commit**: YES
  - Message: `feat(backend): integrate sentiment analysis module`
  - Files: `backend/sentiment_service.py`, `backend/main.py`

---

- [ ] 6. Trwałe sesje rozmów w SQLite

  **What to do**:
  - Utworzyć tabelę `conversations` w SQLite
  - Zapisywać każdą wiadomość (user + assistant) z timestamp
  - Przy połączeniu WebSocket - ładować historię sesji
  - Generować session_id dla każdej nowej konwersacji

  **Must NOT do**:
  - Nie modyfikować tabeli `reservations` w hotel_aurora.db
  - Nie czyścić historii automatycznie

  **Parallelizable**: NO (zależy od 3)

  **References**:
  
  **Pattern References**:
  - `llm/main.py` - użycie sqlite3
  - `llm/hotel_aurora.db` - istniejąca baza (dodać nową tabelę)
  
  **API/Type References**:
  - Schemat: `conversations(id, session_id, role, content, timestamp, sentiment)`

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Przeprowadzić rozmowę (3 wiadomości)
  - [ ] `sqlite3 llm/hotel_aurora.db "SELECT * FROM conversations"` → pokazuje 6 wpisów
  - [ ] Restart serwera, nowe połączenie z tym samym session_id → historia załadowana

  **Commit**: YES
  - Message: `feat(backend): add persistent conversation sessions`
  - Files: `backend/session_service.py`, `backend/main.py`

---

### Faza 2: Frontend Core

- [ ] 7. Inicjalizacja projektu React

  **What to do**:
  - `npm create vite@latest frontend -- --template react-ts`
  - Zainstalować zależności: tsparticles, @mesh-gradient/react
  - Skonfigurować Tailwind CSS (dark mode)
  - Utworzyć podstawowy layout App.tsx

  **Must NOT do**:
  - Nie dodawać React Router (single page)
  - Nie dodawać state management library (useState wystarczy)

  **Parallelizable**: YES (z task 8 po inicjalizacji)

  **References**:
  
  **External References**:
  - Vite React template: https://vitejs.dev/guide/
  - Tailwind CSS: https://tailwindcss.com/docs/guides/vite
  - tsParticles React: https://particles.js.org/docs/react/

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] `cd frontend && npm run dev` → app działa na localhost:5173
  - [ ] Przeglądarka pokazuje ciemne tło (dark mode)
  - [ ] DevTools → Network → brak błędów 404

  **Commit**: YES
  - Message: `feat(frontend): initialize React with Vite, Tailwind, tsParticles`
  - Files: `frontend/`

---

- [ ] 8. Animowane tło z mesh gradient

  **What to do**:
  - Zaimplementować animowany mesh gradient jako tło
  - Użyć @mesh-gradient/react lub CSS animation
  - Kolory: ciemne purple/blue/indigo (dark mode aesthetic)
  - Płynna animacja (60fps, GPU accelerated)

  **Must NOT do**:
  - Nie używać statycznego obrazka
  - Nie blokować UI podczas animacji

  **Parallelizable**: YES (z task 7 po inicjalizacji)

  **References**:
  
  **External References**:
  - @mesh-gradient/react: https://www.npmjs.com/package/@mesh-gradient/react
  - CSS mesh gradients: https://csshero.org/mesher/
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("mesh gradient animation", language=["TypeScript", "TSX"])`

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Przeglądarka: tło płynnie animuje kolory
  - [ ] DevTools → Performance → brak frame drops
  - [ ] Kolory: odcienie purple/blue/indigo

  **Commit**: YES
  - Message: `feat(frontend): add animated mesh gradient background`
  - Files: `frontend/src/components/Background.tsx`

---

- [ ] 9. Komponent Chat UI

  **What to do**:
  - Utworzyć komponent ChatHistory z listą wiadomości
  - Style bąbelków: user (prawo, niebieski), assistant (lewo, szary)
  - Auto-scroll do najnowszej wiadomości
  - Timestamp przy każdej wiadomości
  - Animacja pojawiania się nowych wiadomości

  **Must NOT do**:
  - Nie dodawać avatarów
  - Nie dodawać reakcji/emojis
  - Nie dodawać edycji wiadomości

  **Parallelizable**: NO (zależy od 7)

  **References**:
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("chat bubble component react", language=["TSX"])`
  
  **External References**:
  - Tailwind chat examples: https://tailwindui.com/components/application-ui/messaging

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Dodać mock wiadomości w komponencie
  - [ ] Bąbelki user → prawo, niebieskie
  - [ ] Bąbelki assistant → lewo, szare
  - [ ] Scroll automatyczny do dołu
  - [ ] Animacja fade-in na nowych wiadomościach

  **Commit**: YES
  - Message: `feat(frontend): add chat UI component with message bubbles`
  - Files: `frontend/src/components/ChatHistory.tsx`, `frontend/src/components/MessageBubble.tsx`

---

- [ ] 10. WebSocket client

  **What to do**:
  - Utworzyć hook `useWebSocket` do połączenia z backendem
  - Obsłużyć typy wiadomości: transcription, response, audio, error
  - Auto-reconnect przy zerwaniu połączenia
  - Przekazywać session_id dla trwałości sesji

  **Must NOT do**:
  - Nie używać Socket.IO (czysty WebSocket)
  - Nie cachować wiadomości lokalnie (backend jest źródłem prawdy)

  **Parallelizable**: NO (wymaga działającego backendu z task 2 i frontendu z task 7)

  **References**:
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("useWebSocket hook react", language=["TypeScript"])`
  
  **External References**:
  - React WebSocket patterns: https://ably.com/blog/websockets-react-tutorial

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Frontend łączy się z `ws://localhost:8000/ws`
  - [ ] DevTools → Network → WebSocket → status "101 Switching Protocols"
  - [ ] Wysłanie testowej wiadomości → odpowiedź w konsoli
  - [ ] Zamknięcie serwera → auto-reconnect po 3s

  **Commit**: YES
  - Message: `feat(frontend): add WebSocket client with auto-reconnect`
  - Files: `frontend/src/hooks/useWebSocket.ts`

---

- [ ] 11. Nagrywanie audio z mikrofonu

  **What to do**:
  - Użyć MediaRecorder API do nagrywania WebM/Opus
  - Utworzyć hook `useAudioRecorder`
  - Wysyłać audio chunks przez WebSocket
  - Obsłużyć permission denied dla mikrofonu

  **Must NOT do**:
  - Nie używać getUserMedia z video
  - Nie zapisywać audio lokalnie

  **Parallelizable**: NO (wymaga WebSocket z task 10)

  **References**:
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("MediaRecorder WebSocket audio", language=["TypeScript"])`
  
  **External References**:
  - MDN MediaRecorder: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Kliknięcie "Record" → przeglądarka pyta o mikrofon
  - [ ] Nagranie 3s audio → wysłane do backendu
  - [ ] Backend loguje: "Received audio chunk: X bytes"
  - [ ] Permission denied → UI pokazuje komunikat błędu

  **Commit**: YES
  - Message: `feat(frontend): add audio recording with MediaRecorder`
  - Files: `frontend/src/hooks/useAudioRecorder.ts`

---

- [ ] 12. Odtwarzanie audio TTS

  **What to do**:
  - Odbierać MP3 z backendu (jako blob/base64)
  - Odtwarzać za pomocą Audio API lub `<audio>` element
  - Pokazać wizualny wskaźnik "asystent mówi"
  - Queue audio jeśli kilka odpowiedzi naraz

  **Must NOT do**:
  - Nie implementować streaming audio (pełny plik)
  - Nie dodawać kontrolek głośności

  **Parallelizable**: NO (wymaga WebSocket z task 10)

  **References**:
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("Audio playback blob react", language=["TypeScript"])`
  
  **External References**:
  - Web Audio API playback: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Backend wysyła odpowiedź z audio
  - [ ] Audio automatycznie się odtwarza
  - [ ] UI pokazuje "Asystent mówi..." podczas playback
  - [ ] Kolejka działa: 2 szybkie odpowiedzi → odtwarzane po kolei

  **Commit**: YES
  - Message: `feat(frontend): add TTS audio playback`
  - Files: `frontend/src/hooks/useAudioPlayback.ts`

---

### Faza 3: Wizualizacja Audio

- [ ] 13. Podstawowa konfiguracja tsParticles

  **What to do**:
  - Skonfigurować tsParticles z preset "particles"
  - Ciemne kolory cząsteczek (cyan/purple/blue)
  - Subtelny ruch w tle (gdy brak audio)
  - Połączyć particles z mesh gradient (overlay)

  **Must NOT do**:
  - Nie używać zbyt wielu cząsteczek (max 100)
  - Nie blokować interakcji z UI

  **Parallelizable**: NO (wymaga frontendu z task 7)

  **References**:
  
  **External References**:
  - tsParticles preset: https://particles.js.org/samples/presets/
  - tsParticles React: https://www.npmjs.com/package/@tsparticles/react
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("tsParticles audio reactive", language=["TypeScript"])`

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Cząsteczki widoczne na tle gradient
  - [ ] Subtelny ruch bez audio input
  - [ ] Wydajność: 60fps (DevTools Performance)
  - [ ] Cząsteczki nie blokują kliknięć w chat

  **Commit**: YES
  - Message: `feat(frontend): add tsParticles base configuration`
  - Files: `frontend/src/components/ParticlesBackground.tsx`

---

- [ ] 14. Wizualizacja głosu użytkownika (particles)

  **What to do**:
  - Użyć Web Audio API AnalyserNode na mikrofonie
  - Mapować frequency data na rozmiar/prędkość cząsteczek
  - Intensywniejsze kolory przy głośniejszym mówieiu
  - Aktywować tylko podczas nagrywania

  **Must NOT do**:
  - Nie analizować audio gdy mikrofon wyłączony (privacy)

  **Parallelizable**: YES (z task 15)

  **References**:
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("AnalyserNode getFrequencyData", language=["TypeScript"])`
  
  **External References**:
  - Web Audio API Analyser: https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Rozpoczęcie nagrywania → cząsteczki reagują na głos
  - [ ] Głośniejsze mówienie → większe/szybsze cząsteczki
  - [ ] Stop nagrywania → cząsteczki wracają do stanu bazowego
  - [ ] Cisza → minimalna aktywność cząsteczek

  **Commit**: YES
  - Message: `feat(frontend): add audio-reactive particles for user voice`
  - Files: `frontend/src/hooks/useAudioAnalyser.ts`, `frontend/src/components/ParticlesBackground.tsx`

---

- [ ] 15. Wizualizacja głosu asystenta (particles)

  **What to do**:
  - Podłączyć AnalyserNode do audio TTS playback
  - Inny styl wizualizacji niż user (np. inny kolor, wzór)
  - Synchronizacja z playback state

  **Must NOT do**:
  - Nie używać tego samego stylu co user voice

  **Parallelizable**: YES (z task 14)

  **References**:
  
  **Pattern References**:
  - Reuse `useAudioAnalyser.ts` z task 14
  - Modyfikacja ParticlesBackground dla dual-source
  
  **External References**:
  - Audio element as source: https://developer.mozilla.org/en-US/docs/Web/API/MediaElementAudioSourceNode

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Audio TTS playing → cząsteczki reagują (inny styl niż user)
  - [ ] Różne kolory: user = cyan, assistant = purple
  - [ ] Oba źródła mogą działać jednocześnie (np. user przerywa)

  **Commit**: YES
  - Message: `feat(frontend): add audio-reactive particles for TTS voice`
  - Files: `frontend/src/hooks/useAudioAnalyser.ts`, `frontend/src/components/ParticlesBackground.tsx`

---

- [ ] 16. UI push-to-talk i ciągłe słuchanie

  **What to do**:
  - Przycisk push-to-talk (przytrzymaj = nagrywa)
  - Toggle "ciągłe słuchanie" (VAD on/off)
  - Visual feedback: pulsowanie gdy nasłuchuje
  - Keyboard shortcut: Space = push-to-talk

  **Must NOT do**:
  - Nie implementować server-side VAD
  - Nie automatycznie włączać ciągłego słuchania

  **Parallelizable**: NO (wymaga audio recording z task 11)

  **References**:
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("push to talk button react", language=["TSX"])`
  
  **External References**:
  - Client-side VAD: https://github.com/ricky0123/vad (opcjonalnie)

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Przytrzymanie przycisku → nagrywanie, puszczenie → wysyłanie
  - [ ] Spacebar → to samo co przycisk
  - [ ] Toggle "Ciągłe słuchanie" ON → automatyczne wykrywanie mowy
  - [ ] Wizualne pulsowanie gdy nasłuchuje

  **Commit**: YES
  - Message: `feat(frontend): add push-to-talk and continuous listening UI`
  - Files: `frontend/src/components/VoiceControls.tsx`

---

### Faza 4: Polish & QA

- [ ] 17. Error handling i fallback do tekstu

  **What to do**:
  - Obsłużyć błędy: WebSocket disconnect, STT fail, TTS fail
  - Fallback: jeśli TTS nie działa → tylko tekst
  - Toast notifications dla błędów
  - Retry logic dla transient failures

  **Must NOT do**:
  - Nie crash'ować przy błędach
  - Nie ukrywać błędów całkowicie (user musi wiedzieć)

  **Parallelizable**: NO (wymaga wszystkich poprzednich)

  **References**:
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("toast notification react", language=["TSX"])`

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Wyłączenie backendu → toast "Połączenie utracone" → auto-reconnect
  - [ ] Błąd TTS (zły API key) → odpowiedź tekstowa bez audio
  - [ ] Błąd STT → toast "Nie rozpoznano mowy" → możliwość retry

  **Commit**: YES
  - Message: `feat(frontend): add error handling and text fallback`
  - Files: `frontend/src/components/Toast.tsx`, `frontend/src/hooks/useWebSocket.ts`

---

- [ ] 18. Loading states i UX polish

  **What to do**:
  - Wskaźnik "przetwarzanie" gdy LLM generuje
  - Typing indicator w chacie (3 pulsujące kropki)
  - Smooth transitions między stanami
  - Disabled states dla przycisków

  **Must NOT do**:
  - Nie blokować UI podczas ładowania
  - Nie ukrywać całego contentu

  **Parallelizable**: NO (wymaga wszystkich komponentów)

  **References**:
  
  **Pattern References**:
  - Znajdź przykłady: `grep_app_searchGitHub("typing indicator css", language=["CSS"])`

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Wysłanie wiadomości → typing indicator w chacie
  - [ ] Podczas nagrywania → przycisk pulsuje, inne disabled
  - [ ] Transitions smooth (opacity, transform)

  **Commit**: YES
  - Message: `feat(frontend): add loading states and UX polish`
  - Files: `frontend/src/components/TypingIndicator.tsx`, various components

---

- [ ] 19. Final Manual QA

  **What to do**:
  - Pełny test flow: nagranie → transkrypcja → odpowiedź → audio
  - Test edge cases: długa cisza, przerwanie, disconnect
  - Sprawdzenie wydajności (no lag, 60fps)
  - Sprawdzenie wszystkich stanów UI

  **Must NOT do**:
  - Nie skipować żadnego scenariusza

  **Parallelizable**: NO (finalne testy)

  **References**:
  
  **Documentation References**:
  - Ten plan - wszystkie acceptance criteria

  **Acceptance Criteria**:
  
  **Manual Execution Verification (FULL CHECKLIST):**
  
  **Happy Path:**
  - [ ] Uruchomienie: `uvicorn backend.main:app --reload` + `npm run dev`
  - [ ] Połączenie WebSocket nawiązane
  - [ ] Push-to-talk: nagranie "Czy macie wolne pokoje?"
  - [ ] Transkrypcja pojawia się w chacie (bąbelek user)
  - [ ] Particles reagują na głos user (cyan)
  - [ ] Loading indicator podczas przetwarzania LLM
  - [ ] Odpowiedź asystenta pojawia się (bąbelek assistant)
  - [ ] Audio TTS automatycznie się odtwarza
  - [ ] Particles reagują na TTS (purple)
  - [ ] Historia zapisana w bazie
  
  **Edge Cases:**
  - [ ] Ciągłe słuchanie: toggle ON, mów, auto-detection działa
  - [ ] Disconnect: wyłącz backend, toast error, auto-reconnect
  - [ ] TTS fail: symuluj błąd, fallback do tekstu
  - [ ] Długa cisza: nie crash'uje, timeout graceful
  - [ ] Refresh strony: nowa sesja, czysta historia
  - [ ] Session persistence: ta sama session_id → historia załadowana
  
  **Performance:**
  - [ ] DevTools Performance: 60fps, no jank
  - [ ] Memory: brak memory leaks (monitor przez 5 min)
  - [ ] Latency: user stop → TTS start < 5s

  **Commit**: NO (QA only)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat(structure): add backend and frontend directories` | backend/, frontend/ | ls |
| 2 | `feat(backend): add FastAPI with WebSocket endpoint` | backend/main.py | curl /health |
| 3 | `feat(backend): integrate LLM logic from llm/main.py` | backend/*.py | WebSocket test |
| 4 | `feat(backend): add audio transcoding and STT integration` | backend/audio_service.py | Audio test |
| 5 | `feat(backend): integrate sentiment analysis module` | backend/sentiment_service.py | Log check |
| 6 | `feat(backend): add persistent conversation sessions` | backend/session_service.py | SQLite query |
| 7 | `feat(frontend): initialize React with Vite, Tailwind, tsParticles` | frontend/ | npm run dev |
| 8 | `feat(frontend): add animated mesh gradient background` | frontend/src/components/ | Visual |
| 9 | `feat(frontend): add chat UI component with message bubbles` | frontend/src/components/ | Visual |
| 10 | `feat(frontend): add WebSocket client with auto-reconnect` | frontend/src/hooks/ | Network tab |
| 11 | `feat(frontend): add audio recording with MediaRecorder` | frontend/src/hooks/ | Audio test |
| 12 | `feat(frontend): add TTS audio playback` | frontend/src/hooks/ | Audio test |
| 13 | `feat(frontend): add tsParticles base configuration` | frontend/src/components/ | Visual |
| 14 | `feat(frontend): add audio-reactive particles for user voice` | frontend/src/ | Audio + visual |
| 15 | `feat(frontend): add audio-reactive particles for TTS voice` | frontend/src/ | Audio + visual |
| 16 | `feat(frontend): add push-to-talk and continuous listening UI` | frontend/src/components/ | Interaction |
| 17 | `feat(frontend): add error handling and text fallback` | frontend/src/ | Error simulation |
| 18 | `feat(frontend): add loading states and UX polish` | frontend/src/ | Visual |

---

## Success Criteria

### Verification Commands
```bash
# Backend
cd backend && uvicorn main:app --reload  # → Running on http://localhost:8000
curl http://localhost:8000/health  # → {"status": "ok"}

# Frontend
cd frontend && npm run dev  # → Running on http://localhost:5173

# Database
sqlite3 llm/hotel_aurora.db "SELECT COUNT(*) FROM conversations"  # → liczba wiadomości
```

### Final Checklist
- [ ] **Must Have** - wszystkie 10 pozycji zaimplementowane
- [ ] **Must NOT Have** - żaden z 11 wykluczonych elementów nie został dodany
- [ ] **Happy Path** - pełna rozmowa głosowa działa end-to-end
- [ ] **Edge Cases** - disconnect, TTS fail, empty audio obsłużone gracefully
- [ ] **Performance** - 60fps, latency < 5s
- [ ] **Persistence** - historia sesji przetrwa restart serwera
