import pandas as pd     #make sure to pip install pandas    Also pip install xlrd   Also pip install openpyxl
import datetime
from helperFunctions import *

def readRoster():
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Roster table from DB
    cur.execute("""DELETE FROM Roster""")
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
        for each_skill in skills:
            cur.execute("""INSERT OR IGNORE INTO Skills(email, skill)  
                    VALUES (?, ?);""", (email,each_skill))
            conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)

    return roster_dict

def readTraining():
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Training table from DB
    cur.execute("""DELETE FROM Training""")
    conn.commit()

    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Training')
    # print(df)

    '''
    Structure: training_dict = {
                email 1:[name, training, start date, end date], 
                email 2:[name, training, start date, end date],
                ...
            }
    '''
    training_dict = {}

    index = df.index
    number_of_rows = len(index)
    # print(number_of_rows)
    # print()

    # Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        training = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        training_dict[email] = [name,training,start_date,end_date]

        cur.execute("""INSERT OR IGNORE INTO Training(email, name, training, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,name,training,start_date,end_date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    return training_dict

def readDuties():
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from Duty table from DB
    cur.execute("""DELETE FROM Duty""")
    conn.commit()

    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Duties')

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

    # Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        duty_name = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        duties_dict[email] = [name,duty_name,start_date,end_date]
        cur.execute("""INSERT OR IGNORE INTO Duty(email, name, duty_name, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,name,duty_name,start_date,end_date))
        conn.commit()
    
    # Close connection to DB
    close_connection(conn, cur)

    # print(duties_dict)
    return duties_dict

def readPl():
    # Establish connection to DB
    conn, cur = create_connection() 

    # Delete any existing data from PriorityLeave table from DB
    cur.execute("""DELETE FROM PriorityLeave""")
    conn.commit()

    df = pd.read_excel (r'sample_excel.xlsx', sheet_name='Priority Leave')

    '''
    Structure: pl_dict = {
                email 1:[name, leave reason, start date, end date], 
                email 2:[name, leave reason, start date, end date],
                ...
            }
    '''
    pl_dict = {}

    index = df.index
    number_of_rows = len(index)

    # Extract data and put into a dictionary
    for i in range(number_of_rows):
        email = df.iloc[i][0]
        name = df.iloc[i][1]
        leave_reason = df.iloc[i][2]
        start_date = pd.to_datetime(df.iloc[i][3]).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(df.iloc[i][4]).strftime('%Y-%m-%d')
        pl_dict[email] = [name,leave_reason,start_date,end_date]
        cur.execute("""INSERT OR IGNORE INTO PriorityLeave(email, name, reason, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?);""", (email,name,leave_reason,start_date,end_date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    return pl_dict

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

# A = readRoster()
# print(A)
# print()

# B = readTraining()
# print(B)
# print()

# C = readDuties()
# print(C)
# print()

# D = readPl()
# print(D)
# print()

# E = readPh()
# print(E)
# print()