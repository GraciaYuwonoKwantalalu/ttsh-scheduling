import sqlite3
import holidays
import json
import pandas as pd
from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response, request
from datetime import date, timedelta, datetime
from helperFunctions import create_connection, close_connection, check_weekend, check_day, check_month_num, check_eveph, is_constraint_met, readRoster, readDuties, readtraining, readpleave, readCallRequest, readLeaveApplication, readPh, clashes, exportScheduleS, exportScheduleJ, email_json, produce_doctor_dictionary
from lpFunction import run_lp
from pprint import pprint
from win32com import client
import win32api
import pythoncom
import win32com.client
import xlsxwriter
import os
from itertools import islice
import itertools
import string

# import datetime
# from win32com.client import Dispatch

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "hello"

### PAGES ###
# Display the main page when user first loads the Flask app at localhost:5000
# home
@app.route('/', methods=["POST", "GET"])
@app.route('/home')
def home(): 
    constraints = retrieve_constraints()
    return render_template("home.html", constraints=constraints)

# timetable page  
@app.route('/timetable', methods=["GET"])
def timetable():    
    timetable_dict = retrieve_timetable()

    innerKey2 = list(timetable_dict.keys())[0]
    innerValue2 = timetable_dict[innerKey2]
    innerKey3 = list(innerValue2.keys())[0]
    innerValue3 = innerValue2[innerKey3]

    return render_template("timetable.html", timetable_dict=timetable_dict, innerValue3=innerValue3)

# past timetable page
@app.route('/past_timetable', methods=["GET"])
def past_timetable():    
    # Reading from Senior Doctor file
    df1 = pd.read_excel (r'scheduleS.xlsx', sheet_name='SeniorSchedule')
    
    index1 = df1.index
    number_of_rows1 = len(index1)

    # Get the senior doctor names in 1 list
    senior_doc_name = []
    for col in df1.columns:
        senior_doc_name.append(col)
    senior_doc_name.pop(0)
    senior_doc_name.pop(0)

    # Obtain the senior doctor dictionary
    senior_doc_dict = produce_doctor_dictionary(senior_doc_name,number_of_rows1,df1)
    
    # Reading from Junior Doctor file
    df2 = pd.read_excel (r'scheduleJ.xlsx', sheet_name='JuniorSchedule')

    index2 = df2.index
    number_of_rows2 = len(index2)

    # Get the junior doctor names in 1 list
    junior_doc_name = []
    for col in df2.columns:
        junior_doc_name.append(col)
    junior_doc_name.pop(0)
    junior_doc_name.pop(0)
    
    # Obtain the junior doctor dictionary
    junior_doc_dict = produce_doctor_dictionary(junior_doc_name,number_of_rows2,df2)

    # Put everything in format for front-end: {'S': senior_doc_dict, 'J': junior_doc_dict}      
    timetable_dict = {'S': senior_doc_dict, 'J': junior_doc_dict}

    innerKey2 = list(timetable_dict.keys())[0]
    innerValue2 = timetable_dict[innerKey2]
    innerKey3 = list(innerValue2.keys())[0]
    innerValue3 = innerValue2[innerKey3]
    
    return render_template("past_timetable.html", timetable_dict=timetable_dict, innerValue3=innerValue3)

# calls page  
@app.route('/calls')
def calls():    
    call_summary_dict = retrieve_call_summary()
    call_summary_df = pd.DataFrame.from_dict(call_summary_dict)
    return render_template("calls.html", call_summary_dict=call_summary_dict, call_summary_tables=[call_summary_df.to_html(classes='data')])

# icu duties page
@app.route('/icu_duties')
def icu_duties():
    icu1 = retrieve_icu_1_table()
    icu2 = retrieve_icu_2_table()
    return render_template("icu_duties.html", icu1=icu1, icu2=icu2)

# points page
@app.route('/points')
def points():
    overall_summary = retrieve_points_summary()
    return render_template("points.html", overall_summary=overall_summary)

### DOWNLOAD ###
# download timetable as pdf
@app.route('/download_pdf')
def download_timetable():
    conn, cur = create_connection()
    ### Junior
    script = """SELECT * FROM TempJ;"""
    cur.execute(script)
    columns = [desc[0] for desc in cur.description]
    dataJ = cur.fetchall()

    data_new2 = []
    for i in dataJ:
        myTuple = ()
        data_new_tuple2 = [i[0]]
    
        for j in i[1:]:
            j = j.split(':')        
            j = j[0][2:]
            j = j[:-1]
            data_new_tuple2.append(j)
        myTuple = tuple(data_new_tuple2)
        data_new2.append(myTuple)
        myTuple = ()
        data_new_tuple2 = []
        
    df = pd.DataFrame(list(data_new2), columns=columns)
    
    writer = pd.ExcelWriter("schedule_J_pdf.xlsx", engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Junior')
    workbook  = writer.book
    worksheet = writer.sheets['Junior']

    # Add some cell formats.
    format1 = workbook.add_format({'num_format': '#,##0.00'})
    format2 = workbook.add_format({'num_format': '0%'})

    # Set the column width and format.
    worksheet.set_column('B:B', 18, format1)
    # Set the format but not the column width.
    worksheet.set_column('C:C', None, format2)
    writer.save()    

    input_file = r'C:\flask_app\schedule_J_pdf.xlsx'
    output_file = r'C:\flask_app\schedule_J_pdf.pdf'
    
    pythoncom.CoInitialize()
    app = win32com.client.Dispatch("Excel.Application")
    app.Interactive = False
    app.Visible = False
    Workbook = app.Workbooks.Open(input_file)
    Workbook.ActiveSheet.ExportAsFixedFormat(0, output_file)
    pythoncom.CoUninitialize()
    
    close_connection(conn, cur)
    conn, cur = create_connection()
    
    ### Senior
    script1 = """SELECT * FROM TempS;"""
    cur.execute(script1)
    columnsS = [desc[0] for desc in cur.description]
    dataS = cur.fetchall()

    data_new1 = []
    for i in dataS:
        myTuple = ()
        data_new_tuple2 = [i[0]]
    
        for j in i[1:]:
            j = j.split(':')        
            j = j[0][2:]
            j = j[:-1]
            data_new_tuple2.append(j)
        myTuple = tuple(data_new_tuple2)
        data_new1.append(myTuple)
        myTuple = ()
        data_new_tuple2 = []
        
    df2 = pd.DataFrame(list(data_new1), columns=columnsS)
    
    writer2 = pd.ExcelWriter("schedule_S_pdf.xlsx", engine='xlsxwriter')
    df2.to_excel(writer2, sheet_name='Senior')
    workbook2  = writer2.book
    worksheet2 = writer2.sheets['Senior']

    # Add some cell formats.
    format1 = workbook2.add_format({'num_format': '#,##0.00'})
    format2 = workbook2.add_format({'num_format': '0%'})

    # Set the column width and format.
    worksheet2.set_column('B:B', 18, format1)
    # Set the format but not the column width.
    worksheet2.set_column('C:C', None, format2)
    writer2.save()    

    input_file2 = r'C:\flask_app\schedule_S_pdf.xlsx'
    output_file2 = r'C:\flask_app\schedule_S_pdf.pdf'
    
    pythoncom.CoInitialize()
    app2 = win32com.client.Dispatch("Excel.Application")
    app2.Interactive = False
    app2.Visible = False
    Workbook2 = app2.Workbooks.Open(input_file2)
    Workbook2.ActiveSheet.ExportAsFixedFormat(0, output_file2)
    pythoncom.CoUninitialize()
    
    close_connection(conn, cur)

    return redirect(url_for("timetable"))

# download points summary as pdf
@app.route('/download_points')
def download_points():
    if os.path.exists("points_J_pdf.pdf"):
        os.remove("points_J_pdf.pdf")
   
    if os.path.exists("points_S_pdf.pdf"):
        os.remove("points_S_pdf.pdf")
        
    myJson = retrieve_points_summary()
    myJunior = ''
    mySenior = ''
    
    for i in myJson:
        if i.lower() == 's':
            mySenior = myJson[i]    # <dict>
        elif i.lower() == 'j':
            myJunior = myJson[i]    # <dict>
    
    myJ = []
    myS = []
    for i in myJunior:
        myJ.append(i)
        
    for i in mySenior:
        myS.append(i)
    
    ### JUNIOR
    df_J = pd.DataFrame.from_dict(myJunior, orient='index')
    df_J.reset_index(level=0, inplace=False)

    writer = pd.ExcelWriter("points_J_pdf.xlsx", engine='xlsxwriter')
    df_J.to_excel(writer, sheet_name='Junior')
    workbook  = writer.book
    worksheet = writer.sheets['Junior']
    format1 = workbook.add_format({'num_format': '#,##0.00'})
    
    x = labels(alphabet='abcdefghijklmnopqrstuvwxyz')
    myCol = [next(x) for _ in range(len(myJ))]
    
    for i in myCol:
        worksheet.set_column(i.upper() +':'+ i.upper(), 18, format1)

    writer.save()    

    input_file = r'C:\flask_app\points_J_pdf.xlsx'
    output_file = r'C:\flask_app\points_J_pdf.pdf'

    pythoncom.CoInitialize()
    app = win32com.client.Dispatch("Excel.Application")
    app.Interactive = False
    app.Visible = False
    Workbook = app.Workbooks.Open(input_file)
    Workbook.ActiveSheet.ExportAsFixedFormat(0, output_file)
    pythoncom.CoUninitialize()

    ### SENIOR
    df_S = pd.DataFrame.from_dict(mySenior, orient='index')
    df_S.reset_index(level=0, inplace=False)

    writer2 = pd.ExcelWriter("points_S_pdf.xlsx", engine='xlsxwriter')
    df_S.to_excel(writer2, sheet_name='Senior')
    workbook2  = writer2.book
    worksheet2 = writer2.sheets['Senior']
    format1 = workbook2.add_format({'num_format': '#,##0.00'})
    
    y = labels(alphabet='abcdefghijklmnopqrstuvwxyz')
    myCol2 = [next(y) for _ in range(len(myS))]
    
    for i in myCol2:
        worksheet2.set_column(i.upper() +':'+ i.upper(), 18, format1)
    
    writer2.save()    

    input_file2 = r'C:\flask_app\points_S_pdf.xlsx'
    output_file2 = r'C:\flask_app\points_S_pdf.pdf'

    pythoncom.CoInitialize()
    app2 = win32com.client.Dispatch("Excel.Application")
    app2.Interactive = False
    app2.Visible = False
    Workbook2 = app2.Workbooks.Open(input_file2)
    Workbook2.ActiveSheet.ExportAsFixedFormat(0, output_file2)
    pythoncom.CoUninitialize() 
    
    return redirect(url_for("points"))

@app.route('/download_calls')
def download_calls():
    if os.path.exists("call_J_pdf.pdf"):
        os.remove("call_J_pdf.pdf")
     
    myJson = retrieve_call_summary()
     
    myJ = []
    for i in myJson:
        myJ.append(i)
   
    df_J = pd.DataFrame.from_dict(myJson, orient='index')
    df_J.reset_index(level=0, inplace=False)
    
    writer = pd.ExcelWriter("call_J_pdf.xlsx", engine='xlsxwriter')
    df_J.to_excel(writer, sheet_name='call')
    workbook  = writer.book
    worksheet = writer.sheets['call'] 
    
    format1 = workbook.add_format({'num_format': '#,##0.00'})
    
    x = labels(alphabet='abcdefghijklmnopqrstuvwxyz')
    myCol = [next(x) for _ in range(len(myJ))]
    
    for i in myCol:
        worksheet.set_column(i.upper() +':'+ i.upper(), 18, format1)
    
    writer.save()    
      
    input_file = r'C:\flask_app\call_J_pdf.xlsx'
    output_file = r'C:\flask_app\call_J_pdf.pdf'

    pythoncom.CoInitialize()
    app = win32com.client.Dispatch("Excel.Application")
    app.Interactive = False
    app.Visible = False
    Workbook = app.Workbooks.Open(input_file)
    Workbook.ActiveSheet.ExportAsFixedFormat(0, output_file)
    pythoncom.CoUninitialize()    
    
    return redirect(url_for("calls"))

def labels(alphabet=string.ascii_uppercase):
    assert len(alphabet) == len(set(alphabet))  # make sure every letter is unique
    s = [alphabet[0]]
    while 1:
        yield ''.join(s)
        l = len(s)
        for i in range(l-1, -1, -1):
            if s[i] != alphabet[-1]:
                s[i] = alphabet[alphabet.index(s[i])+1]
                s[i+1:] = [alphabet[0]] * (l-i-1)
                break
        else:
            s = [alphabet[0]] * (l+1)

# download icu duties as pdf
@app.route('/download_icu_duties')
def download_icu_duties():

    if os.path.exists("ICU_1_pdf.pdf"):
        os.remove("ICU_1_pdf.pdf")
   
    if os.path.exists("ICU_2_pdf.pdf"):
        os.remove("ICU_2_pdf.pdf")
        
    myJunior = retrieve_icu_1_table()
    mySenior = retrieve_icu_2_table()
    
    
    myJ = []
    myS = []
    for i in myJunior:
        myJ.append(i)
        
    for i in mySenior:
        myS.append(i)
    
    ### icu1
    df_J = pd.DataFrame.from_dict(myJunior, orient='index')
    df_J.reset_index(level=0, inplace=False)

    writer = pd.ExcelWriter("ICU_1_pdf.xlsx", engine='xlsxwriter')
    df_J.to_excel(writer, sheet_name='icu1')
    workbook  = writer.book
    worksheet = writer.sheets['icu1']
    format1 = workbook.add_format({'num_format': '#,##0.00'})
    
    x = labels(alphabet='abcdefghijklmnopqrstuvwxyz')
    myCol = [next(x) for _ in range(len(myJ))]
    
    for i in myCol:
        worksheet.set_column(i.upper() +':'+ i.upper(), 21, format1)

    writer.save()    

    input_file = r'C:\flask_app\ICU_1_pdf.xlsx'
    output_file = r'C:\flask_app\ICU_1_pdf.pdf'

    pythoncom.CoInitialize()
    app = win32com.client.Dispatch("Excel.Application")
    app.Interactive = False
    app.Visible = False
    Workbook = app.Workbooks.Open(input_file)
    Workbook.ActiveSheet.ExportAsFixedFormat(0, output_file)
    pythoncom.CoUninitialize()

    ### icu2
    df_S = pd.DataFrame.from_dict(mySenior, orient='index')
    df_S.reset_index(level=0, inplace=False)

    writer2 = pd.ExcelWriter("ICU_2_pdf.xlsx", engine='xlsxwriter')
    df_S.to_excel(writer2, sheet_name='icu2')
    workbook2  = writer2.book
    worksheet2 = writer2.sheets['icu2']
    format1 = workbook2.add_format({'num_format': '#,##0.00'})
    
    y = labels(alphabet='abcdefghijklmnopqrstuvwxyz')
    myCol2 = [next(y) for _ in range(len(myS))]
    
    for i in myCol2:
        worksheet2.set_column(i.upper() +':'+ i.upper(), 21, format1)
    
    writer2.save()    

    input_file2 = r'C:\flask_app\ICU_2_pdf.xlsx'
    output_file2 = r'C:\flask_app\ICU_2_pdf.pdf'

    pythoncom.CoInitialize()
    app2 = win32com.client.Dispatch("Excel.Application")
    app2.Interactive = False
    app2.Visible = False
    Workbook2 = app2.Workbooks.Open(input_file2)
    Workbook2.ActiveSheet.ExportAsFixedFormat(0, output_file2)
    pythoncom.CoUninitialize() 
    
    return redirect(url_for("icu_duties"))

# Downloading Senior & Junior timetables as csv
@app.route('/download_schedules_csv')
def download_schedules_csv():
    # Download the senior doctor schedule
    senior_schedule = exportScheduleS()

    # Download the junior doctor schedule
    junior_schedule = exportScheduleJ()

    return redirect(url_for("timetable"))

### TIMETABLE DATABASE ###
# generate new schedule
@app.route('/populate_database', methods=['GET','POST'])
def populate_database():
    # Obtain user input for schedule start date and end date
    try:
        query_start_date = request.form['start_date']        # Must be in this format of dd-mm-yyyy
        query_last_date = request.form['end_date']           # Must be in this format of dd-mm-yyyy
        query_request_month = request.form['selected_month'] 

        # If not must use the below 2 lines to convert the format
        query_start_date = datetime.strptime(query_start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
        query_last_date = datetime.strptime(query_last_date, '%d-%m-%Y').strftime('%Y-%m-%d')

        # Establish connection to DB
        conn, cur = create_connection()    

        cur.execute("""DELETE FROM InputDate;""")
        conn.commit() 

        cur.execute("""INSERT INTO InputDate (start_date,end_date,month) VALUES (?,?,?);""",
        (query_start_date,query_last_date,query_request_month))
        conn.commit() 

    except Exception as e:
        return (str(e)), 401

    # Check and read all sheets from the excel file and insert into DB
    try:
        clash_checker = clashes(query_start_date,query_last_date)
        if clash_checker == 'False':
            A = readRoster()
            B = readtraining(query_start_date,query_last_date)
            C = readDuties(query_start_date,query_last_date)
            D = readpleave(query_start_date,query_last_date)
            E = readPh()
        else:
            # return clash_checker, 501 
            return render_template("excel_error.html", clash_checker=clash_checker)
        
        F = email_json(query_start_date,query_last_date)

    except Exception as e:
        return (str(e)), 402
    
    # Get relevant data from DB
    try:
        # Fetch the constraints defined by the user from DB
        cur.execute("""SELECT * FROM Constraints;""")
        constraints_results = cur.fetchone()
        doctor_call_daily = constraints_results[1]
        day_off_monthly = constraints_results[2]
        max_call_month_4 = constraints_results[3]
        max_call_month_5 = constraints_results[4]

        # Fetch the doctor's name stored in DB
        cur.execute("""SELECT name FROM Roster;""")
        roster_results = cur.fetchall()

        # Drop previous Temp table, then create new Temp table with the doctor's name as column header
        cur.execute('''DROP TABLE IF EXISTS Temp;''')
        cur.execute("""CREATE TABLE IF NOT EXISTS Temp(date TEXT PRIMARY KEY);""")
        conn.commit()

        # Placing the name of doctors in a list AND adding doctor's name to Temp table as header
        doc_list = []
        for each in roster_results:
            doc_list.append(each[0])
            cur.execute('''ALTER TABLE Temp ADD COLUMN ''' + each[0] + ''' TEXT;''')

        # Fetch the Senior doctor's name stored in DB
        cur.execute("""SELECT name FROM Roster WHERE type ='S';""")
        senior_roster_results = cur.fetchall()

        # Drop previous TempS table, then create new TempS table with the senior doctor's name as column header
        cur.execute('''DROP TABLE IF EXISTS TempS;''')
        cur.execute("""CREATE TABLE IF NOT EXISTS TempS(date TEXT PRIMARY KEY);""")
        conn.commit()

        # Placing the name of senior doctors in a list AND adding doctor's name to TempS table as header
        senior_doc_list = []
        for each in senior_roster_results:
            senior_doc_list.append(each[0])
            cur.execute('''ALTER TABLE TempS ADD COLUMN ''' + each[0] + ''' TEXT;''')

        # Fetch the Junior doctor's name stored in DB
        cur.execute("""SELECT name FROM Roster WHERE type ='J';""")
        junior_roster_results = cur.fetchall()

        # Drop previous TempJ table, then create new TempJ table with the junior doctor's name as column header
        cur.execute('''DROP TABLE IF EXISTS TempJ;''')
        cur.execute("""CREATE TABLE IF NOT EXISTS TempJ(date TEXT PRIMARY KEY);""")
        conn.commit()

        # Placing the name of junior doctors in a list AND adding doctor's name to TempJ table as header
        junior_doc_list = []
        for each in junior_roster_results:
            junior_doc_list.append(each[0])
            cur.execute('''ALTER TABLE TempJ ADD COLUMN ''' + each[0] + ''' TEXT;''')

        # Fetch the training data stored in DB
        cur.execute("""SELECT * FROM Training WHERE start_date >= ? INTERSECT SELECT * FROM Training WHERE start_date <= ? 
        UNION SELECT * FROM Training WHERE end_date <= ? INTERSECT SELECT * FROM Training WHERE end_date >= ?;""",
        (query_start_date, query_last_date, query_last_date, query_start_date))
        training_results = cur.fetchall()

        # Fetch the duty data stored in DB
        cur.execute("""SELECT * FROM Duty WHERE start_date >= ? INTERSECT SELECT * FROM Duty WHERE start_date <= ? 
        UNION SELECT * FROM Duty WHERE end_date <= ? INTERSECT SELECT * FROM Duty WHERE end_date >= ?;""",
        (query_start_date, query_last_date, query_last_date, query_start_date))
        duty_results = cur.fetchall()

        # Fetch the priority leave data stored in DB
        cur.execute("""SELECT * FROM PriorityLeave WHERE start_date >= ? INTERSECT SELECT * FROM PriorityLeave WHERE start_date <= ? 
        UNION SELECT * FROM PriorityLeave WHERE end_date <= ? INTERSECT SELECT * FROM PriorityLeave WHERE end_date >= ?;""",
        (query_start_date, query_last_date, query_last_date, query_start_date))
        pl_results = cur.fetchall()

        # Fetch the leave application data stored in DB
        cur.execute("""SELECT * FROM LeaveApplication WHERE start_date >= ? INTERSECT SELECT * FROM LeaveApplication WHERE start_date <= ? 
        UNION SELECT * FROM LeaveApplication WHERE end_date <= ? INTERSECT SELECT * FROM LeaveApplication WHERE end_date >= ?;""",
        (query_start_date, query_last_date, query_last_date, query_start_date))
        la_results = cur.fetchall()

        # Fetch the call request data stored in DB
        cur.execute("""SELECT * FROM CallRequest WHERE date >= ? AND date <= ?;""",
        (query_start_date, query_last_date))
        cr_results = cur.fetchall()

    except Exception as e:
        return (str(e)), 403

    # Run the LP and get the LP results that are stored in DB
    # The input for run_lp is from read_excel functions above + days_for_dates_v3 + excel2matrix
    try:
        # Delete any existing data from ICU1Duty table from DB
        cur.execute("""DELETE FROM ICU1Duty""")
        conn.commit()

        # Delete any existing data from ICU2Duty table from DB
        cur.execute("""DELETE FROM ICU2Duty""")
        conn.commit()

        # Delete any existing data from CallLP table from DB
        cur.execute("""DELETE FROM CallLP""")
        conn.commit()

        # Reset the auto incremental numbers when each month's schedule is being generated
        cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'CallLP';""")
        conn.commit()

        # Delete any existing data from LeaveLP table from DB
        cur.execute("""DELETE FROM LeaveLP""")
        conn.commit()

        # Reset the auto incremental numbers when each month's schedule is being generated
        cur.execute("""DELETE FROM sqlite_sequence WHERE name = 'LeaveLP';""")
        conn.commit()

        lp_result = run_lp(doctor_call_daily, day_off_monthly, max_call_month_4, max_call_month_5, query_start_date, query_last_date, doc_list, A, B, C, D)

        # Insert lp results into DB
        for doc,monthly_activity in lp_result.items():

            cur.execute("""SELECT name FROM Roster where email = ?""",(doc,))
            query_result = cur.fetchone()
            doc_name = query_result[0]


            for each_day in monthly_activity:
                if each_day[1] == 1:
                    day = check_day(datetime.strptime(each_day[0], '%Y-%m-%d').date())
                    cr_dict = readCallRequest(doc_list,query_start_date,query_last_date)
                    check_ph_eve = check_eveph(each_day[0],E)
                    if doc in cr_dict:
                        for key,value in cr_dict[doc].items():
                            if value[1] == 'On Call':
                                if day == 'Friday':
                                    request_type = 'crF'
                                elif day == 'Saturday':
                                    request_type = 'crSat'
                                elif day == 'Sunday':
                                    request_type = 'crSun'
                                elif day in E:
                                    request_type = 'crPH'
                                elif check_ph_eve == True:
                                    request_type = 'crpPH'
                                else:
                                    request_type = 'cr'
                                if value[2] == None:
                                    new_remark = ''
                                    remark = new_remark
                                else:
                                    remark = cr_dict[doc][2]
                    # When doctors assigned calls but they did not request for calls
                    else:
                        if day == 'Friday':
                            request_type = 'cF'
                        elif day == 'Saturday':
                            request_type = 'cSat'
                        elif day == 'Sunday':
                            request_type = 'cSun'
                        elif day in E:
                            request_type = 'cPH'
                        elif check_ph_eve == True:
                            request_type = 'cpPH'
                        else:
                            request_type = 'c'
                        remark = ''

                    cur.execute("""INSERT INTO CallLP (email,name,date,request_type,remark) VALUES (?,?,?,?,?);""",
                    (doc,doc_name,each_day[0],request_type,remark))
                    conn.commit()

        # Fetch the call LP data stored in DB (call LP data should only contain processed data for the requested schedule month)
        cur.execute("""SELECT * FROM CallLP;""")
        call_lp_results = cur.fetchall()

        # Populate the LeaveLP table in DB
        # Update LeaveLP with approved leave applications, update LeaveApplication with rejected applications by adding (Rejected) in the remark column
        for each_leave_row in la_results:
            call_flag = False
            training_flag = False
            duty_flag = False
            pl_flag = False

            # Search the CallLP table for any calls that are within the leave application dates
            cur.execute("""SELECT * FROM CallLP WHERE email = ? AND date >= ? AND date <= ?""",(each_leave_row[1],each_leave_row[3],each_leave_row[4]))
            callLP_each_result = cur.fetchall()
            # When the leave application dates are not within the CallLP date for that doctor
            if len(callLP_each_result) == 0:
                call_flag = True

            # Search the Training table for any trainings that are within the leave application dates
            cur.execute("""SELECT * FROM Training WHERE start_date >= ? INTERSECT SELECT * FROM Training WHERE start_date <= ? 
            UNION SELECT * FROM Training WHERE end_date <= ? INTERSECT SELECT * FROM Training WHERE end_date >= ?;""",
            (each_leave_row[3], each_leave_row[4], each_leave_row[4], each_leave_row[3]))
            training_each_result = cur.fetchall()
            # When the leave application dates are not within the Training dates for that doctor
            if len(training_each_result) == 0:
                training_flag = True
            
            # Search the Duty table for any duties that are within the leave application dates
            cur.execute("""SELECT * FROM Duty WHERE start_date >= ? INTERSECT SELECT * FROM Duty WHERE start_date <= ? 
            UNION SELECT * FROM Duty WHERE end_date <= ? INTERSECT SELECT * FROM Duty WHERE end_date >= ?;""",
            (each_leave_row[3], each_leave_row[4], each_leave_row[4], each_leave_row[3]))
            duty_each_result = cur.fetchall()
            # When the leave application dates are not within the Duty dates for that doctor
            if len(duty_each_result) == 0:
                duty_flag = True
            
            # Search the PriorityLeave table for any priority leaves that are within the leave application dates
            cur.execute("""SELECT * FROM PriorityLeave WHERE start_date >= ? INTERSECT SELECT * FROM PriorityLeave WHERE start_date <= ? 
            UNION SELECT * FROM PriorityLeave WHERE end_date <= ? INTERSECT SELECT * FROM PriorityLeave WHERE end_date >= ?;""",
            (each_leave_row[3], each_leave_row[4], each_leave_row[4], each_leave_row[3]))
            pl_each_result = cur.fetchall()
            # When the leave application dates are not within the PriorityLeave dates for that doctor
            if len(pl_each_result) == 0:
                pl_flag = True

            # Accept the leave application when all flags are True by updating LeaveLP Table in DB
            if call_flag == True and training_flag == True and duty_flag == True and pl_flag == True:
                cur.execute("""INSERT INTO LeaveLP (email,name,start_date,end_date,duration,leave_type,remark) VALUES (?,?,?,?,?,?,?);""",
                (each_leave_row[1],each_leave_row[2],each_leave_row[3],each_leave_row[4],each_leave_row[5],each_leave_row[6],each_leave_row[7]))
                conn.commit()
            # Reject those leave application that clash with training/duty/calls/priorityleave by updating LeaveApplication Table remark column with (Rejected) behind any remarks already present
            else:
                old_remark = each_leave_row[7]
                if old_remark == None:
                    new_remark = "(Rejected)"
                    cur.execute("""UPDATE LeaveApplication SET remark = ? WHERE leave_id = ?;""",
                    (new_remark,each_leave_row[0]))
                    conn.commit()
                elif "(Rejected)" not in old_remark:
                    if old_remark != None:
                        new_remark = old_remark + " (Rejected)"
                    else:
                        new_remark = "(Rejected)"
                    cur.execute("""UPDATE LeaveApplication SET remark = ? WHERE leave_id = ?;""",
                    (new_remark,each_leave_row[0]))
                    conn.commit()

        # Fetch the leave LP data stored in DB (leave LP data should only contain processed data for the requested schedule month)
        cur.execute("""SELECT * FROM LeaveLP WHERE start_date >= ? INTERSECT SELECT * FROM LeaveLP WHERE start_date <= ? 
        UNION SELECT * FROM LeaveLP WHERE end_date <= ? INTERSECT SELECT * FROM LeaveLP WHERE end_date >= ?;""",
        (query_start_date, query_last_date, query_last_date, query_start_date))
        leave_lp_results = cur.fetchall()

    except Exception as e:
        return (str(e)), 404
    
    # Return the data in dictionary format to FrontEnd/UI
    try:
        # Dictionary to store all necessary data to render the main page timetable
        overall_result = {}
        overall_result1 = {}
        overall_result2 = {}

        # Appending all into dictionary with day as key and everything else as values
        sdate = datetime.strptime(query_start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(query_last_date, '%Y-%m-%d').date()   # end date
        delta = edate - sdate       # as timedelta
        for date_diff in range(delta.days + 1):
            day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
            day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)
            display_day = check_day(day) + " " + day.strftime("%d-%m-%Y")   # Sunday 31-12-2020 (string format)

            # Initialize an sql statement for inserting a row into Temp table
            sqlstmt = '''INSERT INTO Temp(date,'''
            for each in doc_list:
                sqlstmt += each + ''','''
            sqlstmt = sqlstmt[:-1] + """) VALUES ('""" + day_key + """',"""
            
            # Initialize an sql statement for inserting a row into TempS table
            sqlstmt1 = '''INSERT INTO TempS(date,'''
            for each in senior_doc_list:
                sqlstmt1 += each + ''','''
            sqlstmt1 = sqlstmt1[:-1] + """) VALUES ('""" + display_day + """',"""

            # Initialize an sql statement for inserting a row into TempJ table
            sqlstmt2 = '''INSERT INTO TempJ(date,'''
            for each in junior_doc_list:
                sqlstmt2 += each + ''','''
            sqlstmt2 = sqlstmt2[:-1] + """) VALUES ('""" + display_day + """',"""

            # Insert date into ICU1Duty and ICU2Duty table
            cur.execute("""INSERT INTO ICU1Duty(date) VALUES (?);""",(display_day,))    
            conn.commit()
            cur.execute("""INSERT INTO ICU2Duty(date) VALUES (?);""",(display_day,))                      
            conn.commit()

            # Check if the date is a weekend or weekday
            weekend_checker = check_weekend(day)    # True: date is on a weekend; False: date is on a weekday

            # Check if date is a public holiday (based on public holidays stored in DB)
            if day in E:
                ph_checker = 'True'   # Date is a public holiday
            else:
                ph_checker = 'False'  # Date is not a public holiday

            # Storing all doctor's training for schedule month in training dictionary
            training = {}
            for doc in training_results:
                startDate = doc[4]
                endDate = doc[5]
                doc_name = doc[2]
                training_name = doc[3]
                if day >= datetime.strptime(startDate, '%Y-%m-%d').date() and day <= datetime.strptime(endDate, '%Y-%m-%d').date():
                    training[doc_name] = training_name
            
            # Storing all doctor's duty for schedule month in duty dictionary
            duty = {}
            for doc in duty_results:
                startDate = doc[4]
                endDate = doc[5]
                doc_name = doc[2]
                duty_name = doc[3]
                if day >= datetime.strptime(startDate, '%Y-%m-%d').date() and day <= datetime.strptime(endDate, '%Y-%m-%d').date():
                    duty[doc_name] = duty_name
            
            # Storing all doctor's priority leave for schedule month in priority leave dictionary
            priority_leave = {}
            for doc in pl_results:
                startDate = doc[4]
                endDate = doc[5]
                doc_name = doc[2]
                leave_reason = doc[3]
                if day >= datetime.strptime(startDate, '%Y-%m-%d').date() and day <= datetime.strptime(endDate, '%Y-%m-%d').date():
                    priority_leave[doc_name] = leave_reason
            
            # Storing all doctor's calls based on LP for schedule month in call_LP dictionary
            call_LP = {}
            for doc in call_lp_results:
                call_date = doc[3]
                doc_name = doc[2]
                call_type = doc[4]
                remark = doc[5]
                if day == datetime.strptime(call_date, '%Y-%m-%d').date():
                    call_LP[doc_name] = call_type,remark
            
            # # Storing all doctor's leaves based on LP for schedule month in leave_LP dictionary
            leave_LP = {}
            for doc in leave_lp_results:
                startDate = doc[3]
                endDate = doc[4]
                doc_name = doc[2]
                duration = doc[5]
                leave_type = doc[6]
                remark = doc[7]
                if day >= datetime.strptime(startDate, '%Y-%m-%d').date() and day <= datetime.strptime(endDate, '%Y-%m-%d').date():
                    leave_LP[doc_name] = duration,leave_type,remark

            # Storing each day's activity by all doctors in one_day_dict
            one_day_dict = {}
            senior_one_day = {}
            junior_one_day = {}
            
            # Determine each doctor's activity based on above dictionaries and collate into 1 dictionary
            for each_doc in doc_list:
                one_doc_dict = {}

                if each_doc in training:
                    one_doc_dict[each_doc] = {"Training": training[each_doc]}
                elif each_doc in duty:
                    one_doc_dict[each_doc] = {"Duty": duty[each_doc]}
                elif each_doc in priority_leave:
                    one_doc_dict[each_doc] = {"Priority Leave": priority_leave[each_doc]}
                elif each_doc in call_LP:
                    one_doc_dict[each_doc] = {"On-Call": call_LP[each_doc][0] + "-" + call_LP[each_doc][1]}
                elif each_doc in leave_LP:
                    leave_converter = {
                        "Annual Leave" : "Leave (AL)",
                        "Training Leave" : "Leave (Training)",
                        "MC/Hospitalisation Leave" : "Leave (MC/HL)",
                        "Reservist Leave" : "Leave (Reservist)",
                        "Family Care Leave" : "Leave (Family)",
                        "Child Care Leave" : "Leave (Child)",
                        "Marriage Leave" : "Leave (Marriage)",
                        "Maternity Leave" : "Leave (Maternity)",
                        "Paternity Leave" : "Leave (Paternity)",
                        "Others": "Leave (Others)"
                    }
                    if leave_LP[each_doc][2] == None:
                        new_remark = ''
                    else:
                        new_remark = leave_LP[each_doc][2]
                    act_type = leave_LP[each_doc][1]
                    # one_doc_dict[each_doc] = {leave_LP[each_doc][0] + " " + leave_converter[act_type]: leave_LP[each_doc][2]}
                    # one_doc_dict[each_doc] = {leave_LP[each_doc][1]: leave_LP[each_doc][2]}       
                    one_doc_dict[each_doc] = {"On-Leave": leave_converter[act_type] + '-' + new_remark}   # No duration
                elif weekend_checker == 'True' or ph_checker == 'True':
                    one_doc_dict[each_doc] = {"Off": ""}
                else:
                    one_doc_dict[each_doc] = {"Working": ""}

                # Combine all the activity data into 1 single dictionary
                one_day_dict[each_doc] = one_doc_dict[each_doc]

            # Combine one day's worth of data into 1 overall dictionary
            overall_result[display_day] = one_day_dict

            # Continuation of creating sql statement to insert values into Temp table
            temp_list = []
            for each in doc_list:
                temp_list.append(str(one_day_dict[each]))
                sqlstmt += '''?,'''
            sqlstmt = sqlstmt[:-1] + ''');'''   # Example: INSERT INTO Temp(date,name,...) VALUES ('2020-08-15','training',...);
            temp_tuple = tuple(temp_list)

            # Executing sql statement to add values into Temp table
            cur.execute(sqlstmt,temp_tuple)
            conn.commit()

            # Determine each Senior doctor's activity based on above dictionaries and collate into 1 dictionary
            for each_doc in senior_doc_list:
                one_doc_dict = {}

                if each_doc in training:
                    one_doc_dict[each_doc] = {"Training": training[each_doc]}
                elif each_doc in duty:
                    one_doc_dict[each_doc] = {"Duty": duty[each_doc]}
                elif each_doc in priority_leave:
                    one_doc_dict[each_doc] = {"Priority Leave": priority_leave[each_doc]}
                elif each_doc in call_LP:
                    one_doc_dict[each_doc] = {"On-Call": call_LP[each_doc][0] + "-" + call_LP[each_doc][1]}
                elif each_doc in leave_LP:
                    leave_converter = {
                        "Annual Leave" : "Leave (AL)",
                        "Training Leave" : "Leave (Training)",
                        "MC/Hospitalisation Leave" : "Leave (MC/HL)",
                        "Reservist Leave" : "Leave (Reservist)",
                        "Family Care Leave" : "Leave (Family)",
                        "Child Care Leave" : "Leave (Child)",
                        "Marriage Leave" : "Leave (Marriage)",
                        "Maternity Leave" : "Leave (Maternity)",
                        "Paternity Leave" : "Leave (Paternity)",
                        "Others": "Leave (Others)"
                    }
                    if leave_LP[each_doc][2] == None:
                        new_remark = ''
                    else:
                        new_remark = leave_LP[each_doc][2]
                    act_type = leave_LP[each_doc][1]     
                    one_doc_dict[each_doc] = {"On-Leave": leave_converter[act_type] + '-' + new_remark}   # No duration
                elif weekend_checker == 'True' or ph_checker == 'True':
                    one_doc_dict[each_doc] = {"Off": ""}
                else:
                    one_doc_dict[each_doc] = {"Working": ""}

                # Combine all the activity data into 1 single dictionary
                senior_one_day[each_doc] = one_doc_dict[each_doc]
            
            # Combine one day's worth of data into 1 overall dictionary
            overall_result1[display_day] = senior_one_day

            # Continuation of creating sql statement 1 to insert values into TempS table
            temp_list = []
            for each in senior_doc_list:
                temp_list.append(str(senior_one_day[each]))
                sqlstmt1 += '''?,'''
            sqlstmt1 = sqlstmt1[:-1] + ''');'''   # Example: INSERT INTO TempS(date,name,...) VALUES ('2020-08-15','training',...);
            temp_tuple = tuple(temp_list)

            # Executing sql statement to add values into TempS table
            cur.execute(sqlstmt1,temp_tuple)
            conn.commit()

            # Determine each Junior doctor's activity based on above dictionaries and collate into 1 dictionary
            for each_doc in junior_doc_list:
                one_doc_dict = {}

                if each_doc in training:
                    one_doc_dict[each_doc] = {"Training": training[each_doc]}
                elif each_doc in duty:
                    one_doc_dict[each_doc] = {"Duty": duty[each_doc]}
                elif each_doc in priority_leave:
                    one_doc_dict[each_doc] = {"Priority Leave": priority_leave[each_doc]}
                elif each_doc in call_LP:
                    one_doc_dict[each_doc] = {"On-Call": call_LP[each_doc][0] + "-" + call_LP[each_doc][1]}
                elif each_doc in leave_LP:
                    leave_converter = {
                        "Annual Leave" : "Leave (AL)",
                        "Training Leave" : "Leave (Training)",
                        "MC/Hospitalisation Leave" : "Leave (MC/HL)",
                        "Reservist Leave" : "Leave (Reservist)",
                        "Family Care Leave" : "Leave (Family)",
                        "Child Care Leave" : "Leave (Child)",
                        "Marriage Leave" : "Leave (Marriage)",
                        "Maternity Leave" : "Leave (Maternity)",
                        "Paternity Leave" : "Leave (Paternity)",
                        "Others": "Leave (Others)"
                    }
                    if leave_LP[each_doc][2] == None:
                        new_remark = ''
                    else:
                        new_remark = leave_LP[each_doc][2]
                    act_type = leave_LP[each_doc][1]     
                    one_doc_dict[each_doc] = {"On-Leave": leave_converter[act_type] + '-' + new_remark}   # No duration
                elif weekend_checker == 'True' or ph_checker == 'True':
                    one_doc_dict[each_doc] = {"Off": ""}
                else:
                    one_doc_dict[each_doc] = {"Working": ""}

                # Combine all the activity data into 1 single dictionary
                junior_one_day[each_doc] = one_doc_dict[each_doc]

            # Combine one day's worth of data into 1 overall dictionary
            overall_result2[display_day] = junior_one_day

            # Continuation of creating sql statement 2 to insert values into TempJ table
            temp_list = []
            for each in junior_doc_list:
                temp_list.append(str(junior_one_day[each]))
                sqlstmt2 += '''?,'''
            sqlstmt2 = sqlstmt2[:-1] + ''');'''   # Example: INSERT INTO TempJ(date,name,...) VALUES ('2020-08-15','training',...);
            temp_tuple = tuple(temp_list)

            # Executing sql statement to add values into TempJ table
            cur.execute(sqlstmt2,temp_tuple)
            conn.commit()

        # Changing the output to desired format
        new = {}
        for each_doc in doc_list:
            overall_doc_activity = {}
            for key,value in overall_result.items():
                overall_doc_activity[key] = value[each_doc]
            
            new[each_doc] = overall_doc_activity
        
        new1 = {}
        for each_doc in senior_doc_list:
            overall_doc_activity = {}
            for key,value in overall_result1.items():
                overall_doc_activity[key] = value[each_doc]
            
            new1[each_doc] = overall_doc_activity
        
        new2 = {}
        for each_doc in junior_doc_list:
            overall_doc_activity = {}
            for key,value in overall_result2.items():
                overall_doc_activity[key] = value[each_doc]
            
            new2[each_doc] = overall_doc_activity
        
        # Put the dictionaries into dictionary format: {S: Senior doctor dictionary, J: Junior doctor dictionary}
        final = {'S':new1,'J':new2}
        
        # Close connection to DB
        close_connection(conn, cur)

        # returns the necessary data to render schedule
        return redirect(url_for('timetable'))  

    except Exception as e:
        return (str(e)), 405

# retrieve current timetable db state (TempS, TempJ tables)
@app.route('/retrieve_timetable', methods=['GET'])
def retrieve_timetable():
    conn, cur = create_connection()

    cur.execute("""SELECT name FROM Roster where type = 'J';""")
    junior_names = cur.fetchall()
    
    cur.execute("""SELECT name FROM Roster where type = 'S';""")
    senior_names = cur.fetchall()

    junior_dict = {}
    for i in range(len(junior_names)):
        cur.execute("""SELECT date, """ + str(junior_names[i][0]) + """ FROM TempJ;""")
        new1 = cur.fetchall()
        new = {}
        for each in new1:
            date = each[0]
            activty = each[1]
            activity1 = activty.replace("'",'"')
            new[date] = json.loads(activity1)
        name = str(junior_names[i][0])
        junior_dict[name] = new

    senior_dict = {}
    for i in range(len(senior_names)):
        cur.execute("""SELECT date, """ + str(senior_names[i][0]) + """ FROM TempS;""")
        new2 = cur.fetchall()
        new = {}
        for each in new2:
            date = each[0]
            activty = each[1]
            activity1 = activty.replace("'",'"')
            new[date] = json.loads(activity1)
        name = str(senior_names[i][0])
        senior_dict[name] = new
    
    # Put the dictionaries into dictionary format: {S: Senior doctor dictionary, J: Junior doctor dictionary}
    final = {'S':senior_dict,'J':junior_dict}
    
    # Close connection to DB
    close_connection(conn, cur)

    # returns the necessary data to render schedule
    return final

# update timetable
@app.route('/update_timetable_new',methods=['POST'])
def update_timetable_new():
    conn, cur = create_connection()

    jsdata = request.form['javascript_data']
    status = json.loads(jsdata)['status']
    doctor = json.loads(jsdata)['doctor']
    date = json.loads(jsdata)['date']
    types = json.loads(jsdata)['types']
    remarks = json.loads(jsdata)['remarks']

    if status == 'J':
        # SELECT * from "TempJ"where date='Thursday 16-07-2020'
        # UPDATE "TempJ" SET H = "{'Priority Leave': 'NEW'}" WHERE date = 'Thursday 16-07-2020'
        sqlstmt = """UPDATE TempJ SET """ + doctor + """ = ? WHERE date = ?;"""
        new_variable = "{'" + str(types) + "':'" + str(remarks) + "'}"
        cur.execute(sqlstmt, (new_variable, date))
        conn.commit()

    elif status == 'S':
        sqlstmt = """UPDATE TempS SET """ + doctor + """ = ? WHERE date = ?;"""
        new_variable = "{'" + str(types) + "':'" + str(remarks) + "'}"
        cur.execute(sqlstmt, (new_variable, date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    # Returns either True or constraints that are not met in the form: {date:[constraint1,constraint2],date:[constraint1],...}
    return "True"

### HOME DATABASE ###
# RETRIEVE FROM CONSTRAINTS TABLE
@app.route('/retrieve_constraints', methods=['GET'])
def retrieve_constraints():
    conn, cur = create_connection()
    cur.execute("""SELECT * FROM Constraints;""")
    constraints = cur.fetchall()
    close_connection(conn, cur)

    result = {
                'doctor_call_daily': constraints[0][1],
                'day_off_monthly': constraints[0][2],
                'max_call_month_4': constraints[0][3],
                'max_call_month_5': constraints[0][4],
                'total_call': constraints[0][5],
                'clinic1': constraints[0][6],
                'clinic2': constraints[0][7],
                'amSat_clinic4': constraints[0][8],
                'amSat_clinic1': constraints[0][9],
                'amSat_clinic3': constraints[0][10],
                'p': constraints[0][11]
            }

    return result

# Takes in user-edited constraint and updates the DB
@app.route('/edit_constraints', methods=['POST'])
def edit_constraints():
    # Obtain user input values from front-end UI to save into DB, also create connection to DB
    try:
        doctor_call_daily = request.form['doctor_call_daily']
        day_off_monthly = request.form['day_off_monthly']
        max_call_month_4 = request.form['max_call_month_4']
        max_call_month_5 = request.form['max_call_month_5']
        total_call = request.form['total_call']
        clinic1 = request.form['clinic1']
        clinic2 = request.form['clinic2']
        amSat_clinic4 = request.form['amSat_clinic4']
        amSat_clinic1 = request.form['amSat_clinic1']
        amSat_clinic3 = request.form['amSat_clinic3']
        p = request.form['p']

        # Establish connection to DB
        conn, cur = create_connection()

    except Exception as e:
        return (str(e)), 401

    try:
        # Empty the Constraints Table in DB
        cur.execute("""DELETE FROM Constraints""")
        conn.commit()

        # Original Constraints set by admin
        # cur.execute("""INSERT OR IGNORE INTO Constraints(constraint_id, doctor_call_daily, day_off_monthly, max_call_month_four, max_call_month_five,total_call,clinic1,clinic2,amSat_clinic4,amSat_clinic1,amSat_clinic3,p) 
        # VALUES (1, 3, 4, 6, 7, 3, 2, 1, 2, 1, 1, 3);""")
        # conn.commit()

        # Insert edited values into database and commit to database
        cur.execute("""INSERT OR IGNORE INTO Constraints
        (constraint_id, doctor_call_daily, day_off_monthly, max_call_month_four, max_call_month_five,total_call,clinic1,clinic2,amSat_clinic4,amSat_clinic1,amSat_clinic3,p) 
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", 
        (doctor_call_daily,day_off_monthly,max_call_month_4,max_call_month_5,
        total_call,clinic1,clinic2,amSat_clinic4,amSat_clinic1,amSat_clinic3,p))
        conn.commit()

        # Close connection to DB
        close_connection(conn, cur)

        # Returns True when saved successfully into DB
        return redirect(url_for("home"))
    
    except Exception as e:
        return (str(e)), 402

# Checks the constraints as specified in the DB with the Temp table
@app.route('/check_constraints', methods=['GET'])
def check_constraints():
    # Establish connection to DB
    conn, cur = create_connection()
    sqlstmt = """SELECT * FROM InputDate;"""
    cur.execute(sqlstmt)
    query_date = cur.fetchone()
    start_date = query_date[0]    
    end_date = query_date[1]

    # Close connection to DB
    close_connection(conn, cur)

    checking = is_constraint_met('Temp', start_date, end_date)
    return checking

### CALLS DATABASE ### 
# Retrieves the call summary based on the current Temp table in DB
@app.route('/retrieve_call_summary', methods=['GET'])
def retrieve_call_summary():
    # Obtain user input and create connection to DB
    try:
        # Establish connection to DB
        conn, cur = create_connection()
        sqlstmt = """SELECT * FROM InputDate;"""
        cur.execute(sqlstmt)
        query_date = cur.fetchone()
        start_date = query_date[0]
        end_date = query_date[1]
  
    except Exception as e:
        return (str(e)), 401

    # Calculate the month's call summary and return to UI
    try:
        # Manipulating the dates for the function to work
        sdate = datetime.strptime(start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(end_date, '%Y-%m-%d').date()   # end date
        delta = edate - sdate       # as timedelta

        # Dictionary to store the month's call summary
        overall_summary = {}
     
        # Creating a loop to check the calls/duties/working for each day
        for date_diff in range(delta.days + 1):
            day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
            day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)
            display_day = check_day(day) + " " + day.strftime("%d-%m-%Y")   # Sunday 31-12-2020 (string format)
        
            # Retrieve from DB each day's schedule
            sqlstmt = """SELECT * FROM TempS WHERE date = ?;"""
            cur.execute(sqlstmt,(display_day,))
            constraints_result_S = cur.fetchone()

            # Retrieve from DB each day's schedule
            sqlstmt = """SELECT * FROM TempJ WHERE date = ?;"""
            cur.execute(sqlstmt,(display_day,))
            constraints_result_J = cur.fetchone()
       
            # Counters to record the number of calls/duties/working for each day assigned
            counter_clinic1 = 0
            counter_clinic2 = 0
            counter_amsatclinic1 = 0
            counter_amsatclinic3 = 0
            counter_amsatclinic4 = 0
            counter_p = 0
            counter_totalcall = 0
            counter_total = 0
      
            # Counting the calls/duties/working from all doctors for each day
            for element in constraints_result_S[1:]:
                str_element = element.replace("'",'"')
                dict_element = json.loads(str_element)
  
                for key,value in dict_element.items():
                    if value == 'Clinic 1':
                        counter_clinic1 += 1
                    elif value == 'Clinic 2':
                        counter_clinic2 += 1
                    elif value == 'amSat Clinic 1':
                        counter_amsatclinic1 += 1
                    elif value == 'amSat Clinic 3':
                        counter_amsatclinic3 += 1
                    elif value == 'amSat Clinic 4':
                        counter_amsatclinic4 += 1
                    elif value == 'P':
                        counter_p += 1
                    elif value == 'c' or value == 'cr':
                        counter_totalcall += 1
                    elif key == 'AM leave' or key == 'PM leave' or key == 'Working':
                        counter_total += 1
            
            # Counting the calls/duties/working from all doctors for each day
            for element in constraints_result_J[1:]:
                str_element = element.replace("'",'"')
                dict_element = json.loads(str_element)
  
                for key,value in dict_element.items():
                    if value == 'Clinic 1':
                        counter_clinic1 += 1
                    elif value == 'Clinic 2':
                        counter_clinic2 += 1
                    elif value == 'amSat Clinic 1':
                        counter_amsatclinic1 += 1
                    elif value == 'amSat Clinic 3':
                        counter_amsatclinic3 += 1
                    elif value == 'amSat Clinic 4':
                        counter_amsatclinic4 += 1
                    elif value == 'P':
                        counter_p += 1
                    elif value == 'c' or value == 'cr':
                        counter_totalcall += 1
                    elif key == 'AM leave' or key == 'PM leave' or key == 'Working':
                        counter_total += 1

            # Placing each day's call summary into a dictionary format
            overall_summary[day_key] = {
                "total" : counter_total,
                "total call" : counter_totalcall,
                "clinic 1" : counter_clinic1,
                "clinic 2" : counter_clinic2,
                "amSat Clinic 1" : counter_amsatclinic1,
                "amSat Clinic 3" : counter_amsatclinic3,
                "amSat Clinic 4" : counter_amsatclinic4,
                "P" : counter_p
            }

        # Close connection to DB
        close_connection(conn, cur)

        # Return the month's call summary to UI
        return overall_summary

    except Exception as e:
        return (str(e)), 402

### ICU DATABASE ### 
# Retrieve ICU1 table
@app.route('/retrieve_icu_1_table',methods=['GET'])
def retrieve_icu_1_table():
    conn, cur = create_connection()
    cur.execute("""SELECT name, date FROM ICU1Duty;""")
    result = cur.fetchall()
    close_connection(conn, cur)

    final = {}
    for i in result:
        name = i[0]
        date = i[1]
        final[date] = name

    return final

# Retrieve ICU2 table
@app.route('/retrieve_icu_2_table',methods=['GET'])
def retrieve_icu_2_table():
    conn, cur = create_connection()
    cur.execute("""SELECT name, date FROM ICU2Duty;""")
    result = cur.fetchall()
    close_connection(conn, cur)

    final = {}
    for i in result:
        name = i[0]
        date = i[1]
        final[date] = name

    return final

# Update ICU tables
@app.route('/update_icu_table',methods=['POST'])
def update_icu_table():
    jsdata = request.form['javascript_data']
    cell_id = json.loads(jsdata)['cell_id']
    table = cell_id.split('/')[0]
    date = cell_id.split('/')[1]
    doctor = cell_id.split('/')[2]

    # SELECT * from "ICU1Duty"
    # INSERT OR REPLACE INTO ICU1Duty (name, date) VALUES ('hello', 'Thursday 16-07-2020');
    # UPDATE "ICU1Duty" SET name = "hey" WHERE date = 'Thursday 16-07-2020'
    conn, cur = create_connection()
    if table == '1':
        sqlstmt = """UPDATE ICU1Duty SET name = ? WHERE date = ?;"""
        cur.execute(sqlstmt, (doctor, date))
        conn.commit()
    else:
        sqlstmt = """UPDATE ICU2Duty SET name = ? WHERE date = ?;"""
        cur.execute(sqlstmt, (doctor, date))
        conn.commit()

    # Close connection to DB
    close_connection(conn, cur)

    # Returns either True or constraints that are not met in the form: {date:[constraint1,constraint2],date:[constraint1],...}
    return "True"

### POINTS DATABASE ###
# Calculating and returning each doctor's number of points for the scheduled month
@app.route('/retrieve_points_summary', methods=['GET'])
def retrieve_points_summary():
    # Create connection to DB and obtain the request month from UI
    try:
        # Establish connection to DB & retrieve request month
        conn, cur = create_connection()
        sqlstmt = """SELECT * FROM InputDate;"""
        cur.execute(sqlstmt)
        query_date = cur.fetchone()
        request_month = query_date[2]
        month_num = check_month_num(request_month)
        
    except Exception as e:
        return (str(e)), 401

    # Calculate the month's point summary for all doctors and return to UI
    try:
        # Fetch the Senior doctor's name stored in DB
        cur.execute("""SELECT name FROM Roster WHERE type ='S';""")
        senior_roster_results = cur.fetchall()

        # Dictionary to store the scheduled month's point summary for senior doctors
        senior_summary = {}
        
        # Query TempS table for each doctor's schedule
        for each in senior_roster_results:
            sqlstmt = """SELECT """ + each[0] + """ FROM TempS;"""   #each[0] refers to the doctor's name
            cur.execute(sqlstmt)
            constraints_result = cur.fetchall()

            # Counters to record the number of calls/duties/leave for each day assigned
            counter_wd = 0
            counter_fri = 0
            counter_sat = 0
            counter_sun = 0
            counter_preph = 0
            counter_ph = 0
            counter_satsunam = 0
            counter_leave = 0
            counter_clinic1 = 0
            counter_clinic2 = 0
            counter_clinic3 = 0
            counter_clinic4 = 0
            counter_duty = 0

            for element in constraints_result:
                str_element = element[0].replace("'",'"')
                dict_element = json.loads(str_element)
                for key,value in dict_element.items():
                    if 'c-' in value or 'cr-' in value:
                        counter_wd += 1
                    elif 'cF-' in value or 'crF-' in value:
                        counter_fri += 1
                    elif 'cSat-' in value or 'crSat-' in value:
                        counter_sat += 1
                    elif 'cSun-' in value or 'crSun-' in value:
                        counter_sun += 1
                    elif 'cpPH-' in value or 'crpPH-' in value:
                        counter_preph += 1
                    elif 'cPH-' in value or 'crPH-' in value:
                        counter_ph += 1
                    elif value == 'Clinic 1':
                        counter_clinic1 += 1
                    elif value == 'Clinic 2':
                        counter_clinic2 += 1
                    elif value == 'Clinic 3':
                        counter_clinic3 += 1
                    elif value == 'Clinic 4':
                        counter_clinic4 += 1
                    elif value == 'amSat Clinic 1' or value == 'amSat Clinic 2' or value == 'amSat Clinic 3' or value == 'amSat Clinic 4':
                        counter_satsunam += 1
                    elif value == 'amSun Clinic 1' or value == 'amSun Clinic 2' or value == 'amSun Clinic 3' or value == 'amSun Clinic 4':
                        counter_satsunam += 1
                    elif key == 'AM Leave' or key == 'PM Leave' or key == 'Whole Leave' or key == 'Priority Leave':
                        counter_leave += 1
                    if key == 'Duty':
                        counter_duty += 1
            
            
            # Tabulating the total points for calls and duties
            points_fri = 1.5 * counter_fri
            points_sat = 2 * counter_sat
            points_sun = 3 * counter_sun
            points_preph = 2.5 * counter_preph
            points_ph = 3 * counter_ph
            points_satsunam = 0.5 * counter_satsunam
            month_call_points = counter_wd + points_fri + points_sat + points_sun + points_preph + points_ph
            month_calls = counter_wd + counter_fri + counter_sat + counter_sun + counter_preph + counter_ph

            # Placing each day's call summary into a dictionary format
            senior_summary[each[0]] = {
                "Month calls" : month_calls,
                "Month call points" : month_call_points,
                "WD" : counter_wd,
                "Fri" : points_fri,
                "Sat" : points_sat,
                "Sun" : points_sun,
                "Pre-PH" : points_preph,
                "PH" : points_ph,
                "Sat/Sun AM" : points_satsunam,
                "Leave" : counter_leave,
                "Clinic 1" : counter_clinic1,
                "Clinic 2" : counter_clinic2,
                "Clinic 3" : counter_clinic3,
                "Clinic 4" : counter_clinic4,
                "Duties" : counter_duty
            }

        # Fetch the Junior doctor's name stored in DB
        cur.execute("""SELECT name FROM Roster WHERE type ='J';""")
        junior_roster_results = cur.fetchall()

        # Dictionary to store the scheduled month's point summary for junior doctors
        junior_summary = {}

        # Query TempJ table for each doctor's schedule
        for each in junior_roster_results:
            sqlstmt = """SELECT """ + each[0] + """ FROM TempJ;"""   #each[0] refers to the doctor's name
            cur.execute(sqlstmt)
            constraints_result = cur.fetchall()

            # Counters to record the number of calls/duties/leave for each day assigned
            counter_wd = 0
            counter_fri = 0
            counter_sat = 0
            counter_sun = 0
            counter_preph = 0
            counter_ph = 0
            counter_satsunam = 0
            counter_leave = 0
            counter_clinic1 = 0
            counter_clinic2 = 0
            counter_clinic3 = 0
            counter_clinic4 = 0
            counter_duty = 0

            # Counting the calls/duties/leave from all doctors for each day
            for element in constraints_result:
                str_element = element[0].replace("'",'"')
                dict_element = json.loads(str_element)
                for key,value in dict_element.items():
                    if 'c-' in value or 'cr-' in value:
                        counter_wd += 1
                    elif 'cF-' in value or 'crF-' in value:
                        counter_fri += 1
                    elif 'cSat-' in value or 'crSat-' in value:
                        counter_sat += 1
                    elif 'cSun-' in value or 'crSun-' in value:
                        counter_sun += 1
                    elif 'cpPH-' in value or 'crpPH-' in value:
                        counter_preph += 1
                    elif 'cPH-' in value or 'crPH-' in value:
                        counter_ph += 1
                    elif value == 'Clinic 1':
                        counter_clinic1 += 1
                    elif value == 'Clinic 2':
                        counter_clinic2 += 1
                    elif value == 'Clinic 3':
                        counter_clinic3 += 1
                    elif value == 'Clinic 4':
                        counter_clinic4 += 1
                    elif value == 'amSat Clinic 1' or value == 'amSat Clinic 2' or value == 'amSat Clinic 3' or value == 'amSat Clinic 4':
                        counter_satsunam += 1
                    elif value == 'amSun Clinic 1' or value == 'amSun Clinic 2' or value == 'amSun Clinic 3' or value == 'amSun Clinic 4':
                        counter_satsunam += 1
                    elif key == 'AM Leave' or key == 'PM Leave' or key == 'Whole Leave' or key == 'Priority Leave':
                        counter_leave += 1
                    if key == 'Duty':
                        counter_duty += 1
            
            # Tabulating the total points for calls and duties
            points_fri = 1.5 * counter_fri
            points_sat = 2 * counter_sat
            points_sun = 3 * counter_sun
            points_preph = 2.5 * counter_preph
            points_ph = 3 * counter_ph
            points_satsunam = 0.5 * counter_satsunam
            month_call_points = counter_wd + points_fri + points_sat + points_sun + points_preph + points_ph
            month_calls = counter_wd + counter_fri + counter_sat + counter_sun + counter_preph + counter_ph

            # Placing each day's call summary into a dictionary format
            junior_summary[each[0]] = {
                "Month calls" : month_calls,
                "Month call points" : month_call_points,
                "WD" : counter_wd,
                "Fri" : points_fri,
                "Sat" : points_sat,
                "Sun" : points_sun,
                "Pre-PH" : points_preph,
                "PH" : points_ph,
                "Sat/Sun AM" : points_satsunam,
                "Leave" : counter_leave,
                "Clinic 1" : counter_clinic1,
                "Clinic 2" : counter_clinic2,
                "Clinic 3" : counter_clinic3,
                "Clinic 4" : counter_clinic4,
                "Duties" : counter_duty
            }

        # Place the 2 points summary dictionaries into a single dictionary
        overall_summary = {'S': senior_summary, 'J': junior_summary}

        # Close connection to DB
        close_connection(conn, cur)

        # Return the month's call summary to UI
        return overall_summary
    
    except Exception as e:
        return (str(e)), 402


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)