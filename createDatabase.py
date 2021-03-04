import sqlite3
from sqlFunctionCalls import create_connection, close_connection

conn, cur = create_connection()

cur.execute("""CREATE TABLE IF NOT EXISTS Constraints(
   constraint_id INTEGER PRIMARY KEY AUTOINCREMENT,
   doctor_call_daily INTEGER NOT NULL,
   day_off_monthly INTEGER NOT NULL,
   max_call_month_four INTEGER NOT NULL,
   max_call_month_five INTEGER NOT NULL
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS PublicHoliday(
   holiday_id INTEGER PRIMARY KEY,
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
   points INTEGER
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Skill(
   email TEXT,
   skill TEXT,
   PRIMARY KEY (email, skill),
   FOREIGN KEY (email) REFERENCES Roster (email)
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Training(
   training_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   training TEXT NOT NULL,
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL,
   FOREIGN KEY (email) REFERENCES Roster (email)
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Duty(
   duty_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   duty_name TEXT NOT NULL,
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL,
   FOREIGN KEY (email) REFERENCES Roster (email)
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS PriorityLeave(
   pl_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   reason TEXT NOT NULL,
   start_date TEXT NOT NULL,
   end_date TEXT NOT NULL,
   FOREIGN KEY (email) REFERENCES Roster (email)
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
   remark TEXT,
   FOREIGN KEY (email) REFERENCES Roster (email)
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
   remark TEXT,
   FOREIGN KEY (email) REFERENCES Roster (email)
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS CallRequest(
   call_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   date TEXT NOT NULL,
   request_type TEXT NOT NULL,
   remark TEXT,
   FOREIGN KEY (email) REFERENCES Roster (email)
   );
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS CallLP(
   call_id INTEGER PRIMARY KEY AUTOINCREMENT,
   email TEXT NOT NULL,
   name TEXT NOT NULL,
   date TEXT NOT NULL,
   request_type TEXT NOT NULL,
   remark TEXT,
   FOREIGN KEY (email) REFERENCES Roster (email)
   );
""")
conn.commit()

close_connection(conn, cur)


#Format Reference: Create table in sqlite
'''
cur.execute("""CREATE TABLE IF NOT EXISTS users(
   userid INT PRIMARY KEY,
   fname TEXT,
   lname TEXT,
   gender TEXT);
""")
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS orders(
   orderid INT PRIMARY KEY,
   date TEXT,
   userid TEXT,
   total TEXT);
""")
conn.commit()
'''