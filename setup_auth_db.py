import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup():
    conn = sqlite3.connect('aero_cpi.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Clear existing to be safe
    cursor.execute('DELETE FROM users')
    
    # Insert Demo Accounts
    users = [
        ('admin@mospi.gov.in', hash_password('admin123'), 'admin'),
        ('jury@mospi.gov.in', hash_password('jury123'), 'user')
    ]
    
    cursor.executemany('INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)', users)
    
    conn.commit()
    conn.close()
    print("Database updated with secure users table!")

if __name__ == '__main__':
    setup()
