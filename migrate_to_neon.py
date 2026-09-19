import sqlite3
import psycopg2
from psycopg2.extras import execute_values

DATABASE_URL = "postgresql://neondb_owner:npg_BR1ro8vGHAND@ep-long-frog-az4ccszz-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

print("Connecting to Neon...")
pg_conn = psycopg2.connect(DATABASE_URL)
pg_cursor = pg_conn.cursor()

# Create tables in Postgres
print("Creating tables in Postgres...")
pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS historical_prices (
    date TEXT,
    route TEXT,
    price INTEGER,
    departure_date TEXT,
    timestamp TEXT,
    class_type TEXT DEFAULT 'economy',
    source_portal TEXT DEFAULT 'Ixigo',
    airline TEXT DEFAULT 'Unknown',
    flight_code TEXT DEFAULT 'Unknown'
);

CREATE TABLE IF NOT EXISTS extraction_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    target_route TEXT,
    status TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);
""")
pg_conn.commit()

print("Connecting to SQLite...")
sl_conn = sqlite3.connect('aero_cpi.db')
sl_cursor = sl_conn.cursor()

# Migrate users
sl_cursor.execute("SELECT id, email, password_hash, role FROM users")
users = sl_cursor.fetchall()
if users:
    print(f"Migrating {len(users)} users...")
    pg_cursor.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")
    execute_values(pg_cursor, "INSERT INTO users (id, email, password_hash, role) VALUES %s", users)
    pg_conn.commit()

# Migrate logs
sl_cursor.execute("SELECT id, timestamp, target_route, status, error_message FROM extraction_logs")
logs = sl_cursor.fetchall()
if logs:
    print(f"Migrating {len(logs)} logs...")
    pg_cursor.execute("TRUNCATE TABLE extraction_logs RESTART IDENTITY CASCADE;")
    execute_values(pg_cursor, "INSERT INTO extraction_logs (id, timestamp, target_route, status, error_message) VALUES %s", logs)
    pg_conn.commit()

# Migrate historical_prices
sl_cursor.execute("SELECT date, route, price, departure_date, timestamp, class_type, source_portal, airline, flight_code FROM historical_prices")
prices = sl_cursor.fetchall()
if prices:
    print(f"Migrating {len(prices)} prices...")
    pg_cursor.execute("TRUNCATE TABLE historical_prices;")
    execute_values(pg_cursor, "INSERT INTO historical_prices (date, route, price, departure_date, timestamp, class_type, source_portal, airline, flight_code) VALUES %s", prices)
    pg_conn.commit()

print("Migration Complete!")
pg_conn.close()
sl_conn.close()
