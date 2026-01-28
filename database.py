import sqlite3
from flask import g
import bcrypt

DB_NAME = "library.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_NAME)
    cur = db.cursor()

  
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL,
            role TEXT CHECK(role IN ('admin', 'member')) NOT NULL
        )
    """)

   
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            available INTEGER CHECK(available IN (0,1)) DEFAULT 1
        )
    """)

   
    cur.execute("""
        CREATE TABLE IF NOT EXISTS borrowed_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
        )
    """)

   
    admin_username = "admin"
    admin_password = "admin123"

    cur.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
    if not cur.fetchone():
        hashed = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (admin_username, hashed, "admin")
        )

    db.commit()
    db.close()
