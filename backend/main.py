from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
import logging
import os
from pathlib import Path

env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hotel Aurora API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_service = None
sessions: dict[str, list[dict[str, Any]]] = {}


def get_llm_service():
    global llm_service
    if llm_service is None:
        from llm_service import LLMService

        llm_service = LLMService()
    return llm_service


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = websocket.query_params.get("session_id", "default")

    try:
        service = get_llm_service()
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})
        await websocket.close()
        return

    if session_id not in sessions:
        sessions[session_id] = service.create_initial_messages()
        logger.info(f"New session created: {session_id}")

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "text")
            content = data.get("content", "")

            if msg_type == "text" and content:
                logger.info(f"[{session_id}] User: {content[:50]}...")

                response_text, sessions[session_id] = await service.process_message(
                    content, sessions[session_id]
                )

                logger.info(f"[{session_id}] Assistant: {response_text[:50]}...")

                await websocket.send_json(
                    {"type": "response", "content": response_text}
                )
            else:
                await websocket.send_json(
                    {"type": "error", "content": "Invalid message format"}
                )

    except WebSocketDisconnect:
        logger.info(f"Session {session_id} disconnected")
