import sqlite3
import pandas as pd
from langchain_community.utilities.sql_database import SQLDatabase

def load_db(data_uri):
    # Load MySQL database from data URI
    db = SQLDatabase.from_uri(data_uri)
    return db

def load_csv(file_path):
    # Load CSV data into a pandas DataFrame and simulate it as a SQL table
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.replace(r"[^a-zA-Z0-9_]", "", regex=True)
    context = pd.io.sql.get_schema(df.reset_index(), "df").replace('"', "")
    return df, context

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
