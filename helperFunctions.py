import sqlite3, datetime, json, pyodbc, dateutil.parser
import pandas as pd
from sqlite3 import Error
from datetime import date, timedelta, datetime
from win32com.client import Dispatch

# Create a database connection to a SQLite database
def create_connection():
    try:
        conn = sqlite3.connect('Database/database.db')
        cur = conn.cursor()
        return conn, cur
    except Error as e:
        # print(e)
        return (str(e))

# Close a database connection to a SQLite database
def close_connection(conn, cur):
    try:
        cur.close()
        conn.close()
    except Error as e:
        # print(e)
        return (str(e))

# Checks whether a date is a weekday or weekend
def check_weekend(date):
    weekend = {5: "Saturday", 6: "Sunday"}

    # Check what is the value for the date
    num = date.weekday()    # returns a value from 0-6 where 0 is Monday and 6 is Sunday
    if num in weekend:
        return 'True'
    else:
        return 'False'

# Checks the day of the date
def check_day(date):
    week = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    
    # Check what is the value for the date
    num = date.weekday()    # returns a value from 0-6 where 0 is Monday and 6 is Sunday
    return week[num]

# Check public holiday eve
def check_eveph(date,e):
    dateo = datetime.strptime(date, '%Y-%m-%d').date()
    eveo = dateo + timedelta(days=1)
    eves = eveo.strftime("%Y-%m-%d")
    if eves in e:
        return True

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
        # # If not must use the below 2 lines to convert the format
        # start_date = datetime.strptime(start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
        # end_date = datetime.strptime(end_date, '%d-%m-%Y').strftime('%Y-%m-%d')

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
            
            if not_met:
                temp = {}
                temp[day_key] = not_met
        
            if day_key in dict_notmet:
                dict_notmet[day_key].update(not_met)
            elif day_key not in dict_notmet:
                dict_notmet[day_key] = not_met

        # Dictionary to store the overall days and constraints that are not met
        # dict_notmet[day_key] = not_met

        # Close connection to DB
        close_connection(conn, cur)

        # Returns the failed constraints dictionary in the form: {date:[constraint1,constraint2],date:[constraint1],...}
        if dict_notmet:
            return dict_notmet
        # Return True when constraints met
        else:
            return 'True'
    
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
    # df.rename(columns=df.iloc[0], inplace = True)
    # df.drop([0], inplace = True)

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
        roster_dict[email] = [str(name),first_position,second_position,posting,skills,mo_type]

        # Insert values into Roster table in DB
        cur.execute("""INSERT OR IGNORE INTO Roster(email, name, first_position, second_position, posting, type) 
                VALUES (?, ?, ?, ?, ?, ?);""", (email,str(name),first_position,second_position,posting,mo_type))
        conn.commit()

        # If a new staff joins the department, insert a fresh data column into Points table for that new staff; Old staff values are untouched
        cur.execute("""INSERT OR IGNORE INTO Points(email, '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12') 
                VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);""", (email,))
        conn.commit()

        # Insert the multiple skills each staff has into Skill table in DB
        for each_skill in skills:
            cur.execute("""INSERT OR IGNORE INTO Skill(email, skill)  
                    VALUES (?, ?);""", (email,each_skill))
            conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)

    # print(roster_dict)
    return roster_dict

# Read Duty from excel file
def readDuties(query_start_date,query_last_date):
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Duty table from DB
    cur.execute("""DELETE FROM Duty""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'Duty';""")
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

    # If not must use the below 2 lines to convert the format
    # query_start_date = datetime.strptime(query_start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
    # query_last_date = datetime.strptime(query_last_date, '%d-%m-%Y').strftime('%Y-%m-%d')
    # print(query_start_date)
    # print(query_last_date)
    # print()
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
        temp[start_date] = [str(name),duty_name,end_date]
        #print(temp)

        if email in duties_dict:
            duties_dict[email].update(temp)
        if email not in duties_dict:
            duties_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO Duty(email, name, duty_name, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,str(name),duty_name,start_date,end_date))
        conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)

    # print(duties_dict)
    return duties_dict

# Read Training from excel file
def readtraining(query_start_date,query_last_date):
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM Training""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'Training';""")
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

    # If not must use the below 2 lines to convert the format
    # query_start_date = datetime.strptime(query_start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
    # query_last_date = datetime.strptime(query_last_date, '%d-%m-%Y').strftime('%Y-%m-%d')

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
        temp[start_date] = [str(name),training,end_date]
        #print(temp)

        if email in training_dict:
            training_dict[email].update(temp)
        if email not in training_dict:
            training_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO Training(email, name, training, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,str(name),training,start_date,end_date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    # print(training_dict)
    return training_dict

# Read Priority Leave from excel file
def readpleave(query_start_date,query_last_date):
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM PriorityLeave""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'PriorityLeave';""")
    conn.commit()

    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Priority Leave')
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

    # If not must use the below 2 lines to convert the format
    # query_start_date = datetime.strptime(query_start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
    # query_last_date = datetime.strptime(query_last_date, '%d-%m-%Y').strftime('%Y-%m-%d')

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
        temp[start_date] = [str(name),leave_reason,end_date]
        #print(temp)

        if email in pleave_dict:
            pleave_dict[email].update(temp)
        if email not in pleave_dict:
            pleave_dict[email] = temp
        
        cur.execute("""INSERT OR IGNORE INTO PriorityLeave(email, name, reason, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,str(name),leave_reason,start_date,end_date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    # print(pleave_dict)
    return pleave_dict

# Read Call Request from DB
def readCallRequest(doc_list,query_start_date, query_last_date):
    # Establish connection to DB
    conn, cur = create_connection()

    # Fetch the call request data stored in DB
    cur.execute("""SELECT * FROM CallRequest WHERE date >= ? AND date <= ?;""",
    (query_start_date, query_last_date))
    cr_results = cur.fetchall()

    '''
    Structure: cr_dict = {
                email 1:[name, request type, remark], 
                email 2:[name, request type, remark],
                ...
            }
    '''

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
    # print(cr_dict)
    return cr_dict

# Read Leave Application from DB
def readLeaveApplication(doc_list,query_start_date, query_last_date):
    # Establish connection to DB
    conn, cur = create_connection()

    # Fetch the leave application data stored in DB
    cur.execute("""SELECT * FROM LeaveApplication WHERE start_date >= ? INTERSECT SELECT * FROM LeaveApplication WHERE start_date <= ? 
        UNION SELECT * FROM LeaveApplication WHERE end_date <= ? INTERSECT SELECT * FROM LeaveApplication WHERE end_date >= ?;""",
    (query_start_date, query_last_date, query_last_date, query_start_date))
    la_results = cur.fetchall()

    '''
    Structure: la_dict = {
                email 1:[name, request type, remark], 
                email 2:[name, request type, remark],
                ...
            }
    '''

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

# Read Public Holiday from excel file
def readPh():
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

    # print(ph_dict)
    return ph_dict

# Check for clashes in the excel file
def clashes(query_start_date,query_last_date):
    # Format the start and end dates of the schedule to appropriate format
    # query_start_date = datetime.strptime(query_start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
    # query_last_date = datetime.strptime(query_last_date, '%d-%m-%Y').strftime('%Y-%m-%d')
    
    # Combined dictionary to store all the data from the excel file for the scheduled dates
    combined = {}
    
    # Reading and storing the excel file data
    sdate = datetime.strptime(query_start_date, '%Y-%m-%d').date()   # start date
    edate = datetime.strptime(query_last_date, '%Y-%m-%d').date()   # end date
    delta = edate - sdate       # as timedelta
    for date_diff in range(delta.days + 1):
        day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
        day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)
        display_day = check_day(day) + " " + day.strftime("%d-%m-%Y")   # Sunday 31-12-2020 (string format)
        
        # Read Training from excel and store inside training_list
        training_list = []
        df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Training')
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
        df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Duties')
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
        df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Priority Leave')
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

# Export TempS table into excel file
def exportScheduleS():
    # Establish connection to DB
    conn, cur = create_connection()

    # Query from Temp Table in DB and put into a Pandas Dataframe
    script = """SELECT * FROM TempS;"""
    cur.execute(script)
    columns = [desc[0] for desc in cur.description]
    data = cur.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    # Writing the Dataframe data into an excel file and saving the excel file
    writer = pd.ExcelWriter('schedule.xlsx')
    df.to_excel(writer, sheet_name='SeniorSchedule')
    writer.save()

    # Close connection to DB
    close_connection(conn, cur)

    return 'True'

# Export TempJ table into excel file
def exportScheduleJ():
    # Establish connection to DB
    conn, cur = create_connection()

    # Query from Temp Table in DB and put into a Pandas Dataframe
    script = """SELECT * FROM TempJ;"""
    cur.execute(script)
    columns = [desc[0] for desc in cur.description]
    data = cur.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    # Writing the Dataframe data into an excel file and saving the excel file
    writer = pd.ExcelWriter('schedule.xlsx')
    df.to_excel(writer, sheet_name='JuniorSchedule')
    writer.save()

    # Close connection to DB
    close_connection(conn, cur)

    return 'True'

# Retrieve from email
def email_json(start_dateA,end_dateA):

    outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
    root_folder = outlook.Folders.Item(1)   

    ### customised folder name = 'test'
    test_folder = root_folder.Folders['test']
    emails = test_folder.Items

    email_list = []
    email_body_list = []    # list for email body
    needed_emails = []
    latest_emails = []
    check_latest = []

    count = 0

    start_dateA = datetime.strptime(start_dateA, '%Y-%m-%d').strftime('%Y-%m-%d')
    start_date = start_dateA.split('-')
    start_date_mth, start_date_year = start_date[1], start_date[0]

    end_dateA = datetime.strptime(end_dateA, '%Y-%m-%d').strftime('%Y-%m-%d')
    end_date = end_dateA.split('-')
    end_date_mth, end_date_year = end_date[1], end_date[0]

    for email in emails: 
        
        ### email subjects
        emailSubject = email.Subject
        emailSubject = str(emailSubject)
              
        ### sender name
        emailSender = email.Sender
        emailSender = str(emailSender)
        
        ### sender email address
        emailSenderAddress = email.Sender.Address
        emailSenderAddress = str(emailSenderAddress)

        ### email body
        emailBody = email.Body
        emailBody = emailBody.encode('ascii', 'ignore')
        emailBody = str(emailBody)
        
        ### email received date
        emailReceivedDate = email.SentOn
        emailReceivedDateStr = str(email.SentOn)
        
        ### filter the JSON
        formatJson = emailBody.split()
        formatJson = ''.join(formatJson)
        start = formatJson.find('--StartofJSON--') + 15
        end = formatJson.find('--EndofJSON--')
        myJson = formatJson[start:end]
        myQuestion = myJson.split('{"question":')
        
        count += 1
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
                   
            case2 = {
                "question":myQuestion,
                "answer":myAns
            }
                  
            ### save all question & answer in the list called email_body_list
            email_body_list.append(case2)
        
        myRequestMonthList = myRequestMonth.split(',')
        request_year_name = myRequestMonthList[1]  
        request_month_name = myRequestMonthList[0]
        if len(request_month_name) > 3:
            request_month_name = request_month_name[:3]
        month_number = datetime.strptime(request_month_name,'%b').tm_mon
        month_number = str(month_number)
        
        ### check if request month is within start date and end date         
        ### assumption: start date & end date are in the same month same year
        ### thus, we cannot accept start date this year, end date next year
        if int(start_date_year) <= int(request_year_name) <= int(end_date_year):
            if int(start_date_mth) <= int(month_number) <= int(end_date_mth):
                
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
                
                ### to prevent appending from old emails
                email_body_list = []

                email_list.append(case2)

                new_email_body = email_list[count-1]['Body']
                
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
                    myQnA,      # "Email"
                    email_list[count-1]['Subject'],         # "Subject"
                    email_list[count-1]['SenderEmail'],     # "SenderEmail"
                    email_list[count-1]['SenderName'],      # "SenderName"
                    email_list[count-1]['Date'],            # "RequestMonth"
                    emailReceivedDate                       # "ReceivedDate"
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
                            if receivedDate_time_sec > check_receivedDate_time_sec:
                                delete_index.append([i])
                            
                        elif receivedDate_time_min > check_receivedDate_time_min:
                            delete_index.append([i])
                        
                    elif receivedDate_time_hr > check_receivedDate_time_hr:
                        delete_index.append([i])
                    
                elif receivedDate_date > check_receivedDate_date:
                    delete_index.append([i])

    sorted_delete_index = []
    for i in delete_index:
        if i not in sorted_delete_index:
            sorted_delete_index.append(i)

    final_emails = []

    for i in reversed(sorted_delete_index):
        needed_emails.pop(i[0])
    
    ### Establish connection to DB
    conn, cur = create_connection()

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM LeaveApplication""")
    conn.commit()

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM CallRequest""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'LeaveApplication';""")
    conn.commit()

    # Reset the auto incremental numbers when each month's schedule is being generated
    cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'CallRequest';""")
    conn.commit()
        
    for i in range(len(needed_emails)):       
        myStartDate = start_dateA
        myEndDate = end_dateA
        
        myEmail = needed_emails[i][2]
        myName = needed_emails[i][3]
        
        for j in needed_emails[i][0]:
            if j['question'] == 'leaveRequest':
                for k in j['answer']:
                    mySplit = k.split(',')                    
                    if mySplit[0] != '' and mySplit[1] != '' and mySplit[2] != '' and mySplit[3] != '':                       
                        cur.execute("""INSERT OR IGNORE INTO LeaveApplication(email, name, start_date, end_date, duration, leave_type, remark) 
                           VALUES
                           (?, ?, ?, ?, ?, ?, ?)
                           ;""",(myEmail,myName,mySplit[0],mySplit[1],mySplit[2],mySplit[3],mySplit[4]))
                        conn.commit()
                    
            if j['question'] == 'callRequest':
                for m in j['answer']:
                    mySplit = m.split(',')
                        
                    if mySplit[0] != '' and mySplit[1] != '':
                        cur.execute("""INSERT OR IGNORE INTO CallRequest(email, name, date, request_type, remark) 
                            VALUES
                            (?, ?, ?, ?, ?)
                            ;""",(myEmail,myName,mySplit[0],mySplit[1],mySplit[2]))
                        conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)
    
    return needed_emails

# # Export ICU1Duty table into excel file
# def exportICU1Duty():
#     # Establish connection to DB
#     conn, cur = create_connection()

#     # Query from ICU1Duty Table in DB and put into a Pandas Dataframe
#     script = """SELECT * FROM ICU1Duty;"""
#     cur.execute(script)
#     columns = [desc[0] for desc in cur.description]
#     data = cur.fetchall()
#     df = pd.DataFrame(list(data), columns=columns)

#     # Writing the Dataframe data into an excel file and saving the excel file
#     writer = pd.ExcelWriter('ICU1.xlsx')
#     df.to_excel(writer, sheet_name='ICU1Duty')
#     writer.save()

#     # Close connection to DB
#     close_connection(conn, cur)

#     return 'True'

# # Export ICU2Duty table into excel file
# def exportICU2Duty():
#     # Establish connection to DB
#     conn, cur = create_connection()

#     # Query from ICU2Duty Table in DB and put into a Pandas Dataframe
#     script = """SELECT * FROM ICU2Duty;"""
#     cur.execute(script)
#     columns = [desc[0] for desc in cur.description]
#     data = cur.fetchall()
#     df = pd.DataFrame(list(data), columns=columns)

#     # Writing the Dataframe data into an excel file and saving the excel file
#     writer = pd.ExcelWriter('ICU2.xlsx')
#     df.to_excel(writer, sheet_name='ICU2Duty')
#     writer.save()

#     # Close connection to DB
#     close_connection(conn, cur)

#     return 'True'

# # Export Points table into excel file
# def exportPoints():
#     # Establish connection to DB
#     conn, cur = create_connection()

#     # Query from Points Table in DB and put into a Pandas Dataframe
#     script = """SELECT * FROM Points;"""
#     cur.execute(script)
#     columns = [desc[0] for desc in cur.description]
#     data = cur.fetchall()
#     df = pd.DataFrame(list(data), columns=columns)

#     # Writing the Dataframe data into an excel file and saving the excel file
#     writer = pd.ExcelWriter('points.xlsx')
#     df.to_excel(writer, sheet_name='Points')
#     writer.save()

#     # Close connection to DB
#     close_connection(conn, cur)

#     return 'True'