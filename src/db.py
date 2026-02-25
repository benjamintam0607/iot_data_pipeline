import sqlite3
import os

# DB_PATH = os.getenv("DB_PATH", "data/iot.db")

def get_connection(dp_path=None):
    conn = sqlite3.connect(dp_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")  
    conn.execute("PRAGMA synchronous=NORMAL") 
    return conn

def init_db(db_path=None):

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = get_connection(db_path)
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()