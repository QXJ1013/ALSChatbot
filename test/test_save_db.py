import sqlite3

DB_PATH = "database/simple_chat.db"

def check_all():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 10")
    for row in cursor.fetchall():
        print(row)
    conn.close()

if __name__ == "__main__":
    check_all()
