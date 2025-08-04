import sqlite3
from pathlib import Path

class Database:
    def __init__(self):
        self.db_path = Path(__file__).parent / "bot_database.db"
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_message(self, content):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO messages (content) VALUES (?)
        ''', (content,))
        self.conn.commit()

    def get_latest_message(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT content FROM messages 
            ORDER BY updated_at DESC 
            LIMIT 1
        ''')
        result = cursor.fetchone()
        return result[0] if result else "No messages available"
