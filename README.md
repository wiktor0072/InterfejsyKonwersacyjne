# Hotel Aurora - Głosowy Asystent Rezerwacji

Aplikacja webowa umożliwiająca rezerwację pokoi hotelowych za pomocą głosu. Wykorzystuje Speech-to-Text (Google Cloud), LLM (Groq/Llama 3.3), analiza sentymentu (transformers) oraz Text-to-Speech (ElevenLabs).

## Wymagania wstępne

### System
- **Python 3.11+**
- **Node.js 18+** i **npm**
- **ffmpeg** (do transkodowania audio)
- **uv** (menadżer pakietów Python) - [instalacja](https://docs.astral.sh/uv/getting-started/installation/)

### Klucze API

| Usługa | Zmienna środowiskowa | Gdzie uzyskać |
|--------|---------------------|---------------|
| **Groq** (LLM) | `GROQ_API_KEY` | https://console.groq.com/keys |
| **Google Cloud Speech** | plik `gcp_key.json` | https://console.cloud.google.com/apis/credentials |
| **ElevenLabs** (TTS) | `ELEVENLABS_API_KEY` | https://elevenlabs.io/app/settings/api-keys |

## Instalacja

### 1. Klonowanie repozytorium
```bash
git clone <repo-url>
cd InterfejsyKonwersacyjne
```

### 2. Backend (Python)
```bash
cd backend
uv venv
source .venv/bin/activate  # Linux/macOS
# lub: .venv\Scripts\activate  # Windows

uv pip install -r requirements.txt
```

### 3. Frontend (Node.js)
```bash
cd frontend
npm install
```

### 4. Konfiguracja kluczy API

#### Opcja A: Plik `.env` (zalecane)
Utwórz plik `.env` w katalogu `backend/`:
```bash
# backend/.env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxx
```

#### Opcja B: Eksport zmiennych
```bash
export GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxx"
export ELEVENLABS_API_KEY="sk_xxxxxxxxxxxxxxxxxxxxxxxx"
```

### 5. Google Cloud Speech credentials
Umieść plik `gcp_key.json` w głównym katalogu projektu:
```
InterfejsyKonwersacyjne/
├── gcp_key.json          <-- tutaj
├── backend/
├── frontend/
└── ...
```

## Uruchomienie

### Terminal 1: Backend
```bash
cd backend
source .venv/bin/activate
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

### Otwórz aplikację
Przejdź do: **http://localhost:5173**

## Weryfikacja działania

### Sprawdź backend
```bash
curl http://localhost:8000/health
# Oczekiwana odpowiedź: {"status":"ok"}
```

### Logi backendu przy poprawnym uruchomieniu
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     127.0.0.1:xxxxx - "WebSocket /ws?session_id=..." [accepted]
INFO:     connection open
[LLM] Groq client initialized
```

### Typowe błędy

| Błąd | Rozwiązanie |
|------|-------------|
| `GROQ_API_KEY environment variable` | Ustaw `GROQ_API_KEY` lub dodaj do `.env` |
| `GCP key file not found` | Umieść `gcp_key.json` w głównym katalogu |
| `ELEVENLABS_API_KEY` | Ustaw klucz lub wyłącz TTS |
| `ffmpeg not found` | Zainstaluj ffmpeg: `sudo apt install ffmpeg` |

## Struktura projektu

```
InterfejsyKonwersacyjne/
├── backend/                 # FastAPI + WebSocket server
│   ├── main.py             # Główny serwer
│   ├── llm_service.py      # Integracja z Groq LLM
│   ├── audio_service.py    # Google Speech-to-Text
│   └── requirements.txt
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── App.tsx        # Główny komponent
│   │   ├── components/    # UI components
│   │   └── hooks/         # Custom hooks
│   └── package.json
├── llm/                    # Core LLM logic
│   └── main.py            # Hotel tools, prompts, database
├── tts/                    # ElevenLabs TTS
│   └── elevenlabs_tts.py
└── gcp_key.json           # Google Cloud credentials
```

## Funkcjonalności

- **Rozpoznawanie mowy** (Google Cloud Speech) - polski
- **Analiza sentymentu** - dostosowanie odpowiedzi do nastroju
- **LLM** (Groq/Llama 3.3 70B) - inteligentny asystent z narzędziami
- **Baza danych** (SQLite) - zarządzanie pokojami i rezerwacjami  
- **Synteza mowy** (ElevenLabs) - naturalne odpowiedzi głosowe
- **WebSocket** - komunikacja w czasie rzeczywistym

## Rozwój

### Rebuild frontend
```bash
cd frontend && npm run build
```

### Testy TTS
```bash
export ELEVENLABS_API_KEY='...'
python tts/test_elevenlabs.py
```

### Bezpośredni test LLM
```bash
python llm/main.py
```
