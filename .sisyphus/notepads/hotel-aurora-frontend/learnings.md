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
