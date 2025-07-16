
import sqlite3
import uuid
from datetime import datetime

class SimpleChatEngine:
    def __init__(self, db_path="data/user_profiles.db"):
        self.db_path = db_path

    def _save_message(self, chat_id: str, user_id: str, role: str, message: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                chat_id TEXT,
                user_id TEXT,
                role TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "INSERT INTO conversations (chat_id, user_id, role, message) VALUES (?, ?, ?, ?)",
            (chat_id, user_id, role, message)
        )
        conn.commit()
        conn.close()

    def _generate_response(self, message: str) -> str:
        # Mock response, replace with IBM LLM or other AI later
        return f"I received your message: '{message}'. This is a placeholder response."

    def chat(self, user_id: str, message: str, chat_id: str = None):
        chat_id = chat_id or str(uuid.uuid4())

        # Save user message
        self._save_message(chat_id, user_id, "user", message)

        # Generate and save assistant response
        response = self._generate_response(message)
        self._save_message(chat_id, user_id, "assistant", response)

        return {
            "chat_id": chat_id,
            "response": response
        }

    def get_history(self, chat_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, message, timestamp FROM conversations WHERE chat_id = ? ORDER BY timestamp",
            (chat_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
