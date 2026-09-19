import psycopg2
import os

DATABASE_URL = "postgresql://neondb_owner:npg_BR1ro8vGHAND@ep-long-frog-az4ccszz-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

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
