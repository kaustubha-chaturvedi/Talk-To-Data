import sqlite3
from langchain_community.utilities.sql_database import SQLDatabase

def load_db(db_uri):
    db = SQLDatabase.from_uri(db_uri)
    return db