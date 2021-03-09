import sqlite3, datetime
from sqlite3 import Error
from datetime import date, timedelta

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

def check_weekend(date):
    weekend = {5: "Saturday", 6: "Sunday"}
    
    # Check what is the value for the date
    num = date.weekday()    # returns a value from 0-6 where 0 is Monday and 6 is Sunday
    if num in weekend:
        return True
    else:
        return False