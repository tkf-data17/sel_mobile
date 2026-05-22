import sqlite3

class DatabaseManager:
    def __init__(self):
        conn = sqlite3.connect("chat_logs.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                query TEXT,
                response TEXT,
                score TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save_feedback(self, user_id, query, response, score):
        conn = sqlite3.connect("chat_logs.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_logs (user_id, query, response, score)
            VALUES (?, ?, ?, ?)
        """, (user_id, query, response, score))
        conn.commit()
        conn.close()

    def get_feedback(self):
        conn = sqlite3.connect("chat_logs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_logs")
        result = cursor.fetchall()
        conn.close()
        return result