import sqlite3
import holidays
import pdfkit
import json
import pandas as pd
from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response, request
from datetime import date, timedelta, datetime
from helperFunctions import create_connection, close_connection, check_weekend, is_constraint_met
from lpFunction import run_lp
from pprint import pprint
# import datetime
# from win32com.client import Dispatch

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "hello"

### PAGES ###
# Display the main page when user first loads the Flask app at localhost:5000
@app.route('/login', methods=["POST", "GET"])
def login(): 
    if request.method == "POST": 
        session["user"] = request.form["name"]
        return redirect(url_for("timetable"))
    else: 
        if "user" in session:
            return redirect(url_for("timetable"))
        return render_template("login.html")

# home
@app.route('/', methods=["POST", "GET"])
@app.route('/home')
def home(): 
    return render_template("home.html")

# logout 
@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out!", "info")
    return redirect(url_for("login"))

# specify email filter page
@app.route('/extract_dates', methods=["POST"])
def extract_dates():
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    dates = [start_date, end_date]

    return redirect(url_for("timetable"))

# SCRATCH
@app.route('/scratch')
def scratch():
    result = {
                "2020-07-16": {
                    "A": "Duty",
                    "B": "On-leave",
                    "C": "On-call",
                    "D": "Working",
                    "E": "Off"
                },
                "2020-07-17": {
                    "A": "Duty",
                    "B": "On-call",
                    "C": "Working",
                    "D": "On-leave",
                    "E": "Working"
                },
                "2020-07-18": {
                    "A": "Duty",
                    "B": "On-call",
                    "C": "On-leave",
                    "D": "Working",
                    "E": "Working"
                },
                "2020-07-19": {
                    "A": "Duty",
                    "B": "On-leave",
                    "C": "Working",
                    "D": "Working",
                    "E": "Duty"
                },
                "2020-07-20": {
                    "A": "Duty",
                    "B": "Working",
                    "C": "Working",
                    "D": "Working",
                    "E": "Duty"
                }
            }

    dict1 = retrieve_timetable()
    dict2 = retrieve_call_summary()
    return render_template("scratch.html", result=result, dict1=dict1, dict2=dict2)

# timetable page  
@app.route('/timetable')
def timetable():    
    # timetable_dict = {
    #     "2020-07-16": {
    #         "A": "Duty",
    #         "B": "On-leave",
    #         "C": "On-call",
    #         "D": "Working",
    #         "E": "Off",
    #         "F": "Off"
    #     },
    #     "2020-07-17": {
    #         "A": "Duty",
    #         "B": "On-call",
    #         "C": "Working",
    #         "D": "On-leave",
    #         "E": "Working",
    #         "F": "On-call"
    #     },
    #     "2020-07-18": {
    #         "A": "Duty",
    #         "B": "On-call",
    #         "C": "On-leave",
    #         "D": "Working",
    #         "E": "Working",
    #         "F": "Duty"
    #     },
    #     "2020-07-19": {
    #         "A": "On-leave",
    #         "B": "On-leave",
    #         "C": "Working",
    #         "D": "Working",
    #         "E": "Duty",
    #         "F": "Duty"
    #     },
    #     "2020-07-20": {
    #         "A": "Duty",
    #         "B": "Working",
    #         "C": "Working",
    #         "D": "Working",
    #         "E": "Duty",
    #         "F": "On-leave"
    #     },
    #         "2020-07-21": {
    #         "A": "Working",
    #         "B": "On-leave",
    #         "C": "On-call",
    #         "D": "Working",
    #         "E": "Off",
    #         "F": "Off"
    #     }
    # }

    # call_summary_dict = {
    #     "2020-07-16": {
    #         "total call": "8",
    #         "Clinic 1": "1",
    #         "Clinic 2": "2",
    #         "amSat Clinic 4": "0",
    #         "amSat Clinic 1": "1",
    #         "amSat Clinic 3": "1",
    #         "P": "2"
    #     },
    #     "2020-07-17": {
    #         "total call": "7",
    #         "Clinic 1": "1",
    #         "Clinic 2": "0",
    #         "amSat Clinic 4": "2",
    #         "amSat Clinic 1": "0",
    #         "amSat Clinic 3": "2",
    #         "P": "1"
    #     },
    #     "2020-07-18": {
    #         "total call": "8",
    #         "Clinic 1": "1",
    #         "Clinic 2": "1",
    #         "amSat Clinic 4": "1",
    #         "amSat Clinic 1": "1",
    #         "amSat Clinic 3": "1",
    #         "P": "2"
    #     },
    #     "2020-07-19": {
    #         "total call": "8",
    #         "Clinic 1": "1",
    #         "Clinic 2": "2",
    #         "amSat Clinic 4": "1",
    #         "amSat Clinic 1": "1",
    #         "amSat Clinic 3": "0",
    #         "P": "1"
    #     },
    #     "2020-07-20": {
    #         "total call": "8",
    #         "Clinic 1": "1",
    #         "Clinic 2": "0",
    #         "amSat Clinic 4": "2",
    #         "amSat Clinic 1": "2",
    #         "amSat Clinic 3": "1",
    #         "P": "2"
    #     },
    #     "2020-07-21": {
    #         "total call": "8",
    #         "Clinic 1": "2",
    #         "Clinic 2": "0",
    #         "amSat Clinic 4": "2",
    #         "amSat Clinic 1": "1",
    #         "amSat Clinic 3": "1",
    #         "P": "1"
    #     }
    # }

    timetable_dict = retrieve_timetable()
    timetable_dict_df = pd.DataFrame.from_dict(timetable_dict)
    call_summary_dict = retrieve_call_summary()
    call_summary_df = pd.DataFrame.from_dict(call_summary_dict)
    
    return render_template("timetable.html", timetable_dict=timetable_dict, row_names=timetable_dict_df.index.values, column_names=timetable_dict_df.columns.values, row_data=list(timetable_dict_df.values.tolist()), zip=zip, call_summary_tables=[call_summary_df.to_html(classes='data')])

# points page
@app.route('/points')
def points():
    overall_summary = retrieve_points_summary()
    # points_dict = {
    #     "A": {
    #         "Month Calls": "6",
    #         "WD": "0",
    #         "Fri": "1",
    #         "Sat": "0",
    #         "Sun": "1",
    #         "Pre-PH": "0",
    #         "PH": "1",
    #         "Sat/Sun AM":"0",
    #         "Leave": "1",
    #         "Clinic 1": "2",
    #         "Clinic 2": "0"
    #     },
    #     "B": {
    #         "Month Calls": "6",
    #         "WD": "1",
    #         "Fri": "0",
    #         "Sat": "1",
    #         "Sun": "0",
    #         "Pre-PH": "0",
    #         "PH": "1",
    #         "Sat/Sun AM":"0",
    #         "Leave": "2",
    #         "Clinic 1": "1",
    #         "Clinic 2": "0"
    #     },
    #     "C": {
    #         "Month Calls": "7",
    #         "WD": "1",
    #         "Fri": "1",
    #         "Sat": "1",
    #         "Sun": "1",
    #         "Pre-PH": "0",
    #         "PH": "0",
    #         "Sat/Sun AM":"0",
    #         "Leave": "2",
    #         "Clinic 1": "1",
    #         "Clinic 2": "3"
    #     },
    #     "D": {
    #         "Month Calls": "6",
    #         "WD": "1",
    #         "Fri": "2",
    #         "Sat": "0",
    #         "Sun": "0",
    #         "Pre-PH": "1",
    #         "PH": "0",
    #         "Sat/Sun AM":"1",
    #         "Leave": "0",
    #         "Clinic 1": "0",
    #         "Clinic 2": "2"
    #     },
    #     "E": {
    #         "Month Calls": "7",
    #         "WD": "0",
    #         "Fri": "1",
    #         "Sat": "0",
    #         "Sun": "1",
    #         "Pre-PH": "0",
    #         "PH": "1",
    #         "Sat/Sun AM":"0",
    #         "Leave": "2",
    #         "Clinic 1": "0",
    #         "Clinic 2": "2"
    #     },
    #     "F": {
    #         "Month Calls": "8",
    #         "WD": "1",
    #         "Fri": "2",
    #         "Sat": "0",
    #         "Sun": "1",
    #         "Pre-PH": "1",
    #         "PH": "2",
    #         "Sat/Sun AM":"2",
    #         "Leave": "1",
    #         "Clinic 1": "2",
    #         "Clinic 2": "3"
    #     }
    # }
    return render_template("points.html", overall_summary=overall_summary)

# icu duties page
@app.route('/icu_duties')
def icu_duties():
    call_summary_dict = retrieve_call_summary()
    return render_template("icu_duties.html", call_summary_dict=call_summary_dict)

### DOWNLOAD ###
# download timetable as pdf
@app.route('/download_pdf')
def download_timetable():
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_url('http://localhost:5000/timetable', False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=timetable.pdf'
    return response

# download points summary as pdf
@app.route('/download_points')
def download_points():
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_url('http://localhost:5000/points', False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=points.pdf'
    return response

# download icu duties as pdf
@app.route('/download_icu_duties')
def download_icu_duties():
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_url('http://localhost:5000/icu_duties', False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=icu_duties.pdf'
    return response

### DATABASE ###
# Fetch data necessary for LP, runs LP, create new DB Temp table, returns formatted doctor's schedule
@app.route('/retrieve_timetable', methods=['GET'])
def retrieve_timetable():
    # Obtain user input for schedule start date and end date
    try:
        query_start_date = '2020-07-16'
        query_last_date = '2020-08-15'

        # Establish connection to DB
        conn, cur = create_connection()     

    except Exception as e:
        return (str(e)), 404

    # Read all sheets from the excel file and insert into DB
    # try:
    #     A = readRoster()
    #     B = readTraining()
    #     C = readDuties()
    #     D = readPl()
    #     E = readPh()
    
    # except Exception as e:
    #     return (str(e)), 404
    
    # Get relevant data from DB
    try:
        # Fetch the constraints defined by the user from DB
        cur.execute("""SELECT * FROM Constraints;""")
        constraints_results = cur.fetchone()
        doctor_call_daily = constraints_results[1]
        day_off_monthly = constraints_results[2]
        max_call_month_4 = constraints_results[3]
        max_call_month_5 = constraints_results[4]
        total_call = constraints_results[5]
        clinic1 = constraints_results[6]
        clinic2 = constraints_results[7]
        amSat_clinic4 = constraints_results[8]
        amSat_clinic1 = constraints_results[9]
        amSat_clinic3 = constraints_results[10]
        p = constraints_results[11]

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

        # Fetch the public holiday data stored in DB
        cur.execute("""SELECT * FROM PublicHoliday;""")
        ph_results = cur.fetchall()

    except Exception as e:
        return (str(e)), 404

    # Run the LP and get the LP results that are stored in DB
    try:
        run_lp(doctor_call_daily, day_off_monthly, max_call_month_4, max_call_month_5, 
                total_call, clinic1, clinic2, amSat_clinic4, amSat_clinic1, amSat_clinic3, p, 
                duty_results, training_results, pl_results, ph_results)
        
        # Fetch the call LP data stored in DB (call LP data should only contain processed data for the requested schedule month)
        cur.execute("""SELECT * FROM CallLP;""")
        call_lp_results = cur.fetchall()

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

        # Appending all into dictionary with day as key and everything else as values
        sdate = datetime.strptime(query_start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(query_last_date, '%Y-%m-%d').date()   # end date
        delta = edate - sdate       # as timedelta
        for date_diff in range(delta.days + 1):
            day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
            day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)

            # Initialize an sql statement for inserting a row into Temp table
            sqlstmt = '''INSERT INTO Temp(date,'''
            for each in doc_list:
                sqlstmt += each + ''','''
            sqlstmt = sqlstmt[:-1] + """) VALUES ('""" + day_key + """',"""

            # Check if the date is a weekend or weekday
            weekend_checker = check_weekend(day)    # True: date is on a weekend; False: date is on a weekday

            # Check if date is a public holiday (based on public holidays stored in DB)
            if day in ph_results:
                ph_checker = True   # Date is a public holiday
            else:
                ph_checker = False  # Date is not a public holiday

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
            
            # Storing all doctor's leaves based on LP for schedule month in leave_LP dictionary
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
                    one_doc_dict[each_doc] = {call_LP[each_doc][0]: call_LP[each_doc][1]}
                elif each_doc in leave_LP:
                    one_doc_dict[each_doc] = {"leave_LP[each_doc][1]": leave_LP[each_doc][2]}
                elif weekend_checker == True or ph_checker == True:
                    one_doc_dict[each_doc] = {"Off": ""}
                else:
                    one_doc_dict[each_doc] = {"Working": ""}

                # Combine all the activity data into 1 single dictionary
                one_day_dict[each_doc] = one_doc_dict[each_doc]

            # Combine one day's worth of data into 1 overall dictionary
            overall_result[day_key] = one_day_dict

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
    
        # Close connection to DB
        close_connection(conn, cur)

        # returns the necessary data to render schedule
        return overall_result
        # return render_template("scratch.html", all_data_dict)

    except Exception as e:
        return (str(e)), 404

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
        return (str(e)), 404

    try:
        # Insert edited values into database and commit to database
        cur.execute("""UPDATE Constraints 
        SET doctor_call_daily = ?, day_off_monthly = ?, max_call_month_four = ?, max_call_month_five = ?,
        total_call = ?, clinic1 = ?, clinic2 = ?, amSat_clinic4 = ?, amSat_clinic1 = ?, amSat_clinic3 = ?, p = ?
        ;""", 
        (doctor_call_daily,day_off_monthly,max_call_month_4,max_call_month_5,
        total_call,clinic1,clinic2,amSat_clinic4,amSat_clinic1,amSat_clinic3,p))
        conn.commit()

        # Close connection to DB
        close_connection(conn, cur)

        # Returns True when saved successfully into DB
        return True, 200
    
    except Exception as e:
        return (str(e)), 404

# Checks the constraints as specified in the DB with the Temp table
@app.route('/check_constraints', methods=['GET'])
def is_constraint_met_temp():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    checking = is_constraint_met('Temp', start_date, end_date)
    return checking

# Updates the Temp table if constraints are still met after changes are made to the schedule
@app.route('/update_timetable',methods=['POST'])
def update_timetable():
    # Obtain user input values from front-end UI for saving into the DB
    activityType = request.form['type']
    remark = request.form['remark']
    doctor = request.form['doctor']
    date = request.form['date']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    
    # Format the changes in dictionary format
    input_data = {str(activityType) : str(remark)}

    # Establish connection to DB
    conn, cur = create_connection()

    # Delete and previous Checking table and create a new Checking table to check whether changes made does not violate the constraints
    cur.execute('''DROP TABLE IF EXISTS Checking;''')
    cur.execute("""CREATE TABLE IF NOT EXISTS Checking AS SELECT * FROM Temp""")

    # Make changes to the Checking table to check constraint violation
    # WARNING: Prone to SQL Injection Attack (Assumption is that the admin is trustworthy and won't jeopardise the system)
    sqlstmt = """UPDATE Checking SET """ + doctor + """ = ? WHERE date = ?;"""
    cur.execute(sqlstmt,(input_data,date))
    conn.commit()

    # Check whether constraints are violated.
    # WARNING: Prone to SQL Injection Attack (Assumption is that the admin is trustworthy and won't jeopardise the system)
    checker = is_constraint_met('Checking', start_date, end_date)

    # If constraints not violated, then make permanent changes to the Temp table
    # WARNING: Prone to SQL Injection Attack (Assumption is that the admin is trustworthy and won't jeopardise the system)
    if checker == True:
        sqlstmt = """UPDATE Temp SET """ + doctor + """ = ? WHERE date = ?;"""
        cur.execute(sqlstmt,(input_data,date))
        conn.commit()
        message = True
    # Otherwise, do not make any changes to the Temp table and discard user's changes
    else:
        message = checker
    
    # Close connection to DB
    close_connection(conn, cur)

    # Returns either True or constraints that are not met in the form: {date:[constraint1,constraint2],date:[constraint1],...}
    return message, 200

# Retrieves the call summary based on the current Temp table in DB
@app.route('/retrieve_call_summary', methods=['GET'])
def retrieve_call_summary():
    # Obtain user input and create connection to DB
    try:
        # Establish connection to DB
        conn, cur = create_connection()

        # Obtain the schedule's start date and end date
        start_date = '2020-07-16'
        end_date = '2020-08-15'

    except Exception as e:
        return (str(e)), 404

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

            # Retrieve from DB each day's schedule
            sqlstmt = """SELECT * FROM Temp WHERE date = ?;"""
            cur.execute(sqlstmt,(day_key,))
            constraints_result = cur.fetchone()

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
            for element in constraints_result[1:]:
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
        return (str(e)), 404

# API endpoint to check public holidays
@app.route('/check_public_holiday', methods=['GET'])
def check_ph():
    try:
        # Establish connection to DB
        conn, cur = create_connection()

        # Obtain the schedule's start date and end date
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Delete any old data inside PublicHoliday table in DB
        cur.execute("""DELETE FROM PublicHoliday""")
        conn.commit()

    except Exception as e:
        return (str(e)), 404
    
    try:
        # Manipulating the dates for the function to work
        sdate = datetime.strptime(start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(end_date, '%Y-%m-%d').date()   # end date
        syear = sdate.year
        eyear = edate.year

        # Weekdays as a tuple
        weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

        sg_Holiday = []
        count = 0

        # When the scheduled month is within the same year
        if syear == eyear:
            # Singapore Holidays - the starting year
            for holiday in sorted(holidays.Singapore(years=syear).items()):
                # Get the day of that week
                holiday_date = holiday[0]
                holiday_day = holiday_date.weekday()
                holiday_weekday = weekDays[holiday_day]
                
                count += 1
                
                case = {
                    "ID": count,
                    "HolidayName":holiday[1],
                    "HolidayDate":format(holiday[0]),
                    "HolidayDay":format(holiday_weekday)
                }

                cur.execute("""INSERT OR IGNORE INTO PublicHoliday(holiday_id, holiday_name, holiday_date, holiday_day) 
                VALUES (?, ?, ?, ?);""", (count,holiday[1],format(holiday[0]),format(holiday_weekday)))
                conn.commit()

                sg_Holiday.append(case)

        # When the scheduled month spills over into the next year
        else:
            # Singapore Holidays - the starting year
            for holiday in sorted(holidays.Singapore(years=syear).items()):
                # Get the day of that week
                holiday_date = holiday[0]
                holiday_day = holiday_date.weekday()
                holiday_weekday = weekDays[holiday_day]
                
                count += 1
                
                case = {
                    "ID": count,
                    "HolidayName":holiday[1],
                    "HolidayDate":format(holiday[0]),
                    "HolidayDay":format(holiday_weekday)
                }

                cur.execute("""INSERT OR IGNORE INTO PublicHoliday(holiday_id, holiday_name, holiday_date, holiday_day) 
                VALUES (?, ?, ?, ?);""", (count,holiday[1],format(holiday[0]),format(holiday_weekday)))
                conn.commit()

                sg_Holiday.append(case)

            # Singapore Holidays - the ending year
            for holiday in sorted(holidays.Singapore(years=eyear).items()):
                # Get the day of that week
                holiday_date = holiday[0]
                holiday_day = holiday_date.weekday()
                holiday_weekday = weekDays[holiday_day]
                
                count += 1
                
                case = {
                    "ID": count,
                    "HolidayName":holiday[1],
                    "HolidayDate":format(holiday[0]),
                    "HolidayDay":format(holiday_weekday)
                }

                cur.execute("""INSERT OR IGNORE INTO PublicHoliday(holiday_id, holiday_name, holiday_date, holiday_day) 
                VALUES (?, ?, ?, ?);""", (count,holiday[1],format(holiday[0]),format(holiday_weekday)))
                conn.commit()

                sg_Holiday.append(case)

        # Close connection to DB
        close_connection(conn, cur)

        # Return the public holidays for the year to UI
        return(str(sg_Holiday)), 200

    except Exception as e:
        return (str(e)), 404

# Checking and storing the ICU 1 Duty for the scheduled month
@app.route('/insert_icu_1_duties', methods=['POST'])
def insert_icu_1_duties():
    # Obtain user input and create connection to DB
    try:
        # Establish connection to DB
        conn, cur = create_connection()

        # Obtain the ICU1 user input as dictionary
        user_input_dict = request.form['input_dictionary']

        # Obtain the schedule's start date and end date
        start_date = request.form['start_date']
        end_date = request.form['end_date']

    except Exception as e:
        return (str(e)), 404

    try:
        # Manipulating the dates for the function to work
        sdate = datetime.strptime(start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(end_date, '%Y-%m-%d').date()   # end date
        delta = edate - sdate       # as timedelta

        # List to store any dates that have errors
        error_list = []

        # Creating a loop to go through the input dictionary
        for date_diff in range(delta.days + 1):
            day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
            day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)

            # Counting the total number of ICU 1 duty in 1 day
            sum_counter = 0
            for key,value in user_input_dict[day_key]:
                sum_counter += int(value)

            # If the ICU 1 duty constraint is met, store the user inputs into the ICU1Duty table in DB
            if sum_counter == 1:
                for key,value in user_input_dict[day_key]:
                    cur.execute("""INSERT OR IGNORE INTO ICU1Duty(name, date, duty_status) VALUES (?,?,?);""",(key,day_key,value))
                    conn.commit()
            # Otherwise, store the days where the constraint is not met
            else:
                error_list.append(day_key)
        
        # If there are any days where ICU duty constraint is not met, delete all data from ICU1Duty table in DB and return the list of dates with constraint not met
        if len(error_list) != 0:
            cur.execute("""DELETE FROM ICU1Duty""")
            conn.commit()
            message = error_list
        # Return True when constraint for all days is met
        else:
            message = True

        # Close connection to DB
        close_connection(conn, cur)

        #Returns True or list of dates with constraint not met
        return message, 200

    except Exception as e:
        return (str(e)), 404

# Checking and storing the ICU 2 Duty for the scheduled month
@app.route('/insert_icu_2_duties', methods=['POST'])
def insert_icu_2_duties():
    # Obtain user input and create connection to DB
    try:
        # Establish connection to DB
        conn, cur = create_connection()

        # Obtain the ICU1 user input as dictionary
        user_input_dict = request.form['input_dictionary']

        # Obtain the schedule's start date and end date
        start_date = request.form['start_date']
        end_date = request.form['end_date']

    except Exception as e:
        return (str(e)), 404

    try:
        # Manipulating the dates for the function to work
        sdate = datetime.strptime(start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(end_date, '%Y-%m-%d').date()   # end date
        delta = edate - sdate       # as timedelta

        # List to store any dates that have errors
        error_list = []

        # Creating a loop to go through the input dictionary
        for date_diff in range(delta.days + 1):
            day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
            day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)

            # Counting the total number of ICU 2 duty in 1 day
            sum_counter = 0
            for key,value in user_input_dict[day_key]:
                sum_counter += int(value)

            # If the ICU 2 duty constraint is met, store the user inputs into the ICU2Duty table in DB
            if sum_counter == 1:
                for key,value in user_input_dict[day_key]:
                    cur.execute("""INSERT OR IGNORE INTO ICU2Duty(name, date, duty_status) VALUES (?,?,?);""",(key,day_key,value))
                    conn.commit()
            # Otherwise, store the days where the constraint is not met
            else:
                error_list.append(day_key)
        
        # If there are any days where ICU duty constraint is not met, delete all data from ICU2Duty table in DB and return the list of dates with constraint not met
        if len(error_list) != 0:
            cur.execute("""DELETE FROM ICU2Duty""")
            conn.commit()
            message = error_list
        # Return True when constraint for all days is met
        else:
            message = True

        # Close connection to DB
        close_connection(conn, cur)

        #Returns True or list of dates with constraint not met
        return message, 200

    except Exception as e:
        return (str(e)), 404

# Calculating and returning each doctor's number of points for the scheduled month
@app.route('/retrieve_points_summary', methods=['GET'])
def retrieve_points_summary():
    # Obtain schedule start date and end date, also create connection to DB
    try:
        # Establish connection to DB
        conn, cur = create_connection()

    except Exception as e:
        return (str(e)), 404

    # Calculate the month's point summary for all doctors and return to UI
    try:
        # Fetch the doctor's name stored in DB
        cur.execute("""SELECT name FROM Roster;""")
        roster_results = cur.fetchall()

        # Dictionary to store the scheduled month's point summary
        overall_summary = {}

        # Query Temp table for each doctor's schedule
        for each in roster_results:
            sqlstmt = """SELECT """ + each[0] + """ FROM Temp;"""   #each[0] refers to the doctor's name
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
                    if value == 'c' or value == 'cr':
                        counter_wd += 1
                    elif value == 'cF' or value == 'crF':
                        counter_fri += 1
                    elif value == 'cSat' or value == 'crSat':
                        counter_sat += 1
                    elif value == 'cSun' or value == 'crSun':
                        counter_sun += 1
                    elif value == 'cpPH' or value == 'crpPH':
                        counter_preph += 1
                    elif value == 'cPH' or value == 'crPH':
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
            overall_summary[each[0]] = {
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
                 
        # Close connection to DB
        close_connection(conn, cur)

        # Return the month's call summary to UI
        return overall_summary
    
    except Exception as e:
        return (str(e)), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)