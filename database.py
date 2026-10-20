import sqlite3
from datetime import datetime

DB_PATH = "kitt.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT    NOT NULL,
                text       TEXT    NOT NULL,
                command    TEXT,
                success    INTEGER NOT NULL
        )
""")

def log_event(text, command, success):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO events (created_at, text, command, success) VALUES(?, ?, ?, ?)",
            (created_at, text, command, int(success)),
        )

def most_used_commands(limit=3):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT command, COUNT(*) AS total
            FROM events
            WHERE command IS NOT NULL
            GROUP BY command
            ORDER BY total DESC, command ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

def unknown_phrases(limit=5):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT text, COUNT(*) AS total
            FROM events
            WHERE command IS NULL
            GROUP BY text
            ORDER BY total DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

def success_rate():
    with get_connection() as conn:
        return conn.execute(
            "SELECT COUNT(*), ROUND(AVG(success) * 100) FROM events"
        ).fetchone()

def today_summary():
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        total, first = conn.execute(
            "SELECT COUNT(*), MIN(created_at) FROM events WHERE created_at >= ?",
            (today,),
        ).fetchone()
        top = conn.execute(
            """
            SELECT command, COUNT(*) AS total
            FROM events
            WHERE created_at >= ? AND command IS NOT NULL
            GROUP BY command
            ORDER BY total DESC, command ASC
            LIMIT 1
            """,
            (today,),
        ).fetchone()
    return total, first, top