import sqlite3
from sqlite3 import Error

def create_connection():
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect('Database/database.db')
        cur = conn.cursor()
        return conn, cur
    except Error as e:
        print(e)

def close_connection(conn, cur):
    """ close a database connection to a SQLite database """
    try:
        cur.close()
        conn.close()
    except Error as e:
        print(e)
