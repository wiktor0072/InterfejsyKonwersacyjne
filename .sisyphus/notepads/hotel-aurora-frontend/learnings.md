## 2026-01-19 Task 1: Project Structure

### Created
- `backend/` directory for FastAPI
- `frontend/` directory for React  
- `backend/__init__.py` (empty)
- `backend/requirements.txt` with all dependencies

### Dependencies in requirements.txt
- fastapi, uvicorn, websockets, python-multipart
- ffmpeg-python (for audio transcoding)
- google-cloud-speech, groq, elevenlabs (voice pipeline)
- torch, transformers (sentiment analysis)

### Notes
- Do NOT modify files in `llm/` directory - that's the original CLI
- Backend will wrap existing logic from `llm/main.py`

## 2026-01-19 Task 2: FastAPI + WebSocket

### Created
- `backend/main.py` with FastAPI app

### Key Details
- Use `uv run uvicorn main:app --reload` to start server (NOT plain uvicorn)
- Health endpoint: GET `/health` → `{"status": "ok"}`
- WebSocket endpoint: `/ws` - accepts JSON, echoes back (placeholder)
- CORS configured for `http://localhost:5173` (React dev server)

### Commands
```bash
cd backend && uv run uvicorn main:app --reload  # Start server
curl http://localhost:8000/health               # Test health
```

## 2026-01-19 Task 3: LLM Integration

### Created
- `backend/llm_service.py` - wraps Groq client with tool calling

### Key Details
- Import from `llm_service` (not `backend.llm_service`) when running from backend/
- Requires GROQ_API_KEY environment variable
- Uses `llama-3.3-70b-versatile` model
- Agentic loop handles tool calls (check_availability, make_reservation)

## 2026-01-19 Task 4: Audio Service

### Created
- `backend/audio_service.py` - WebM→LINEAR16 transcoding + Google STT

### Key Details
- Requires ffmpeg installed on system
- Requires gcp_key.json in project root
- Uses 16kHz mono for Google Speech API

## 2026-01-19 Task 5: Sentiment Service

### Created
- `backend/sentiment_service.py` - VoiceLab herbert-base-cased-sentiment

### Key Details
- Labels: negative (0), neutral (1), positive (2)
- Returns (label, confidence) tuple
- Model loads on first use (may be slow)

## 2026-01-19 Task 6: Session Service  

### Created
- `backend/session_service.py` - SQLite conversation persistence

### Key Details
- Uses same DB as hotel: `llm/hotel_aurora.db`
- Table: conversations(id, session_id, role, content, timestamp, sentiment)
- Session ID generated with uuid4()
