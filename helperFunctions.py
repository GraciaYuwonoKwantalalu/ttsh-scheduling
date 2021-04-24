import sqlite3, datetime, json, pyodbc, dateutil.parser
import pandas as pd
from sqlite3 import Error
from datetime import date, timedelta, datetime
from win32com.client import Dispatch
from collections import OrderedDict
import dateutil.parser
from time import strptime
import pythoncom
import numpy as np
from collections import OrderedDict

def create_connection():
    """
    Creates a database connection to a SQLite database.
    """
    try:
        conn = sqlite3.connect('Database/database.db')
        cur = conn.cursor()
        return conn, cur
    except Error as e:
        return (str(e))

def close_connection(conn, cur):
    """
    Closes a database connection to a SQLite database.
    """
    try:
        cur.close()
        conn.close()
    except Error as e:
        return (str(e))

def check_weekend(date):
    """
    Checks whether a date is a weekday or weekend.
    """
    weekend = {5: "Saturday", 6: "Sunday"}

    # Check what is the value for the date
    num = date.weekday()    # returns a value from 0-6 where 0 is Monday and 6 is Sunday
    if num in weekend:
        return 'True'
    else:
        return 'False'

def check_day(date):
    """
    Checks the day of the date.
    """
    week = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    
    # Check what is the value for the date
    num = date.weekday()    # returns a value from 0-6 where 0 is Monday and 6 is Sunday
    return week[num]

def check_eveph(date,e):
    """
    Checks public holiday eve.
    """
    dateo = datetime.strptime(date, '%Y-%m-%d').date()
    eveo = dateo + timedelta(days=1)
    eves = eveo.strftime("%Y-%m-%d")
    if eves in e:
        return True

def check_month_num(request_month):
    """
    Checks the number for the request month.
    """   
    month = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    return month[request_month]

def is_constraint_met(table_name,start_date,end_date):
    """
    Validates timetable against specified constraints.

    :parameters: data from *Constraints* and *Temp* tables 
    :return: dictionary containing date and list of unmet constraints. 
    For example:
    *{"01-05-2021 Saturday": ["total call", "clinic 1", "clinic 2"]}*
    """   
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
            display_day = day.strftime("%d-%m-%Y") + " " + check_day(day) # Sunday 31-12-2020 (string format)

            # Retrieve from DB each day's schedule
            # WARNING: Prone to SQL Injection Attack (Assumption is that the admin is trustworthy and won't jeopardise the system)
            sqlstmt = """SELECT * FROM """ + table_name + """ WHERE date = ?;"""
            cur.execute(sqlstmt,(display_day,))
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
                    if 'amSat Clinic 1' in value:
                        counter_amsatclinic1 += 1
                    elif 'Clinic 1' in value:
                        counter_clinic1 += 1
                    elif 'Clinic 2' in value:
                        counter_clinic2 += 1
                    elif 'amSat Clinic 3' in value:
                        counter_amsatclinic3 += 1
                    elif 'amSat Clinic 4' in value:
                        counter_amsatclinic4 += 1
                    elif 'P' in value:
                        counter_p += 1
                    elif 'c-' in value or 'cr-' in value:
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
            
            if not_met:
                temp = {}
                temp[display_day] = not_met

            # Building dictionary to store the overall days and constraints that are not met
            if display_day in dict_notmet:
                dict_notmet[display_day].update(not_met)
            elif display_day not in dict_notmet:
                dict_notmet[display_day] = not_met

        # Close connection to DB
        close_connection(conn, cur)

        # Returns the failed constraints dictionary in the form: {date:[constraint1,constraint2],date:[constraint1],...}. Else, returns True.
        if dict_notmet:
            return dict_notmet
        else:
            return 'True'
    
    except Exception as e:
        return (str(e))

def readRoster():
    """
    Reads *Roster* sheet in *information_excel.xlsx* and updates *Roster* and *Skills* tables.

    :parameters: *Roster* sheet in *information_excel.xlsx**
    :return: dictionary of doctor emails and their roster details (name, first position, second position, posting, skills, type).
    For example: 
    *{"leekh@ttsh.com":["Lee Kang Hao", "MO2", "", "", ["brain", "teeth"], "S"]}*
    """   

    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Roster table from DB
    cur.execute("""DELETE FROM Roster""")
    conn.commit()

    # Delete any existing data from Skill table from DB
    cur.execute("""DELETE FROM Skill""")
    conn.commit()

    df = pd.read_excel (r'information_excel.xlsx', sheet_name='Roster')

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
        if pd.isnull(json_skills) == True:
            skills = "NULL"
        else:
            if ';' in json_skills: 
                skills = json_skills.split(';')
                # Insert the multiple skills each staff has into Skill table in DB
                for each_skill in skills:
                    cur.execute("""INSERT OR IGNORE INTO Skill(email, skill)  
                            VALUES (?, ?);""", (email,each_skill))
                    conn.commit()

            else: 
                skills = json_skills
                # Insert the multiple skills each staff has into Skill table in DB
                cur.execute("""INSERT OR IGNORE INTO Skill(email, skill)  
                        VALUES (?, ?);""", (email,skills))
                conn.commit()

        mo_type = df.iloc[i][6]
        roster_dict[email] = [str(name),first_position,second_position,posting,skills,mo_type]

        # Insert values into Roster table in DB
        cur.execute("""INSERT OR IGNORE INTO Roster(email, name, first_position, second_position, posting, type) 
                VALUES (?, ?, ?, ?, ?, ?);""", (email,str(name),first_position,second_position,posting,mo_type))
        conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)

    return roster_dict

def readDuties(query_start_date,query_last_date):
    """
    Reads *Duties* sheet in *information_excel.xlsx* and updates *Duty* table.

    :parameters: *Duties* sheet in *information_excel.xlsx**
    :return: dictionary of doctor emails and their duties details (name, duty name, start date, end date).
    For example: 
    *{"leekh@ttsh.com":["Lee Kang Hao", "ICU1", "5/2/2021", "5/3/2021"]}*
    """   

    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Duty table from DB
    cur.execute("""DELETE FROM Duty""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'Duty';""")
    conn.commit()
    
    df = pd.read_excel (r'information_excel.xlsx', sheet_name='Duties')

    duties_dict = {}

    index = df.index
    number_of_rows = len(index)

    #Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        duty_name = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        temp = {}
        temp[start_date] = [str(name),duty_name,end_date]

        if email in duties_dict:
            duties_dict[email].update(temp)
        if email not in duties_dict:
            duties_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO Duty(email, name, duty_name, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,str(name),duty_name,start_date,end_date))
        conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)

    return duties_dict

def readtraining(query_start_date,query_last_date):
    """
    Reads *Training* sheet in *information_excel.xlsx* and updates *Training* table.

    :parameters: *Training* sheet in *information_excel.xlsx**
    :return: dictionary of doctor emails and their training details (name, training, start date, end date).
    For example: 
    *{"leekh@ttsh.com":["Lee Kang Hao", "Refresher", "5/2/2021", "5/3/2021"]}*
    """   

    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM Training""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'Training';""")
    conn.commit()

    df = pd.read_excel (r'information_excel.xlsx', sheet_name='Training')

    training_dict = {}

    index = df.index
    number_of_rows = len(index)

    #Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        training = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        temp = {}
        temp[start_date] = [str(name),training,end_date]

        if email in training_dict:
            training_dict[email].update(temp)
        if email not in training_dict:
            training_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO Training(email, name, training, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,str(name),training,start_date,end_date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    return training_dict

def readpleave(query_start_date,query_last_date):
    """
    Reads *Priority Leave* sheet in *information_excel.xlsx* and updates *PriorityLeave* table.

    :parameters: *Priority Leave* sheet in *information_excel.xlsx**
    :return: dictionary of doctor emails and their training details (name, leave reason, start date, end date).
    For example: 
    *{"leekh@ttsh.com":["Lee Kang Hao", "Annual Leave", "5/2/2021", "5/3/2021"]}*
    """   

    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM PriorityLeave""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'PriorityLeave';""")
    conn.commit()

    df = pd.read_excel (r'information_excel.xlsx', sheet_name='Priority Leave')

    pleave_dict = {}

    index = df.index
    number_of_rows = len(index)

    #Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        leave_reason = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        temp = {}
        temp[start_date] = [str(name),leave_reason,end_date]

        if email in pleave_dict:
            pleave_dict[email].update(temp)
        if email not in pleave_dict:
            pleave_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO PriorityLeave(email, name, reason, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,str(name),leave_reason,start_date,end_date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    return pleave_dict

def readPh():
    """
    Reads *Public Holiday* sheet in *information_excel.xlsx*.

    :parameters: *Public Holiday* sheet in *information_excel.xlsx**
    :return: dictionary containing date, day and holiday name. 
    For example: 
    *{"1/1/2020":["New Year's Day", "Wednesday"]}*
    """   

    df = pd.read_excel (r'information_excel.xlsx', sheet_name='Public Holiday')

    ph_dict = {}

    index = df.index
    number_of_rows = len(index)

    # Extract data and put into a dictionary
    for i in range(number_of_rows):
        date = pd.to_datetime(df.iloc[i][0]).strftime('%Y-%m-%d')
        day = df.iloc[i][1]
        name = df.iloc[i][2]
        ph_dict[date] = [name,day]

    return ph_dict

def readPrevCalls():
    """
    Reads *Last 2 Days Calls* sheet in *information_excel.xlsx*.

    :parameters: *Last 2 Days Calls* sheet in *information_excel.xlsx**
    :return: list containing dictionaries of call date and email. 
    For example: 
    *[{"2/1/2020", "leekh@ttsh.com"}]*
    """ 

    df = pd.read_excel (r'information_excel.xlsx', sheet_name='Last 2 Days Calls')

    prev_call_list = []

    index = df.index
    number_of_rows = len(index)

    temp1_dict = {}
    dates_list = []

    # Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        call_date = pd.to_datetime(df.iloc[i][2]).strftime('%Y-%m-%d')

        if call_date in temp1_dict:
            temp1_dict[call_date].append(email)
        if call_date not in temp1_dict:
            temp1_dict[call_date] = [email]
            dates_list.append(call_date)
    
    for i in dates_list:
        prev_call_list.append(temp1_dict[i])

    return prev_call_list

def readCallRequest(query_start_date, query_last_date):
    """
    Retrieves call request from *CallRequest* table.

    :parameters: *CallRequest* table
    :return: dictionary containing doctor emails, date, name, request type, remark. 
    For example: 
    *{"leekh@ttsh.com":{"2021-05-03": ["Lee Kang Hao", "OnCall", "Mock"]}}*
    """   

    # Establish connection to DB
    conn, cur = create_connection()
    
    # Fetch the call request data stored in DB
    cur.execute("""SELECT * FROM CallRequest WHERE date >= ? AND date <= ?;""",
    (query_start_date, query_last_date))
    cr_results = cur.fetchall()

    # Dictionary to store the call request results
    cr_dict = {}

    # Reading from the DB results
    for each in cr_results:
        email = each[1]
        name = each[2]
        request_type = each[4]
        date = pd.to_datetime(each[3]).strftime('%Y-%m-%d')
        remark = each[5]

        temp = {}
        temp[date] = [str(name),request_type,remark]

        if email in cr_dict:
            cr_dict[email].update(temp)
        if email not in cr_dict:
            cr_dict[email] = temp
    
    # Close connection to DB
    close_connection(conn, cur)

    return cr_dict

def readLeaveApplication(query_start_date, query_last_date):
    """
    Retrieves leave request from *LeaveApplication* table.

    :parameters: *LeaveApplication* table
    :return: dictionary containing doctor emails, start date, name, leave type, end date, duration and remark. 
    For example: 
    *{"leekh@ttsh.com":{"2021-05-03": ["Lee Kang Hao", "AnnualLeave", "2021-05-05", "PM", "Mock"]}}*
    """   

    # Establish connection to DB
    conn, cur = create_connection()

    # Fetch the leave application data stored in DB
    cur.execute("""SELECT * FROM LeaveApplication WHERE start_date >= ? INTERSECT SELECT * FROM LeaveApplication WHERE start_date <= ? 
        UNION SELECT * FROM LeaveApplication WHERE end_date <= ? INTERSECT SELECT * FROM LeaveApplication WHERE end_date >= ?;""",
    (query_start_date, query_last_date, query_last_date, query_start_date))
    la_results = cur.fetchall()

    # Dictionary to store the call request results
    la_dict = {}

    # Reading from the DB results
    for each in la_results:
        email = each[1]
        name = each[2]
        leave_type = each[6]
        start_date = pd.to_datetime(each[3]).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(each[4]).strftime('%Y-%m-%d')
        remark = each[7]
        duration = each[5]

        temp = {}
        temp[start_date] = [str(name),leave_type,end_date, duration, remark]

        if email in la_dict:
            la_dict[email].update(temp)
        if email not in la_dict:
            la_dict[email] = temp
    
    # Close connection to DB
    close_connection(conn, cur)

    return la_dict

def clashes(query_start_date,query_last_date):    
    """
    Check for schedule clashes in *Training*, *Duties* and *Priority Leave* sheets in *information_excel.xlsx*

    :parameters: *Training*, *Duties* and *Priority Leave* sheets in *information_excel.xlsx*
    :return: dictionary containing date, email, name and sheets with clashes. 
    For example: *{"2021-05-03": ["leekh@ttsh.com", "Lee Kang Hao", ["Training", "Duty"]]}*
    """   

    # Combined dictionary to store all the data from the excel file for the scheduled dates
    combined = {}
    
    # Reading and storing the excel file data
    sdate = datetime.strptime(query_start_date, '%Y-%m-%d').date()   # start date
    edate = datetime.strptime(query_last_date, '%Y-%m-%d').date()   # end date
    delta = edate - sdate       # as timedelta
    for date_diff in range(delta.days + 1):
        day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
        day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)
        display_day = day.strftime("%d-%m-%Y") + " " + check_day(day) # Sunday 31-12-2020 (string format)
        
        # Read Training from excel and store inside training_list
        training_list = []
        df = pd.read_excel (r'information_excel.xlsx', sheet_name='Training')
        index = df.index
        number_of_rows = len(index)
        for i in range(number_of_rows):
            start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
            end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
            if day >= datetime.strptime(start_date, '%Y-%m-%d').date() and day <= datetime.strptime(end_date, '%Y-%m-%d').date():
                email = df.iloc[i][0]
                name = df.iloc[i][1]
                training = df.iloc[i][2]
                training_list.append([email,str(name),training,start_date,end_date])
        
        # Read Duties from excel and store inside duty_list
        duty_list = []
        df = pd.read_excel (r'information_excel.xlsx', sheet_name='Duties')
        index = df.index
        number_of_rows = len(index)
        for i in range(number_of_rows):
            start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
            end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
            if day >= datetime.strptime(start_date, '%Y-%m-%d').date() and day <= datetime.strptime(end_date, '%Y-%m-%d').date():
                email = df.iloc[i][0]
                name = df.iloc[i][1]
                duty_name = df.iloc[i][2]
                duty_list.append([email,str(name),duty_name,start_date,end_date])
        
        # Read Priority Leave from excel and store inside pl_list
        pl_list = []
        df = pd.read_excel (r'information_excel.xlsx', sheet_name='Priority Leave')
        index = df.index
        number_of_rows = len(index)
        for i in range(number_of_rows):
            start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
            end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
            if day >= datetime.strptime(start_date, '%Y-%m-%d').date() and day <= datetime.strptime(end_date, '%Y-%m-%d').date():
                email = df.iloc[i][0]
                name = df.iloc[i][1]
                leave_reason = df.iloc[i][2]
                pl_list.append([email,str(name),leave_reason,start_date,end_date])

        # Merging all the lists into 1 single combined dictionary
        combined[day_key] = {"Training": training_list,"Duties": duty_list, "Priority Leave": pl_list}

    # Read the excel data stored in the combined dictionary to determine if there are clashes
    clash_dict = {}
    for date,value in combined.items():
        doc_list = []
        clash_doc_list = []
        full_list = []
        clash_list = []
        for activity,lists in value.items():
            for each in lists:
                if each[0] not in doc_list:
                    doc_list.append(each[0])
                else:
                    if each[0] not in clash_doc_list:
                        clash_doc_list.append(each[0])
                each.append(activity)
                full_list.append(each)
        
        # If there are doctors having schedule clashes, start populating the clash_dict
        if len(clash_doc_list) != 0:
            unique_doc_list = []      
            for c in full_list:
                activity_type_list = []   
                if c[0] in clash_doc_list and c[0] not in unique_doc_list:
                    clash_list.append(c)
                    unique_doc_list.append(c[0])
                    activity_type_list.append(c[5])
                    for i in full_list:
                        if i[0] == c[0] and i[5] not in activity_type_list:
                            activity_type_list.append(i[5])
                    if date in clash_dict:
                        clash_dict[date].append([c[0],c[1],activity_type_list])
                    elif date not in clash_dict:
                        clash_dict[date] = [[c[0],c[1],activity_type_list]]
    
    # If there are clashes, return the clashes dictionary
    if clash_dict:     
        return clash_dict       # Format: {date:[ [email,name,[Training,Duty,Priority Leave]], [email,name,[Training,Duty,Priority Leave]]], date: ...}
    # If there are no clashes, return False
    else:
        return 'False'

def exportScheduleS():
    """
    Exports senior doctors timetable as CSV. 

    :parameters: timetable data from *TempS* table
    :return: *scheduleS.xlsx*
    """   

    # Establish connection to DB
    conn, cur = create_connection()

    # Query from Temp Table in DB and put into a Pandas Dataframe
    script = """SELECT * FROM TempS;"""
    cur.execute(script)
    columns = [desc[0] for desc in cur.description]
    data = cur.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    # Writing the Dataframe data into an excel file and saving the excel file
    writer = pd.ExcelWriter('scheduleS.xlsx')
    df.to_excel(writer, sheet_name='SeniorSchedule')
    writer.save()

    # Close connection to DB
    close_connection(conn, cur)

    return 'True'

def exportScheduleJ():
    """
    Exports junior doctors timetable as CSV. 

    :parameters: timetable data from *TempJ* table
    :return: *scheduleJ.xlsx*
    """   

    # Establish connection to DB
    conn, cur = create_connection()

    # Query from Temp Table in DB and put into a Pandas Dataframe
    script = """SELECT * FROM TempJ;"""
    cur.execute(script)
    columns = [desc[0] for desc in cur.description]
    data = cur.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    # Writing the Dataframe data into an excel file and saving the excel file
    writer = pd.ExcelWriter('scheduleJ.xlsx')
    df.to_excel(writer, sheet_name='JuniorSchedule')
    writer.save()

    # Close connection to DB
    close_connection(conn, cur)

    return 'True'

def email_json(start_dateA,end_dateA):
    """
    Extracts FormSG emails from Outlook and updates the *CallRequest* and *LeaveApplication* tables with these data. 

    :parameters: start date and end date which specify emails to extract. 
    """   

    pythoncom.CoInitialize()
    outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
    pythoncom.CoInitialize()
    root_folder = outlook.Folders.Item(1)   

    ### note: change the folder name 'test' to the one in TTSH
    test_folder = root_folder.Folders['test']
    emails = test_folder.Items
 
    email_list = []
    email_body_list = []
    needed_emails = []
    check_latest = []

    start_dateA = datetime.strptime(start_dateA, '%Y-%m-%d').strftime('%Y-%m-%d')
    start_date = start_dateA.split('-')
    start_date_mth, start_date_year = start_date[1], start_date[0]

    end_dateA = datetime.strptime(end_dateA, '%Y-%m-%d').strftime('%Y-%m-%d')
    end_date = end_dateA.split('-')
    end_date_mth, end_date_year = end_date[1], end_date[0]
    
    dates = [start_dateA, end_dateA]
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    myResult = OrderedDict(((start + timedelta(_)).strftime(r"%b,%Y"), None) for _ in range((end - start).days)).keys()
    months_between = list(myResult)

    dates = [start_dateA, end_dateA]
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    myResult = OrderedDict(((start + timedelta(_)).strftime(r"%b,%Y"), None) for _ in range((end - start).days)).keys()
    months_between = list(myResult)

    for email in emails: 
        ### email subjects
        emailSubject = email.Subject
        emailSubject = str(emailSubject)

        ### email body
        emailBody = email.Body
        emailBody = emailBody.encode('ascii', 'ignore')
        emailBody = str(emailBody)
        
        ### email received date
        emailReceivedDate = email.SentOn
        emailReceivedDateStr = str(email.SentOn)
        
        formatJson = emailBody.split()
        formatJson = ''.join(formatJson)
        start = formatJson.find('--StartofJSON--') + 15
        end = formatJson.find('--EndofJSON--')
        myJson = formatJson[start:end]
        myQuestion = myJson.split('{"question":')
     
        myRequestMonth = ''
    
        ### get the questions and answers
        for i in myQuestion:
            myAnswerPosition = i.find('"answer"')
            myQuestion = i[1:myAnswerPosition-2]            
            
            if r'r\n\r' in myQuestion:
                myQuestion = myQuestion.replace(r'r\n\r','')
            
            myAns = i[myAnswerPosition:]
            myAnswerPosition = myAns.find('},')
            myAns = myAns[:myAnswerPosition]
            myAnswerPosition = myAns.find('"answer":"') + 10
            myAns = myAns[myAnswerPosition:]
            myAns = myAns[:len(myAns)-1]
            myAns = str(myAns)
            
            myAns = myAns.replace(r'\r','')
            myAns = myAns.replace(r'\n','')
            myAns = myAns.replace('}','')
            myAns = myAns.replace(']','')
            myAns = myAns.replace('"','')
            
            if r'\r\n\r' in myAns:
                myAns = myAns[:len(myAns)-9]
            
            if 'RequestMonth' in myQuestion:
                myRequestMonth = myAns

            if 'Email' in myQuestion:
                emailSenderAddress = myAns.split('<')
                emailSenderAddress = emailSenderAddress[0]
                emailSender = myAns.split('<')
                emailSender = emailSender[0]
                   
            case2 = {
                "question":myQuestion,
                "answer":myAns
            }

            email_body_list.append(case2)
  
        myRequestMonthList = myRequestMonth.split(',')
        request_year_name = myRequestMonthList[1]  
        request_month_name = myRequestMonthList[0]
        if len(request_month_name) > 3:
            request_month_name = request_month_name[:3]
            myRequestMonth = request_month_name + ',' + request_year_name
        month_number = strptime(request_month_name,'%b').tm_mon
        month_number = str(month_number)
        
        if myRequestMonth in months_between:
            case = [emailReceivedDate, emailSenderAddress, request_year_name, month_number]
            check_latest.append(case)
            
            case2 = {
                "Subject": emailSubject,
                "Body":email_body_list,
                "SenderEmail": emailSenderAddress,
                "SenderName":emailSender,
                "Date":myRequestMonth,
                "ReceivedDate":emailReceivedDate
            }
            
            ### note: don't delete this empty list  --> it is needed to prevent appending from old emails
            email_body_list = []
            
            email_list.append(case2)
            
            new_email_body = email_list[(len(email_list))-1]['Body']
            
            myQnA = []
            leaveRequest = []
            callRequest = []
            otherRequest = []
            
            for thread in new_email_body:
                if "LeaveRequest" in thread['question']:
                    leaveRequest.append(thread['answer'])
                elif "CallRequests" in thread['question']:
                    callRequest.append(thread['answer'])
            
            for thread in new_email_body:
                if "LeaveRequest" in thread['question']:
                    pass
                elif "CallRequests" in thread['question']:
                    pass
                else:
                    myQnA.append(thread)
            
            myQnA.append({"question":"leaveRequest", "answer":leaveRequest})
            myQnA.append({"question":"callRequest", "answer":callRequest})
            
            needed_emails.append([
                myQnA,
                email_list[len(email_list)-1]['Subject'], 
                email_list[len(email_list)-1]['SenderEmail'], 
                email_list[len(email_list)-1]['SenderName'], 
                email_list[len(email_list)-1]['Date'],
                emailReceivedDate
            ]) 
            
    delete_index = []  

    for i in range(len(needed_emails)):
        receivedDate = str(needed_emails[i][5])
        receivedDate = receivedDate.split(' ')
        receivedDate_date = receivedDate[0]
        receivedDate_date = dateutil.parser.parse(receivedDate_date)
        receivedDate_time = receivedDate[1]
        receivedDate_time = receivedDate_time[:-6]
        receivedDate_time = receivedDate_time.split(':')

        senderEmail = needed_emails[i][2]
        
        for j in range(len(check_latest)):
            
            check_receivedDate = str(check_latest[j][0])
            check_receivedDate = check_receivedDate.split(' ')
            check_receivedDate_date = check_receivedDate[0]
            check_receivedDate_date = dateutil.parser.parse(check_receivedDate_date)
            check_receivedDate_time = check_receivedDate[1]
            check_receivedDate_time = check_receivedDate_time[:-6]
            check_receivedDate_time = check_receivedDate_time.split(':')

            check_senderEmail = check_latest[j][1]
            
            if senderEmail == check_senderEmail:
                
                receivedDate_time_hr = int(receivedDate_time[0])
                receivedDate_time_min = int(receivedDate_time[1])
                receivedDate_time_sec = int(receivedDate_time[2])
                
                check_receivedDate_time_hr = int(check_receivedDate_time[0])
                check_receivedDate_time_min = int(check_receivedDate_time[1])
                check_receivedDate_time_sec = int(check_receivedDate_time[2])
                       
                if receivedDate_date == check_receivedDate_date:              
                    if receivedDate_time_hr == check_receivedDate_time_hr:
                        if receivedDate_time_min == check_receivedDate_time_min:
                            if receivedDate_time_sec < check_receivedDate_time_sec:
                                delete_index.append([i])
                            
                        elif receivedDate_time_min < check_receivedDate_time_min:
                            delete_index.append([i])
                        
                    elif receivedDate_time_hr < check_receivedDate_time_hr:
                        delete_index.append([i])
                    
                elif receivedDate_date < check_receivedDate_date:
                    delete_index.append([i])

    sorted_delete_index = []
    for i in delete_index:
        if i not in sorted_delete_index:
            sorted_delete_index.append(i)
    
    for i in reversed(sorted_delete_index):
        needed_emails.pop(i[0])
      
    conn, cur = create_connection() 
    # Delete any existing data from CallRequest table from DB
    cur.execute("""DELETE FROM CallRequest;""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'CallRequest';""")
    conn.commit()

    # Delete any existing data from LeaveApplication table from DB
    cur.execute("""DELETE FROM LeaveApplication;""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'LeaveApplication';""")
    conn.commit()
    
    for i in range(len(needed_emails)):

        myEmail = needed_emails[i][2]

        # Obtain doctor's name from Roster table in DB using submitted FormSG email address
        cur.execute("""SELECT name FROM Roster WHERE email = ?;""",(myEmail,))
        roster_results = cur.fetchone()
        myName = roster_results[0]
        # myName = needed_emails[i][3]
        
        myStartDate = start_dateA
        myEndDate = end_dateA
        
        for j in needed_emails[i][0]:
            if j['question'] == 'leaveRequest':
                for k in j['answer']:
                    mySplit = k.split(',')
                    
                    leaveStartDate = mySplit[0]
                    leaveEndDate = mySplit[1]
                    
                    if leaveStartDate != '':
                        leaveStartDate_List = leaveStartDate.split('/')
                        L_sDate_day = leaveStartDate_List[0]
                        L_sDate_mth = leaveStartDate_List[1]
                        
                        if len(leaveStartDate_List[0]) == 1:
                            L_sDate_day = '0' + L_sDate_day
                        if len(leaveStartDate_List[1]) == 1:
                            L_sDate_mth = '0' + L_sDate_mth
                            
                        L_sDate = request_year_name + '-' + L_sDate_mth + '-' + L_sDate_day
                    
                    if leaveEndDate != '':
                        leaveEndDate_List = leaveEndDate.split('/')                   
                        L_eDate_day = leaveEndDate_List[0]
                        L_eDate_mth = leaveEndDate_List[1]
                        
                        if len(leaveEndDate_List[0]) == 1:
                            L_eDate_day = '0' + L_eDate_day
                        if len(leaveEndDate_List[1]) == 1:
                            L_eDate_mth = '0' + L_eDate_mth
                        
                        L_eDate = request_year_name + '-' + L_eDate_mth + '-' + L_eDate_day
                    
                    if mySplit[0] != '' and mySplit[1] != '' and mySplit[2] != '' and mySplit[3] != '':
                                               
                        cur.execute("""INSERT OR IGNORE INTO LeaveApplication(email, name, start_date, end_date, duration, leave_type, remark) 
                           VALUES
                           (?, ?, ?, ?, ?, ?, ?)
                           ;""",(myEmail,myName,L_sDate,L_eDate,mySplit[2],mySplit[3],mySplit[4]))
                                                  
                        conn.commit()
           
            if j['question'] == 'callRequest':
                C_Date = ''
                for m in j['answer']:
                    mySplit = m.split(',')
                    if mySplit[0] != '':
                        C_Date = mySplit[0]
                        C_Date = C_Date.split('/')
                        if len(C_Date[0]) == 1:
                            C_Date[0] = '0' + C_Date[0]
                        if len(C_Date[1]) == 1:
                            C_Date[1] = '0' + C_Date[1]
                        C_Date = request_year_name + '-' + C_Date[1] + '-' + C_Date[0]
                    
                    if mySplit[0] != '' and mySplit[1] != '':    
                        cur.execute("""INSERT OR IGNORE INTO CallRequest(email, name, date, request_type, remark) 
                            VALUES
                            (?, ?, ?, ?, ?)
                            ;""",(myEmail,myName,C_Date,mySplit[1],mySplit[2]))
                           
                        conn.commit()
                        
    close_connection(conn, cur) 
    return needed_emails

def produce_doctor_dictionary(doc_name,number_of_rows,df):
    """
    Produces doctor dictionary for past schedule.

    :parameters: doctor name, number of rows, dataframe
    :return: nested dictionary containing doctor name, date, activity and remark. 
    For example: 
    {"Dr Lee": {"01-05-2021 Saturday": {"Off": ""}}}
    """   
    one_doc_activity_per_month = {}
    counter = 2

    # Extract data and put into a dictionary
    for each_doc in doc_name:
        each_doc_month_schedule = {}
        
        for i in range(number_of_rows):
            per_day_activity = {}       # {date : activity_dictionary}
            for col in df.columns:
                if col == each_doc:
                    activity_string = df.iloc[i][counter]
                    str_element = activity_string.replace("'",'"')
                    activity_dict = json.loads(str_element)
                    per_day_activity[df.iloc[i][1]] = activity_dict

                    if each_doc in each_doc_month_schedule:
                        each_doc_month_schedule[each_doc].update(per_day_activity)
                    if each_doc not in each_doc_month_schedule:
                        each_doc_month_schedule[each_doc] = per_day_activity

        one_doc_activity_per_month[each_doc] = each_doc_month_schedule[each_doc]
        counter += 1

    return one_doc_activity_per_month
