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

def is_constraint_met():
    try:
        # Establish connection to DB
        conn, cur = create_connection()
    
        # Fetch the constraints defined by the user from DB
        cur.execute("""SELECT * FROM Constraints;""")
        constraints_results = cur.fetchone()
        total_call = constraints_results[5]
        clinic1 = constraints_results[6]
        clinic2 = constraints_results[7]
        amSat_clinic4 = constraints_results[8]
        amSat_clinic1 = constraints_results[9]
        amSat_clinic3 = constraints_results[10]
        p = constraints_results[11]

        # Retrieve from DB the current scheduling call and duty numbers
        cur.execute("""SELECT COUNT(*) FROM CallLP where request_type = "c" or request_type = "cr";""")
        constraints_results = cur.fetchone()
        current_total_call = constraints_results[0]

        cur.execute("""SELECT COUNT(*) FROM Duty where duty_name = "Clinic 1";""")
        constraints_results = cur.fetchone()
        current_clinic1 = constraints_results[0]

        cur.execute("""SELECT COUNT(*) FROM Duty where duty_name = "Clinic 2";""")
        constraints_results = cur.fetchone()
        current_clinic2 = constraints_results[0]

        cur.execute("""SELECT COUNT(*) FROM Duty where duty_name = "amSat Clinic 4";""")
        constraints_results = cur.fetchone()
        current_amSat_clinic4 = constraints_results[0]

        cur.execute("""SELECT COUNT(*) FROM Duty where duty_name = "amSat Clinic 1";""")
        constraints_results = cur.fetchone()
        current_amSat_clinic1 = constraints_results[0]

        cur.execute("""SELECT COUNT(*) FROM Duty where duty_name = "amSat Clinic 3";""")
        constraints_results = cur.fetchone()
        current_amSat_clinic3 = constraints_results[0]

        cur.execute("""SELECT COUNT(*) FROM Duty where duty_name = "P";""")
        constraints_results = cur.fetchone()
        current_p = constraints_results[0]

        # Compare whether the current >= constraints
        not_met = []
        if current_total_call < total_call:
            not_met.append("total_call")
        if current_clinic1 < clinic1:
            not_met.append("clinic 1")
        if current_clinic2 < clinic2:
            not_met.append("clinic 2")
        if current_amSat_clinic4 < amSat_clinic4:
            not_met.append("amSat Clinic 4")
        if current_amSat_clinic1 < amSat_clinic1:
            not_met.append("amSat Clinic 1")
        if current_amSat_clinic3 < amSat_clinic3:
            not_met.append("amSat Clinic 3")
        if current_p < p:
            not_met.append("P")

        # Return True when constraints met, otherwise return the failed constraints
        if len(not_met) == 0:
            return True
        else:
            return not_met

        # Close connection to DB
        close_connection(conn, cur)
    
    except Exception as e:
        return (str(e))