import sqlite3
from typing import Any
from ..config import DB_PATH


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        disabled BOOLEAN NOT NULL DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()


class DatabaseService:
    
    def execute_query(self, query: str, params: tuple = ()) -> Any:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return conn, cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> dict:
        conn, cursor = self.execute_query(query, params)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def fetch_all(self, query: str, params: tuple = ()) -> list:
        conn, cursor = self.execute_query(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def execute(self, query: str, params: tuple = ()) -> int:
        conn, cursor = self.execute_query(query, params)
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return last_id
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        conn, cursor = self.execute_query(query, params)
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows
 