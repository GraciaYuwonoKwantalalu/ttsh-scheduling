import sqlite3
import holidays
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import date, timedelta, datetime
from sqlFunctionCalls import create_connection, close_connection
from lpFunction import run_lp
from pprint import pprint

# Initialize Flask app
app = Flask(__name__)
#app.secret_key = "hello"

# Display the main page when user first loads the Flask app at localhost:5000
@app.route('/')
def index():
    return render_template("base.html")

@app.route('/login', methods=["POST", "GET"])
def login(): 
    if request.method == "POST": 
        session["user"] = request.form["name"]
        return redirect(url_for("timetable"))
    else: 
        if "user" in session:
            return redirect(url_for("timetable"))
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out!", "info")
    return redirect(url_for("login"))

@app.route('/timetable')
def timetable():    
    # LP 
    return render_template("timetable.html")

@app.route('/points')
def points():
    return render_template("points.html")

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
        all_data_dict = {}

        # Appending all into dictionary with day as key and everything else as values
        sdate = datetime.strptime(query_start_date, '%Y-%m-%d').date()   # start date
        edate = datetime.strptime(query_last_date, '%Y-%m-%d').date()   # end date
        delta = edate - sdate       # as timedelta
        for date_diff in range(delta.days + 1):
            day = sdate + timedelta(days=date_diff)     # 2020-08-02 (datetime object format)
            day_key = day.strftime("%Y-%m-%d")          # 2020-08-02 (string format)

            training = {}
            for doc in training_results:
                startDate = doc[4]
                endDate = doc[5]
                doc_name = doc[2]
                training_name = doc[3]
                if day >= datetime.strptime(startDate, '%Y-%m-%d').date() and day <= datetime.strptime(endDate, '%Y-%m-%d').date():
                    training[doc_name] = training_name
                if training:
                    all_data_dict[day_key] ={"Training" : training}
            
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
            # Combine all the necessary data into 1 single dictionary
            all_data_dict[day_key] ={"Training": training, "Duty": duty, "Priority Leave": priority_leave, "Call": 'call_LP', "Leave": 'leave_LP'}

        #Close connection to DB
        close_connection(conn, cur)

        #returns the necessary data to render schedule
        return all_data_dict, 200

    except Exception as e:
        return (str(e)), 404

#Takes in user-edited constraint and updates the DB
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

#API endpoint to check public holidays
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
    #pprint(sg_Holiday)
    return(str(sg_Holiday))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)