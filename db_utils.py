import sqlite3
from langchain_community.utilities.sql_database import SQLDatabase

def load_db(db_uri):
    db = SQLDatabase.from_uri(db_uri)
    return db

def load_store():
    conn = sqlite3.connect("queries.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            query TEXT,
            result TEXT
        )
    ''')
    conn.commit()
    return cursor, conn

def store_query(question, query, result):
    cursor, conn = load_store()
    cursor.execute("INSERT INTO query_history (question, query, result) VALUES (?, ?, ?)",
                   (question, query, result))
    conn.commit()

def get_query_history():
    cursor, _ = load_store()
    cursor.execute("SELECT * FROM query_history")
    history = cursor.fetchall()
    return history
