import sqlite3
import json
import os
import uuid

DB_PATH = "drafts.db"

def _init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS onboarding_drafts (
            token TEXT PRIMARY KEY,
            step INTEGER,
            data_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_draft(step, data, token=None):
    try:
        _init_db()
        if not token:
            token = str(uuid.uuid4())
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # default=str asegura que fechas o campos no serializables no rompan JSON
        data_str = json.dumps(data, default=str)
        cursor.execute('''
            INSERT INTO onboarding_drafts (token, step, data_json)
            VALUES (?, ?, ?)
            ON CONFLICT(token) DO UPDATE SET
                step=excluded.step,
                data_json=excluded.data_json,
                updated_at=CURRENT_TIMESTAMP
        ''', (token, step, data_str))
        
        conn.commit()
        conn.close()
        return token
    except Exception as e:
        print(f"Error saving draft: {e}")
        return f"ERROR: {str(e)}"

def load_draft(token):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT step, data_json FROM onboarding_drafts WHERE token = ?', (token,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        step, data_str = row
        try:
            data = json.loads(data_str)
            return step, data
        except Exception:
            return None, None
    return None, None
