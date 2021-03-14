import sqlite3, datetime, json
from sqlite3 import Error
from datetime import date, timedelta, datetime

# Create a database connection to a SQLite database
def create_connection():
    try:
        conn = sqlite3.connect('Database/database.db')
        cur = conn.cursor()
        return conn, cur
    except Error as e:
        print(e)
        return (str(e))

# Close a database connection to a SQLite database
def close_connection(conn, cur):
    try:
        cur.close()
        conn.close()
    except Error as e:
        print(e)
        return (str(e))

# Checks whether a date is a weekday or weekend
def check_weekend(date):
    weekend = {5: "Saturday", 6: "Sunday"}

    # Check what is the value for the date
    num = date.weekday()    # returns a value from 0-6 where 0 is Monday and 6 is Sunday
    if num in weekend:
        return True
    else:
        return False

# Checks whether constraints are met
def is_constraint_met(table_name,start_date,end_date):
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
    
    except Exception as e:
        return (str(e))

    try:
        # Manipulating the dates for the function to work
        sdate = datetime.strptime(start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(end_date, '%Y-%m-%d').date()   # end date
        delta = edate - sdate       # as timedelta

        # Dictionary to store the results that will be returned if constraints are not met in the form: {date:[constraint1,constraint2],date:[constraint1],...}
        dict_notmet = {}

        # Creating a loop to check the constraints for each day
        for date_diff in range(delta.days + 1):
            day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
            day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)

            # Retrieve from DB each day's schedule
            # WARNING: Prone to SQL Injection Attack (Assumption is that the admin is trustworthy and won't jeopardise the system)
            sqlstmt = """SELECT * FROM """ + table_name + """ WHERE date = ?;"""
            cur.execute(sqlstmt,(day_key,))
            constraints_result = cur.fetchone()

            # Counters to record the number of calls/duties for each day assigned
            counter_clinic1 = 0
            counter_clinic2 = 0
            counter_amsatclinic1 = 0
            counter_amsatclinic3 = 0
            counter_amsatclinic4 = 0
            counter_p = 0
            counter_totalcall = 0

            # Counting the calls/duties from all doctors for each day
            for element in constraints_result[1:]:
                str_element = element.replace("'",'"')
                dict_element = json.loads(str_element)
                for key,value in dict_element.items():
                    if value == 'amSat Clinic 1':
                        counter_amsatclinic1 += 1
                    elif value == 'Clinic 1':
                        counter_clinic1 += 1
                    elif value == 'Clinic 2':
                        counter_clinic2 += 1
                    elif value == 'amSat Clinic 3':
                        counter_amsatclinic3 += 1
                    elif value == 'amSat Clinic 4':
                        counter_amsatclinic4 += 1
                    elif value == 'P':
                        counter_p += 1
                    elif value == 'c' or value == 'cr':
                        counter_totalcall += 1

            # Compare whether the current schedule meets the constraints
            not_met = []
            if counter_totalcall < total_call:
                not_met.append("total call")
            if counter_clinic1 < clinic1:
                not_met.append("clinic 1")
            if counter_clinic2 < clinic2:
                not_met.append("clinic 2")
            if counter_amsatclinic4 < amSat_clinic4:
                not_met.append("amSat Clinic 4")
            if counter_amsatclinic1 < amSat_clinic1:
                not_met.append("amSat Clinic 1")
            if counter_amsatclinic3 < amSat_clinic3:
                not_met.append("amSat Clinic 3")
            if counter_p < p:
                not_met.append("P")

        # Dictionary to store the overall days and constraints that are not met
        dict_notmet[day_key] = not_met

        # Close connection to DB
        close_connection(conn, cur)

        # Returns the failed constraints dictionary in the form: {date:[constraint1,constraint2],date:[constraint1],...}
        if dict_notmet:
            return dict_notmet
        # Return True when constraints met
        else:
            return True
    
    except Exception as e:
        return (str(e))