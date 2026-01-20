from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from typing import Any
import logging
import os
import json
from pathlib import Path

env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("conversation.log", encoding="utf-8"),
    ],
)
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
audio_service = None
tts_service = None
sessions: dict[str, list[dict[str, Any]]] = {}


def get_llm_service():
    global llm_service
    if llm_service is None:
        from llm_service import LLMService

        llm_service = LLMService()
    return llm_service


def get_audio_service():
    global audio_service
    if audio_service is None:
        from audio_service import AudioService

        audio_service = AudioService()
    return audio_service


def get_tts_service():
    global tts_service
    if tts_service is None:
        from tts_service import TTSService

        tts_service = TTSService()
    return tts_service


def get_sentiment_service():
    from sentiment_service import analyze_sentiment

    return analyze_sentiment


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
        await websocket.send_json({"type": "error", "message": str(e)})
        await websocket.close()
        return

    try:
        stt_service = get_audio_service()
        logger.info("STT service initialized")
    except Exception as e:
        logger.warning(f"STT service unavailable: {e}")
        stt_service = None

    try:
        tts = get_tts_service()
        logger.info("TTS service initialized")
    except Exception as e:
        logger.warning(f"TTS service unavailable: {e}")
        tts = None

    analyze_sentiment = get_sentiment_service()

    if session_id not in sessions:
        sessions[session_id] = service.create_initial_messages()
        logger.info(f"New session created: {session_id}")

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            if "bytes" in message and message["bytes"]:
                audio_data = message["bytes"]
                logger.info(f"[{session_id}] Received audio: {len(audio_data)} bytes")

                if not stt_service:
                    await websocket.send_json(
                        {"type": "error", "message": "STT service unavailable"}
                    )
                    continue

                try:
                    transcript = stt_service.transcribe(audio_data, is_webm=True)
                    if not transcript:
                        await websocket.send_json(
                            {"type": "error", "message": "Nie rozpoznano mowy"}
                        )
                        continue

                    logger.info(f"[{session_id}] Transcription: {transcript}")
                    await websocket.send_json(
                        {"type": "transcription", "text": transcript}
                    )

                    sentiment_label = None
                    sentiment_score = 0.0
                    if analyze_sentiment:
                        try:
                            result = analyze_sentiment(transcript)
                            if result:
                                sentiment_label, sentiment_score = result
                                logger.info(
                                    f"[{session_id}] Sentiment: {sentiment_label} ({sentiment_score:.2f})"
                                )
                        except Exception as e:
                            logger.error(
                                f"[{session_id}] Sentiment analysis error: {e}"
                            )

                    response_text, sessions[session_id] = await service.process_message(
                        transcript,
                        sessions[session_id],
                        sentiment=sentiment_label,
                        score=sentiment_score,
                    )
                    logger.info(f"[{session_id}] Assistant: {response_text[:50]}...")

                    await websocket.send_json(
                        {"type": "response", "text": response_text}
                    )

                    if tts and response_text:
                        try:
                            logger.info(f"[{session_id}] Generating TTS audio...")
                            audio_base64 = tts.generate_audio_base64(response_text)
                            await websocket.send_json(
                                {"type": "audio", "data": audio_base64}
                            )
                            logger.info(f"[{session_id}] TTS audio sent")
                        except Exception as e:
                            logger.error(f"[{session_id}] TTS error: {e}")

                except Exception as e:
                    logger.error(f"[{session_id}] Error processing audio: {e}")
                    await websocket.send_json(
                        {"type": "error", "message": f"Błąd przetwarzania: {str(e)}"}
                    )

            elif "text" in message and message["text"]:
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type", "text")
                    content = data.get("content", "")

                    if msg_type == "text" and content:
                        logger.info(f"[{session_id}] User text: {content[:50]}...")

                        sentiment_label = None
                        sentiment_score = 0.0
                        if analyze_sentiment:
                            try:
                                result = analyze_sentiment(content)
                                if result:
                                    sentiment_label, sentiment_score = result
                                    logger.info(
                                        f"[{session_id}] Sentiment: {sentiment_label} ({sentiment_score:.2f})"
                                    )
                            except Exception as e:
                                logger.error(
                                    f"[{session_id}] Sentiment analysis error: {e}"
                                )

                        (
                            response_text,
                            sessions[session_id],
                        ) = await service.process_message(
                            content,
                            sessions[session_id],
                            sentiment=sentiment_label,
                            score=sentiment_score,
                        )
                        logger.info(
                            f"[{session_id}] Assistant: {response_text[:50]}..."
                        )

                        await websocket.send_json(
                            {"type": "response", "text": response_text}
                        )

                        if tts and response_text:
                            try:
                                logger.info(f"[{session_id}] Generating TTS audio...")
                                audio_base64 = tts.generate_audio_base64(response_text)
                                await websocket.send_json(
                                    {"type": "audio", "data": audio_base64}
                                )
                                logger.info(f"[{session_id}] TTS audio sent")
                            except Exception as e:
                                logger.error(f"[{session_id}] TTS error: {e}")
                    else:
                        await websocket.send_json(
                            {"type": "error", "message": "Invalid message format"}
                        )
                except json.JSONDecodeError:
                    await websocket.send_json(
                        {"type": "error", "message": "Invalid JSON"}
                    )

    except WebSocketDisconnect:
        logger.info(f"Session {session_id} disconnected")
