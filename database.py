import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    connection = sqlite3.connect(DATABASE_URL)
    connection.row_factory = sqlite3.Row
    return connection

# ZADACA 1: Napraviti tabele i pozvati create_database

def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories(
            id,
            name
        )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id
            name
            ...
        )
    """)
