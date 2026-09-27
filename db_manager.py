import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def init_db():
    pass # Already initialized via migration script

def save_airfare(data: dict):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO historical_prices (route, date, price, class_type, source_portal)
        VALUES (%s, %s, %s, %s, %s)
    """, (data.get("route"), data.get("date"), data.get("price"), "economy", "Mock"))
    conn.commit()
    conn.close()
