import os
import sqlite3
import json
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), "database.db")

def init_mobile_chat_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mobile_chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,          -- 'user', 'agent', 'system'
        text TEXT NOT NULL,
        msg_type TEXT DEFAULT 'chat',   -- 'chat', 'approval_request', 'command_output'
        approval_status TEXT,          -- 'PENDING', 'APPROVED', 'REJECTED', None
        command_payload TEXT,          -- JSON string with command details
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def add_message(sender, text, msg_type='chat', approval_status=None, command_payload=None):
    init_mobile_chat_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    payload_str = json.dumps(command_payload) if isinstance(command_payload, dict) else command_payload
    cursor.execute("""
    INSERT INTO mobile_chat_messages (sender, text, msg_type, approval_status, command_payload, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (sender, text, msg_type, approval_status, payload_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id

def get_chat_history(limit=50):
    init_mobile_chat_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mobile_chat_messages ORDER BY id ASC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_approval_status(msg_id, new_status):
    init_mobile_chat_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE mobile_chat_messages 
    SET approval_status = ? 
    WHERE id = ?
    """, (new_status, msg_id))
    conn.commit()
    conn.close()

def clear_chat_history():
    init_mobile_chat_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mobile_chat_messages")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_mobile_chat_db()
    print("Mobile Chat SQLite Table initialized successfully.")
