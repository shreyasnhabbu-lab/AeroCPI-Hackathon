import sqlite3
import os

DB_NAME = "phantom_airfares.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS airfares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT NOT NULL,
            date TEXT NOT NULL,
            price REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_airfare(data: dict):
    """
    Accepts exact dictionary contract:
    {"route": "BLR-DEL", "date": "2026-10-01", "price": 5400, "status": "success"}
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO airfares (route, date, price, status)
        VALUES (?, ?, ?, ?)
    """, (data.get("route"), data.get("date"), data.get("price"), data.get("status")))
    conn.commit()
    conn.close()
