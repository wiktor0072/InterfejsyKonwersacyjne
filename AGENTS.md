# AGENTS.md - Context & Guidelines for AI Agents

## 1. Project Overview
**InterfejsyKonwersacyjne** is a voice-based hotel reservation assistant ("Hotel Aurora").
It integrates Speech-to-Text (STT), Sentiment Analysis, Large Language Models (LLM), and Text-to-Speech (TTS) into a conversational pipeline.

### Current Tech Stack
- **Language**: Python 3.x
- **Core Logic**: `llm/main.py` (Orchestrator, State, Tools)
- **STT**: Google Cloud Speech (`google-cloud-speech`), Vosk (Legacy)
- **LLM**: Groq (Llama 3.3) - *Note: Plan mentions Gemini, currently implementation uses Groq.*
- **Sentiment**: VoiceLab/herbert-base-cased-sentiment (`transformers`, `torch`)
- **Audio I/O**: `pyaudio`
- **Database**: `sqlite3` (Hotel inventory)

## 2. Environment & Commands

### Setup
No `requirements.txt` currently exists. Common dependencies observed:
```bash
pip install torch transformers groq google-cloud-speech pyaudio numpy
```

### Running Modules
- **Main Receptionist (Core App)**:
  ```bash
  python llm/main.py
  ```
- **Sentiment Analysis Test**:
  ```bash
  python Emocje/main.py
  ```
- **Voice Recognition Test**:
  ```bash
  python speech3.py
  ```

### Testing
- Currently manual testing via running scripts.
- Future: Use `pytest`.
- **Verify Audio**: Check input microphone and speakers before running voice scripts.

## 3. Code Style Guidelines

### Python
- **Formatting**: PEP 8 (4 spaces indent).
- **Type Hints**: Strongly encouraged for function signatures (e.g., `def func(x: int) -> str:`).
- **Language**:
  - **Code/Variable Names**: English (e.g., `check_availability`, `messages`).
  - **Comments/Logs/UI**: **Polish** (e.g., `print("⏳ Ładowanie modelu...")`).
- **Imports**:
  - Standard library first (`sys`, `json`).
  - Third-party second (`torch`, `groq`).
  - Local imports last.
  - Absolute imports preferred over relative.

### Error Handling
- Use specific `try/except` blocks (e.g., `except KeyboardInterrupt`, `except ImportError`).
- Graceful degradation: If a service (e.g., STT) is missing, disable that feature but keep the app running if possible (or exit cleanly with a helpful message).

### File Structure
- `llm/`: Core logic, database, orchestrator.
- `Emocje/`: Sentiment analysis experiments.
- `Mowa/`: TTS/STT experiments.
- `PierwszeEtapy/`: Legacy/Prototype code.

## 4. Project Roadmap (Sprints)

### SPRINT 1 – Konfiguracja i testy modeli
**Cel**: upewnić się, że każdy komponent działa osobno.
- [x] **Konfiguracja Google Speech-to-Text**
    - Klucze API
    - Testy: plik audio → tekst
    - Sprawdzenie języka PL
- [x] **Konfiguracja modelu sentymentu**
    - `bardsai/twitter-sentiment-pl-base` (lub `VoiceLab/herbert` obecny w kodzie)
    - Testy: tekst → sentyment
- [ ] **Konfiguracja Gemini (LLM)**
    - *Status: Obecnie zaimplementowano Groq/Llama-3*
    - Testy: tekst → odpowiedź
- [ ] **Konfiguracja ElevenLabs (TTS)**
    - Wybór głosu, test opóźnień
- [ ] **Repo + struktura**
    - `stt/`, `sentiment/`, `llm/`, `tts/`

### SPRINT 2 – Minimalny backend i pipeline (MVP)
**Cel**: spiąć wszystko w jeden przepływ.
- [ ] **Prosty backend** (FastAPI / Express - *Obecnie skrypt Python `llm/main.py` pełni tę rolę*)
- [ ] **Pipeline**: Audio → STT → Sentiment → LLM → TTS → Audio
- [ ] **Przekazywanie sentymentu do promptu**
- [ ] **Jeden scenariusz**: "pytanie o dostępność pokoju"
- [ ] **Logowanie**: tekst, sentyment, odpowiedź

### SPRINT 3 – Logika rezerwacyjna + pamięć rozmowy
**Cel**: asystent „rozumie”, że chodzi o rezerwację hotelu.
- [x] **Intent detection**: Reguły/Prompt (`hotel_tools` w `llm/main.py`)
- [x] **Kontekst rozmowy**: Pamięć sesji (w `messages` list)
- [x] **Mock bazy danych**: SQLite (`hotel_aurora.db`)
- [x] **Lepszy prompt**: Styl sprzedażowy, obsługa narzędzi
- [ ] **Response templates**

### SPRINT 4 – Frontend (na sam koniec)
**Cel**: użytkownik może realnie z tego skorzystać.
- [ ] **Frontend web** (React / Vue)
- [ ] **Przycisk „nagraj”**
- [ ] **Odtwarzanie audio**
- [ ] **Integracja z backendem**

## 5. Agent Instructions
- **Read First**: Always read `llm/main.py` before making architectural changes.
- **Tools**: Use `sqlite3` for database interactions.
- **Logs**: Keep logs in Polish to match existing style.
- **Refactoring**: When refactoring, preserve the existing `hotel_aurora.db` schema unless necessary to change.
