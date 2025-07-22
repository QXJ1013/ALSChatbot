import sqlite3
from datetime import datetime

DB_PATH = "database/simple_chat.db"

def save_message(chat_id: str, user_id: str, role: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (chat_id, user_id, role, message, timestamp) VALUES (?, ?, ?, ?, ?)",
        (chat_id, user_id, role, message, datetime.utcnow())
    )
    conn.commit()
    conn.close()

def load_context(chat_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, message FROM conversations WHERE chat_id=? ORDER BY timestamp ASC", (chat_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

if __name__ == "__main__":
    test_chat_id = "test_session_001"
    save_message(test_chat_id, "user_001", "user", "Hello, I need help.")
    save_message(test_chat_id, "user_001", "assistant", "Sure, how can I help?")
    print(load_context(test_chat_id))
