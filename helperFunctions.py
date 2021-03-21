import sqlite3, datetime, json
import pandas as pd
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

# Checks the day of the date
def check_day(date):
    week = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    
    # Check what is the value for the date
    num = date.weekday()    # returns a value from 0-6 where 0 is Monday and 6 is Sunday
    return week[num]

# Check the number for the request month
def check_month_num(request_month):
    month = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    return month[request_month]

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

# Read Roster from excel file
def readRoster():
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Roster table from DB
    cur.execute("""DELETE FROM Roster""")
    conn.commit()

    # Delete any existing data from Skill table from DB
    cur.execute("""DELETE FROM Skill""")
    conn.commit()

    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Roster')
    df.rename(columns=df.iloc[0], inplace = True)
    df.drop([0], inplace = True)

    '''
    Structure: roster_dict = {
                email 1:[name, first position, second position, posting, [skill 1,skill 2,...], type], 
                email 2:[name, first position, second position, posting, [skill 1,skill 2,...], type],
                ...
            }
    '''
    roster_dict = {}

    index = df.index
    number_of_rows = len(index)

    # Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        first_position = df.iloc[i][2]
        second_position = df.iloc[i][3]
        posting = df.iloc[i][4]
        json_skills = df.iloc[i][5]
        skills = json_skills.split(';')
        mo_type = df.iloc[i][6]
        roster_dict[email] = [name,first_position,second_position,posting,skills,mo_type]

        # Insert values into Roster table in DB
        cur.execute("""INSERT OR IGNORE INTO Roster(email, name, first_position, second_position, posting, type) 
                VALUES (?, ?, ?, ?, ?, ?);""", (email,name,first_position,second_position,posting,mo_type))
        conn.commit()

        # If a new staff joins the department, insert a fresh data column into Points table for that new staff; Old staff values are untouched
        cur.execute("""INSERT OR IGNORE INTO Points(email, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12) 
                VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);""", (email,))
        conn.commit()

        # Insert the multiple skills each staff has into Skill table in DB
        for each_skill in skills:
            cur.execute("""INSERT OR IGNORE INTO Skill(email, skill)  
                    VALUES (?, ?);""", (email,each_skill))
            conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)

    return roster_dict

# Read Duty from excel file
def readDuties(query_start_date,query_last_date):
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Duty table from DB
    cur.execute("""DELETE FROM Duty""")
    conn.commit()
    
    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Duties')
    #print(df)

    '''
    Structure: duties_dict = {
                email 1:[name, duty name, start date, end date], 
                email 2:[name, duty name, start date, end date],
                ...
            }
    '''
    duties_dict = {}

    index = df.index
    number_of_rows = len(index)
    #print(number_of_rows)
    #print()

    #Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        duty_name = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        #start_date = pd.to_datetime(df.iloc[i][3])
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        #end_date = pd.to_datetime(df.iloc[i][4])
        temp = {}
        temp[start_date] = [name,duty_name,end_date]
        #print(temp)

        if email in duties_dict:
            duties_dict[email].update(temp)
        if email not in duties_dict:
            duties_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO Duty(email, name, duty_name, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,name,duty_name,start_date,end_date))
        conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)

    #print(duties_dict)
    return duties_dict

# Read Training from excel file
def readtraining(query_start_date,query_last_date):
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM Training""")
    conn.commit()

    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Training')
    #print(df)

    '''
    Structure: training_dict = {
                email 1:[name, Training, start date, end date], 
                email 2:[name, Training, start date, end date],
                ...
            }
    '''
    training_dict = {}

    index = df.index
    number_of_rows = len(index)
    #print(number_of_rows)
    #print()

    #Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        training = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        #start_date = pd.to_datetime(df.iloc[i][3])
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        #end_date = pd.to_datetime(df.iloc[i][4])
        temp = {}
        temp[start_date] = [name,training,end_date]
        #print(temp)

        if email in training_dict:
            training_dict[email].update(temp)
        if email not in training_dict:
            training_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO Training(email, name, training, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,name,training,start_date,end_date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    #print(training_dict)
    return training_dict

# Read Priority Leave from excel file
def readpleave(query_start_date,query_last_date):
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM Training""")
    conn.commit()

    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Leaves')
    #print(df)

    '''
    Structure: pleave_dict = {
                email 1:[name, leave reason, start date, end date], 
                email 2:[name, leave reason, start date, end date],
                ...
            }
    '''
    pleave_dict = {}

    index = df.index
    number_of_rows = len(index)
    #print(number_of_rows)
    #print()

    #Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        leave_reason = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        #start_date = pd.to_datetime(df.iloc[i][3])
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        #end_date = pd.to_datetime(df.iloc[i][4])
        temp = {}
        temp[start_date] = [name,leave_reason,end_date]
        #print(temp)

        if email in pleave_dict:
            pleave_dict[email].update(temp)
        if email not in pleave_dict:
            pleave_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO PriorityLeave(email, name, reason, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,name,leave_reason,start_date,end_date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    #print(duties_dict)
    return pleave_dict

# [Currently not in use] Read Public Holiday from excel file
def readPh():
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from PublicHoliday table from DB
    cur.execute("""DELETE FROM PublicHoliday""")
    conn.commit()

    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Public Holiday')

    '''
    Structure: pl_dict = {
                date 1:[name, day], 
                date 2:[name, day],
                ...
            }
    '''
    ph_dict = {}

    index = df.index
    number_of_rows = len(index)

    # Extract data and put into a dictionary
    for i in range(number_of_rows):
        date = pd.to_datetime(df.iloc[i][0]).strftime('%Y-%m-%d')
        day = df.iloc[i][1]
        name = df.iloc[i][2]
        ph_dict[date] = [name,day]
        cur.execute("""INSERT OR IGNORE INTO PublicHoliday(holiday_name, holiday_date, holiday_day) 
                VALUES (?, ?, ?);""", (name,date,day))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    # print(pl_dict)
    return ph_dict