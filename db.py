import os
import mysql.connector
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@contextmanager
def get_cursor(commit=False):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def fetch_all(sql, params=()):
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()