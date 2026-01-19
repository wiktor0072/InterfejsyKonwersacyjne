import sqlite3
import uuid
from datetime import datetime
from typing import Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "llm", "hotel_aurora.db")


def init_conversations_table():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                sentiment TEXT
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id)"
        )
        conn.commit()
        logger.info("Conversations table initialized")


class SessionService:
    def __init__(self):
        init_conversations_table()

    def generate_session_id(self) -> str:
        return str(uuid.uuid4())

    def save_message(
        self, session_id: str, role: str, content: str, sentiment: Optional[str] = None
    ):
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (session_id, role, content, timestamp, sentiment) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, timestamp, sentiment),
            )
            conn.commit()

    def load_history(self, session_id: str) -> list[dict[str, Any]]:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, timestamp, sentiment FROM conversations WHERE session_id = ? ORDER BY id",
                (session_id,),
            )
            rows = cursor.fetchall()

        return [
            {
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "sentiment": row[3],
            }
            for row in rows
        ]

    def get_messages_for_llm(
        self, session_id: str, system_prompt: str
    ) -> list[dict[str, Any]]:
        history = self.load_history(session_id)
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        return messages


session_service: Optional[SessionService] = None


def get_session_service() -> SessionService:
    global session_service
    if session_service is None:
        session_service = SessionService()
    return session_service
