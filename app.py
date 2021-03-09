import sqlite3
import holidays
import pdfkit
from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response, request
from datetime import date, timedelta, datetime
from helperFunctions import create_connection, close_connection, check_weekend
from lpFunction import run_lp
from pprint import pprint
# import datetime
# from win32com.client import Dispatch

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "hello"

# Display the main page when user first loads the Flask app at localhost:5000
@app.route('/', methods=["POST", "GET"])
@app.route('/login', methods=["POST", "GET"])
def login(): 
    if request.method == "POST": 
        session["user"] = request.form["name"]
        return redirect(url_for("timetable"))
    else: 
        if "user" in session:
            return redirect(url_for("timetable"))
        return render_template("login.html")

# logout 
@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out!", "info")
    return redirect(url_for("login"))

# specify email filter page
@app.route('/email_filter', methods=["POST"])
def email_filter():
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    # use the start_date and end_date for email extraction 
    # put email extraction code here

    return render_template("email_filter.html")

# SCRATCH
# @app.route('/scratch')
# def scratch():
#     result = {
#                 "2020-07-16": {
#                     "A": "Duty",
#                     "B": "On-leave",
#                     "C": "On-call",
#                     "D": "Working",
#                     "E": "Off"
#                 },
#                 "2020-07-17": {
#                     "A": "Duty",
#                     "B": "On-call",
#                     "C": "Working",
#                     "D": "On-leave",
#                     "E": "Working"
#                 },
#                 "2020-07-18": {
#                     "A": "Duty",
#                     "B": "On-call",
#                     "C": "On-leave",
#                     "D": "Working",
#                     "E": "Working"
#                 },
#                 "2020-07-19": {
#                     "A": "Duty",
#                     "B": "On-leave",
#                     "C": "Working",
#                     "D": "Working",
#                     "E": "Duty"
#                 },
#                 "2020-07-20": {
#                     "A": "Duty",
#                     "B": "Working",
#                     "C": "Working",
#                     "D": "Working",
#                     "E": "Duty"
#                 }
#             }
#     return render_template("scratch.html", result=result)

# timetable page - timetable 
@app.route('/timetable')
def timetable():    
    timetable_dict = {
        "2020-07-16": {
            "A": "Duty",
            "B": "On-leave",
            "C": "On-call",
            "D": "Working",
            "E": "Off",
            "F": "Off"
        },
        "2020-07-17": {
            "A": "Duty",
            "B": "On-call",
            "C": "Working",
            "D": "On-leave",
            "E": "Working",
            "F": "On-call"
        },
        "2020-07-18": {
            "A": "Duty",
            "B": "On-call",
            "C": "On-leave",
            "D": "Working",
            "E": "Working",
            "F": "Duty"
        },
        "2020-07-19": {
            "A": "On-leave",
            "B": "On-leave",
            "C": "Working",
            "D": "Working",
            "E": "Duty",
            "F": "Duty"
        },
        "2020-07-20": {
            "A": "Duty",
            "B": "Working",
            "C": "Working",
            "D": "Working",
            "E": "Duty",
            "F": "On-leave"
        },
            "2020-07-21": {
            "A": "Working",
            "B": "On-leave",
            "C": "On-call",
            "D": "Working",
            "E": "Off",
            "F": "Off"
        }
    }

    call_summary_dict = {
        "2020-07-16": {
            "total call": "8",
            "Clinic 1": "1",
            "Clinic 2": "2",
            "amSat Clinic 4": "0",
            "amSat Clinic 1": "1",
            "amSat Clinic 3": "1",
            "P": "2"
        },
        "2020-07-17": {
            "total call": "7",
            "Clinic 1": "1",
            "Clinic 2": "0",
            "amSat Clinic 4": "2",
            "amSat Clinic 1": "0",
            "amSat Clinic 3": "2",
            "P": "1"
        },
        "2020-07-18": {
            "total call": "8",
            "Clinic 1": "1",
            "Clinic 2": "1",
            "amSat Clinic 4": "1",
            "amSat Clinic 1": "1",
            "amSat Clinic 3": "1",
            "P": "2"
        },
        "2020-07-19": {
            "total call": "8",
            "Clinic 1": "1",
            "Clinic 2": "2",
            "amSat Clinic 4": "1",
            "amSat Clinic 1": "1",
            "amSat Clinic 3": "0",
            "P": "1"
        },
        "2020-07-20": {
            "total call": "8",
            "Clinic 1": "1",
            "Clinic 2": "0",
            "amSat Clinic 4": "2",
            "amSat Clinic 1": "2",
            "amSat Clinic 3": "1",
            "P": "2"
        },
        "2020-07-21": {
            "total call": "8",
            "Clinic 1": "2",
            "Clinic 2": "0",
            "amSat Clinic 4": "2",
            "amSat Clinic 1": "1",
            "amSat Clinic 3": "1",
            "P": "1"
        }
    }
    
    return render_template("timetable.html", timetable_dict=timetable_dict, call_summary_dict=call_summary_dict)

# points page
@app.route('/points')
def points():
    points_dict = {
        "A": {
            "Month Calls": "6",
            "WD": "0",
            "Fri": "1",
            "Sat": "0",
            "Sun": "1",
            "Pre-PH": "0",
            "PH": "1",
            "Sat/Sun AM":"0",
            "Leave": "1",
            "Clinic 1": "2",
            "Clinic 2": "0"
        },
        "B": {
            "Month Calls": "6",
            "WD": "1",
            "Fri": "0",
            "Sat": "1",
            "Sun": "0",
            "Pre-PH": "0",
            "PH": "1",
            "Sat/Sun AM":"0",
            "Leave": "2",
            "Clinic 1": "1",
            "Clinic 2": "0"
        },
        "C": {
            "Month Calls": "7",
            "WD": "1",
            "Fri": "1",
            "Sat": "1",
            "Sun": "1",
            "Pre-PH": "0",
            "PH": "0",
            "Sat/Sun AM":"0",
            "Leave": "2",
            "Clinic 1": "1",
            "Clinic 2": "3"
        },
        "D": {
            "Month Calls": "6",
            "WD": "1",
            "Fri": "2",
            "Sat": "0",
            "Sun": "0",
            "Pre-PH": "1",
            "PH": "0",
            "Sat/Sun AM":"1",
            "Leave": "0",
            "Clinic 1": "0",
            "Clinic 2": "2"
        },
        "E": {
            "Month Calls": "7",
            "WD": "0",
            "Fri": "1",
            "Sat": "0",
            "Sun": "1",
            "Pre-PH": "0",
            "PH": "1",
            "Sat/Sun AM":"0",
            "Leave": "2",
            "Clinic 1": "0",
            "Clinic 2": "2"
        },
        "F": {
            "Month Calls": "8",
            "WD": "1",
            "Fri": "2",
            "Sat": "0",
            "Sun": "1",
            "Pre-PH": "1",
            "PH": "2",
            "Sat/Sun AM":"2",
            "Leave": "1",
            "Clinic 1": "2",
            "Clinic 2": "3"
        }
    }
    return render_template("points.html", points_dict=points_dict)

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

# @app.route('/admin')
# def admin():
#     return redirect(url_for("user", content=name, age=2, array_list=["billy","jim","timmy"]))

# Runs the LP and returns all the data needed to render the timetable
@app.route('/display_timetable', methods=['GET'])
def retrieve_all():
    # Obtain user input for schedule start date and end date
    try:
        #query_start_date = request.form['start_date']
        query_start_date = '2020-07-16'
        #query_last_date = request.form['end_date']
        query_last_date = '2020-08-15'
    
    except Exception as e:
        return (str(e)), 404
    
    # Get data from DB, Run the LP, Return the data in dictionary format to FrontEnd/UI
    try:
        # Establish connection to DB
        conn, cur = create_connection()

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
        doc_list = []
        for each in roster_results:
            doc_list.append(each[0])

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

        # Fetch the priority leave data stored in DB
        cur.execute("""SELECT * FROM PublicHoliday;""")
        ph_results = cur.fetchall()

        # Insert LP code here using constraints, duty, training, priority leave, public holiday
        run_lp(doctor_call_daily, day_off_monthly, max_call_month_4, max_call_month_5, duty_results, training_results, pl_results, ph_results)
        
        # Fetch the call LP data stored in DB (call LP data should only contain processed data for the requested schedule month)
        cur.execute("""SELECT * FROM CallLP;""")
        call_lp_results = cur.fetchall()

        # Fetch the leave LP data stored in DB (leave LP data should only contain processed data for the requested schedule month)
        cur.execute("""SELECT * FROM LeaveLP WHERE start_date >= ? INTERSECT SELECT * FROM LeaveLP WHERE start_date <= ? 
        UNION SELECT * FROM LeaveLP WHERE end_date <= ? INTERSECT SELECT * FROM LeaveLP WHERE end_date >= ?;""",
        (query_start_date, query_last_date, query_last_date, query_start_date))
        leave_lp_results = cur.fetchall()

        # Dictionary to store all necessary data to render the main page timetable
        overall_result = {}

        # Appending all into dictionary with day as key and everything else as values
        sdate = datetime.strptime(query_start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(query_last_date, '%Y-%m-%d').date()   # end date
        delta = edate - sdate       # as timedelta
        for date_diff in range(delta.days + 1):
            day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
            day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)

            # Check if the date is a weekend or weekday
            # True: date is on a weekend
            # False: date is on a weekday
            weekend_checker = check_weekend(day)

            # Check if date is a public holiday (based on public holidays stored in DB)
            if day in ph_results:
                # Date is a public holiday
                ph_checker = True
            else:
                # Date is not a public holiday
                ph_checker = False

            training = {}
            for doc in training_results:
                startDate = doc[4]
                endDate = doc[5]
                doc_name = doc[2]
                training_name = doc[3]
                if day >= datetime.strptime(startDate, '%Y-%m-%d').date() and day <= datetime.strptime(endDate, '%Y-%m-%d').date():
                    training[doc_name] = training_name
            
            duty = {}
            for doc in duty_results:
                startDate = doc[4]
                endDate = doc[5]
                doc_name = doc[2]
                duty_name = doc[3]
                if day >= datetime.strptime(startDate, '%Y-%m-%d').date() and day <= datetime.strptime(endDate, '%Y-%m-%d').date():
                    duty[doc_name] = duty_name
            
            priority_leave = {}
            for doc in pl_results:
                startDate = doc[4]
                endDate = doc[5]
                doc_name = doc[2]
                leave_reason = doc[3]
                if day >= datetime.strptime(startDate, '%Y-%m-%d').date() and day <= datetime.strptime(endDate, '%Y-%m-%d').date():
                    priority_leave[doc_name] = leave_reason
            """
            call_LP = {}
            for doc in call_lp_results:
                call_date = doc[3]
                doc_name = doc[2]
                call_type = doc[4]
                remark = doc[5]
                if day == datetime.strptime(call_date, '%Y-%m-%d').date():
                    call_LP[doc_name] = call_type,remark
            
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
"""
            one_day_dict = {}
            
            for each_doc in doc_list:
                one_doc_dict = {}

                if each_doc in training:
                    one_doc_dict[each_doc] = {"Training": training[each_doc]}
                elif each_doc in duty:
                    one_doc_dict[each_doc] = {"Duty": duty[each_doc]}
                elif each_doc in priority_leave:
                    one_doc_dict[each_doc] = {"Priority Leave": priority_leave[each_doc]}
                # elif each_doc in call_LP:
                #     one_doc_dict[each_doc] = {call_LP[each_doc][0]: call_LP[each_doc][1]}
                # elif each_doc in leave_LP:
                #     one_doc_dict[each_doc] = {"leave_LP[each_doc][1]": leave_LP[each_doc][2]}
                elif weekend_checker == True or ph_checker == True:
                    one_doc_dict[each_doc] = {"Off": ""}
                else:
                    one_doc_dict[each_doc] = {"Working": ""}

                # Combine all the activity data into 1 single dictionary
                one_day_dict[each_doc] = one_doc_dict[each_doc]

            # Combine one day's worth of data into 1 overall dictionary
            overall_result[day_key] = one_day_dict

        # Close connection to DB
        close_connection(conn, cur)

        # returns the necessary data to render schedule
        return overall_result, 200
        # return render_template("scratch.html", all_data_dict)

    except Exception as e:
        return (str(e)), 404

# Takes in user-edited constraint and updates the DB
@app.route('/edit_constraints', methods=['POST'])
def edit_constraints():
    #Obtain user input values from front-end UI for saving into the DB
    doctor_call_daily = request.form['']
    day_off_monthly = request.form['']
    max_call_month_4 = request.form['']
    max_call_month_5 = request.form['']

    try:
        #Establish connection to DB
        conn, cur = create_connection()

        #Insert edited values into database and commit to database
        cur.execute("""UPDATE Constraints 
        SET doctor_call_daily = ?, day_off_monthly = ?, max_call_month_four = ?, max_call_month_five = ?;""", 
        (doctor_call_daily,day_off_monthly,max_call_month_4,max_call_month_5))
        conn.commit()

        #Close connection to DB
        close_connection(conn, cur)

        #returns successful message
        return 'Constraints have been successfully changed!' ,200
    
    except Exception as e:
        return (str(e)), 404

# API endpoint to check public holidays
@app.route('/check_public_holiday', methods=['GET'])
def check_ph():
    ### weekdays as a tuple
    weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

    sg_Holiday = []
    count = 0
    conn, cur = create_connection()

    ### Singapore Holidays - 2021
    for holiday in sorted(holidays.Singapore(years=2021).items()):
        ### get the day of that week
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

    close_connection(conn, cur)
    return(str(sg_Holiday))

# API endpoint to check public holidays
# @app.route('/check_public_holiday', methods=['GET'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)