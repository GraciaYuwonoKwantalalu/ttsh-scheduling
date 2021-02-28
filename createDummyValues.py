import sqlite3
from sqlFunctionCalls import create_connection, close_connection

conn, cur = create_connection()

cur.execute("""INSERT OR IGNORE INTO roster(email, name, first_position, second_position, posting, points) 
   VALUES
   ('a@mail.com', 'A', 'A1', 'A2', 'P1', 5),
   ('b@mail.com', 'B', 'B1', 'B2', 'P2', 7)
   ;""")
conn.commit()

#NOTICE: date should be in YYYY-MM-DD format
cur.execute("""INSERT OR IGNORE INTO Training(email, name, training, start_date, end_date) 
   VALUES
   ('a@mail.com', 'A', 'Trial0', '2020-07-21', '2020-07-22'),
   ('b@mail.com', 'B', 'Trial1', '2020-07-21', '2020-08-22'),
   ('c@mail.com', 'C', 'Trial2', '2020-07-10', '2020-07-15'),
   ('d@mail.com', 'D', 'Trial3', '2020-07-13', '2020-07-17'),
   ('f@mail.com', 'F', 'Trial4', '2020-08-16', '2020-08-20')
   ;""")
conn.commit()

cur.execute("""INSERT OR IGNORE INTO Constraints(doctor_call_daily, day_off_monthly, max_call_month_four, max_call_month_five) 
   VALUES (3, 4, 6, 7);""")
conn.commit()

close_connection(conn, cur)

#Format Reference: Insert values in sqlite
'''
cur.execute("""INSERT INTO users(userid, fname, lname, gender) 
   VALUES('00001', 'Nik', 'Piepenbreier', 'male');""")
conn.commit()
'''

#Delete all values in 1 table
'''
cur.execute("""DELETE FROM Constraints;""")
conn.commit()
'''