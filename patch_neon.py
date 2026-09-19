import re

# 1. Alter Postgres table to add ID
import psycopg2
DATABASE_URL = "postgresql://neondb_owner:npg_BR1ro8vGHAND@ep-long-frog-az4ccszz-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
pg_conn = psycopg2.connect(DATABASE_URL)
pg_cursor = pg_conn.cursor()
try:
    pg_cursor.execute("ALTER TABLE historical_prices ADD COLUMN id SERIAL PRIMARY KEY;")
    pg_conn.commit()
except psycopg2.errors.DuplicateColumn:
    pg_conn.rollback()
pg_conn.close()

# 2. Patch main.py
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# Replace import sqlite3 with psycopg2
main_code = main_code.replace("import sqlite3", "import psycopg2\nimport psycopg2.extras")

# Replace get_db_connection
old_conn = """def get_db_connection():
    conn = sqlite3.connect('aero_cpi.db')
    conn.row_factory = sqlite3.Row
    return conn"""

new_conn = """def get_db_connection():
    conn = psycopg2.connect("postgresql://neondb_owner:npg_BR1ro8vGHAND@ep-long-frog-az4ccszz-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")
    return conn"""
main_code = main_code.replace(old_conn, new_conn)

# Fix read_sql_query and ? -> %s
# Function: get_routes
main_code = main_code.replace(
    "query = \"SELECT date, 'All Routes' as route, AVG(price) as price FROM historical_prices WHERE class_type = ? GROUP BY date ORDER BY date ASC\"\n        df = pd.read_sql_query(query, conn, params=(class_type,))",
    "query = \"SELECT date, 'All Routes' as route, AVG(price) as price FROM historical_prices WHERE class_type = %s GROUP BY date ORDER BY date ASC\"\n        df = pd.read_sql_query(query, conn, params=(class_type,))"
)
main_code = main_code.replace(
    "query = \"SELECT date, route, AVG(price) as price FROM historical_prices WHERE route = ? AND class_type = ? GROUP BY date ORDER BY date ASC\"\n        df = pd.read_sql_query(query, conn, params=(route, class_type))",
    "query = \"SELECT date, route, AVG(price) as price FROM historical_prices WHERE route = %s AND class_type = %s GROUP BY date ORDER BY date ASC\"\n        df = pd.read_sql_query(query, conn, params=(route, class_type))"
)

# Function: get_stats
main_code = main_code.replace(
    "cursor.execute(\"SELECT price FROM historical_prices WHERE route=? ORDER BY date ASC\", (r,))",
    "cursor.execute(\"SELECT price FROM historical_prices WHERE route=%s ORDER BY date ASC\", (r,))"
)
main_code = main_code.replace(
    "prices = [row['price'] for row in cursor.fetchall()]",
    "prices = [row[0] for row in cursor.fetchall()]"
)

# Fix rowid -> id
main_code = main_code.replace("rowid", "id")

# Function: login
main_code = main_code.replace(
    "cursor.execute(\"SELECT role, password_hash FROM users WHERE email = ?\", (request.email,))",
    "cursor.execute(\"SELECT role, password_hash FROM users WHERE email = %s\", (request.email,))"
)
main_code = main_code.replace(
    "user = cursor.fetchone()\n    conn.close()\n    \n    if not user or user['password_hash'] != request.password:",
    "user = cursor.fetchone()\n    conn.close()\n    \n    if not user or user[1] != request.password:"
)
main_code = main_code.replace(
    "return {\"status\": \"success\", \"role\": user['role']}",
    "return {\"status\": \"success\", \"role\": user[0]}"
)

# Function: raw_logs (has fetchone dict access issue?)
# raw_logs uses dict(row) from sqlite3.Row. We need RealDictCursor.
old_raw_logs = """    cursor = conn.cursor()
    cursor.execute("SELECT * FROM extraction_logs ORDER BY timestamp DESC LIMIT 20")
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()"""
new_raw_logs = """    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM extraction_logs ORDER BY timestamp DESC LIMIT 20")
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()"""
main_code = main_code.replace(old_raw_logs, new_raw_logs)

# Function: run_live_scrape INSERT
main_code = main_code.replace(
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
)
main_code = main_code.replace(
    "VALUES (?, ?, ?, ?, ?, ?)",
    "VALUES (%s, %s, %s, %s, %s, %s)"
)

# Function: scheduled_scrape INSERT (just in case)
# Wait, scheduled_scrape calls run_live_scrape, it doesn't do INSERT itself.

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
