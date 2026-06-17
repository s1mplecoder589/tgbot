import sqlite3

db = sqlite3.connect("users.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    age TEXT,
    mahalla TEXT
)
""")

db.commit()

def add_user(user_id, first_name, last_name, phone, age, mahalla):
    cursor.execute("""
    INSERT OR REPLACE INTO users
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, first_name, last_name, phone, age, mahalla))
    db.commit()

def get_users():
    cursor.execute("SELECT user_id FROM users")
    return cursor.fetchall()

def get_all_users():
    cursor.execute("""
    SELECT user_id, first_name, last_name, phone, age, mahalla
    FROM users
    """)
    return cursor.fetchall()

def users_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]