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
