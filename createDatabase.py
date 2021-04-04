import sqlite3
from helperFunctions import create_connection, close_connection

conn, cur = create_connection()

cur.execute("""CREATE TABLE IF NOT EXISTS InputDate(
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL,
   month TEXT NOT NULL PRIMARY KEY
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS ICU1Duty(
   name TEXT,
   date TEXT NOT NULL PRIMARY KEY
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS ICU2Duty(
   name TEXT,
   date TEXT NOT NULL PRIMARY KEY
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Constraints(
   constraint_id INTEGER PRIMARY KEY AUTOINCREMENT,
   doctor_call_daily INTEGER NOT NULL,
   day_off_monthly INTEGER NOT NULL,
   max_call_month_four INTEGER NOT NULL,
   max_call_month_five INTEGER NOT NULL,
   total_call INTEGER NOT NULL,
   clinic1 INTEGER NOT NULL,
   clinic2 INTEGER NOT NULL,
   amSat_clinic4 INTEGER NOT NULL,
   amSat_clinic1 INTEGER NOT NULL,
   amSat_clinic3 INTEGER NOT NULL,
   p INTEGER NOT NULL
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS PublicHoliday(
   holiday_id INTEGER PRIMARY KEY AUTOINCREMENT,
   holiday_name TEXT NOT NULL,
   holiday_date TEXT NOT NULL,
   holiday_day TEXT NOT NULL
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Roster(
   email TEXT PRIMARY KEY,
   name TEXT NOT NULL,
   first_position TEXT,
   second_position TEXT,
   posting TEXT,
   type TEXT
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Skill(
   email TEXT,
   skill TEXT,
   PRIMARY KEY (email, skill)
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Training(
   training_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   training TEXT NOT NULL,
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Duty(
   duty_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   duty_name TEXT NOT NULL,
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS PriorityLeave(
   pl_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   reason TEXT NOT NULL,
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS LeaveApplication(
   leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL,
   duration TEXT NOT NULL,
   leave_type TEXT NOT NULL,
   remark TEXT
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS LeaveLP(
   leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL,
   duration TEXT NOT NULL,
   leave_type TEXT NOT NULL,
   remark TEXT
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS CallRequest(
   call_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   date TEXT NOT NULL,
   request_type TEXT NOT NULL,
   remark TEXT
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS CallLP(
   call_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   date TEXT NOT NULL,
   request_type TEXT NOT NULL,
   remark TEXT
   );
""")
conn.commit()

close_connection(conn, cur)