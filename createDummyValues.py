import sqlite3
from helperFunctions import create_connection, close_connection

# ASSUME 2020-07-16 --> 2020-08-15 IS THE PERIOD OF SCHEDULING

# Create connection to DB
conn, cur = create_connection()

# Table for the doctor roster
cur.execute("""INSERT OR IGNORE INTO Roster(email, name, first_position, second_position, posting, type) 
   VALUES
   ('a@mail.com', 'A', 'A1', 'A2', 'P1', 'S'),
   ('b@mail.com', 'B', 'B1', 'B2', 'P2', 'S'),
   ('c@mail.com', 'C', 'C1', 'C2', 'P3', 'S'),
   ('d@mail.com', 'D', 'D1', 'D2', 'P4', 'S'),
   ('e@mail.com', 'E', 'E1', 'E2', 'P5', 'S'),
   ('f@mail.com', 'F', 'F1', 'F2', 'P6', 'S'),
   ('g@mail.com', 'G', 'G1', 'G2', 'P7', 'S'), 
   ('h@mail.com', 'H', 'H1', 'H2', 'P8', 'S'),
   ('i@mail.com', 'I', 'I1', 'I2', 'P9', 'S'),
   ('j@mail.com', 'J', 'J1', 'J2', 'P10', 'S'),
   ('k@mail.com', 'K', 'K1', 'K2', 'P11', 'S'),
   ('l@mail.com', 'L', 'L1', 'L2', 'P12', 'S'),
   ('m@mail.com', 'M', 'M1', 'M2', 'P13', 'S'),
   ('n@mail.com', 'N', 'N1', 'N2', 'P14', 'S'),
   ('o@mail.com', 'O', 'O1', 'O2', 'P15', 'J'),
   ('p@mail.com', 'P', 'P1', 'P2', 'P16', 'J'),
   ('q@mail.com', 'Q', 'Q1', 'Q2', 'P17', 'J'),
   ('r@mail.com', 'R', 'R1', 'R2', 'P18', 'J'),
   ('s@mail.com', 'S', 'S1', 'S2', 'P19', 'J'),
   ('t@mail.com', 'T', 'T1', 'T2', 'P20', 'J'),
   ('u@mail.com', 'U', 'U1', 'U2', 'P21', 'J'),
   ('v@mail.com', 'V', 'V1', 'V2', 'P22', 'J'),
   ('w@mail.com', 'W', 'W1', 'W2', 'P23', 'J'),
   ('x@mail.com', 'X', 'X1', 'X2', 'P24', 'J'),
   ('y@mail.com', 'Y', 'Y1', 'Y2', 'P25', 'J'),
   ('z@mail.com', 'Z', 'Z1', 'Z2', 'P26', 'J')
   ;""")
conn.commit()

# Table for the doctor's skills
cur.execute("""INSERT OR IGNORE INTO Skill(email, skill) 
   VALUES
   ('a@mail.com', 'Skill1'),
   ('b@mail.com', 'Skill2'),
   ('c@mail.com', 'Skill3'),
   ('d@mail.com', 'Skill4'),
   ('e@mail.com', 'Skill5'),
   ('f@mail.com', 'Skill6'),
   ('g@mail.com', 'Skill7'),  
   ('h@mail.com', 'Skill8'),
   ('i@mail.com', 'Skill9'), 
   ('j@mail.com', 'Skill10'),
   ('k@mail.com', 'Skill11'),
   ('l@mail.com', 'Skill12'),
   ('m@mail.com', 'Skill13'),
   ('n@mail.com', 'Skill14'),
   ('o@mail.com', 'Skill15'),
   ('p@mail.com', 'Skill16'),
   ('q@mail.com', 'Skill17'),
   ('r@mail.com', 'Skill18'),
   ('s@mail.com', 'Skill19'),
   ('t@mail.com', 'Skill20'),
   ('u@mail.com', 'Skill21'),
   ('v@mail.com', 'Skill22'),
   ('w@mail.com', 'Skill23'),
   ('x@mail.com', 'Skill24'),
   ('y@mail.com', 'Skill25'),
   ('z@mail.com', 'Skill26'),
   ('a@mail.com', 'Skill27'),
   ('b@mail.com', 'Skill28'),
   ('c@mail.com', 'Skill29'),
   ('d@mail.com', 'Skill30')
   ;""")
conn.commit()

#Table for doctor's points
cur.execute("""INSERT OR IGNORE INTO Points(email, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12) 
   VALUES
   ('a@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('b@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('c@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('d@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('e@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('f@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('g@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),  
   ('h@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('i@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'), 
   ('j@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('k@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('l@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('m@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('n@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('o@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('p@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('q@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('r@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('s@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('t@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('u@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('v@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('w@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('x@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('y@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'),
   ('z@mail.com', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0')
   ;""")
conn.commit()

# NOTICE: date should be in YYYY-MM-DD format
cur.execute("""INSERT OR IGNORE INTO Training(email, name, training, start_date, end_date) 
   VALUES
   ('z@mail.com', 'Z', 'Trianing0', '2020-07-21', '2020-07-22'),
   ('y@mail.com', 'Y', 'Trianing1', '2020-07-21', '2020-08-22'),
   ('x@mail.com', 'X', 'Trianing2', '2020-07-10', '2020-07-15'),
   ('w@mail.com', 'W', 'Trianing3', '2020-07-13', '2020-07-17'),
   ('v@mail.com', 'V', 'Trianing4', '2020-08-16', '2020-08-20')
   ;""")
conn.commit()

# NOTICE: date should be in YYYY-MM-DD format
cur.execute("""INSERT OR IGNORE INTO Duty(email, name, duty_name, start_date, end_date) 
   VALUES
   ('a@mail.com', 'A', 'ICU 1', '2020-07-16', '2020-08-15'),
   ('b@mail.com', 'B', 'ICU 2', '2020-07-13', '2020-07-17'),
   ('c@mail.com', 'C', 'ICU 3', '2020-07-16', '2020-07-18'),
   ('d@mail.com', 'D', 'ICU 4', '2020-08-14', '2020-08-16'),
   ('e@mail.com', 'E', 'Clinic 1', '2020-08-17', '2020-08-18'),
   ('f@mail.com', 'F', 'Clinic 2', '2020-07-11', '2020-07-15'),
   ('g@mail.com', 'G', 'Clinic 3', '2020-07-21', '2020-07-22'),
   ('h@mail.com', 'H', 'Clinic 4', '2020-07-29', '2020-07-30'),
   ('i@mail.com', 'I', 'amSat Clinic 1', '2020-07-17', '2020-08-18'),
   ('j@mail.com', 'J', 'amSat Clinic 2', '2020-08-11', '2020-08-12'),
   ('k@mail.com', 'K', 'amSat Clinic 3', '2020-08-17', '2020-07-18'),
   ('l@mail.com', 'L', 'amSat Clinic 4', '2020-07-21', '2020-08-22'),
   ('m@mail.com', 'M', 'p', '2020-07-21', '2020-08-22')
   ;""")
conn.commit()

# NOTICE: date should be in YYYY-MM-DD format
cur.execute("""INSERT OR IGNORE INTO PriorityLeave(email, name, reason, start_date, end_date) 
   VALUES
   ('g@mail.com', 'G', 'MC', '2020-07-23', '2020-07-23'),
   ('h@mail.com', 'H', 'Reservist', '2020-07-14', '2020-07-28'),
   ('i@mail.com', 'I', 'Compassionate Leave', '2020-07-12', '2020-07-16'),
   ('j@mail.com', 'J', 'Reservist', '2020-08-14', '2020-08-28'),
   ('k@mail.com', 'K', 'Reservist', '2020-07-02', '2020-07-16'),
   ('n@mail.com', 'N', 'Operation Recovery', '2020-07-14', '2020-09-14')
   ;""")
conn.commit()

# This table data should be obtained from employee emails 
cur.execute("""INSERT OR IGNORE INTO LeaveApplication(email, name, start_date, end_date, duration, leave_type, remark) 
   VALUES
   ('o@mail.com', 'O', '2020-07-23', '2020-07-23', 'PM', 'Child Care Leave', 'PSLE Results Collection'),
   ('p@mail.com', 'P', '2020-07-25', '2020-07-25', 'AM', 'Others', 'Medical Appointment'),
   ('q@mail.com', 'Q', '2020-07-17', '2020-07-17', 'Whole Day', 'MC/Hospitalisation Leave', 'Flu'),
   ('r@mail.com', 'R', '2020-07-16', '2020-07-19', 'Whole Day', 'Maternity Leave', NULL),
   ('s@mail.com', 'S', '2020-08-13', '2020-08-15', 'Whole Day', 'Paternity Leave', NULL),
   ('t@mail.com', 'T', '2020-08-12', '2020-08-17', 'Whole Day', 'Marriage Leave', NULL),
   ('u@mail.com', 'U', '2020-07-15', '2020-07-20', 'Whole Day', 'Annual Leave', 'Holiday')
   ;""")
conn.commit()

# This table data should be obtained from employee emails 
cur.execute("""INSERT OR IGNORE INTO CallRequest(email, name, date, request_type, remark) 
   VALUES
   ('v@mail.com', 'V', '2020-07-21', 'No call only', 'Busy'),
   ('w@mail.com', 'W', '2020-07-21', 'No call & no weekend duty', 'Very busy'),
   ('x@mail.com', 'X', '2020-07-21', 'On Call', NULL)
   ;""")
conn.commit()

# Original Constraints set by admin
cur.execute("""INSERT OR IGNORE INTO Constraints(doctor_call_daily, day_off_monthly, max_call_month_four, max_call_month_five,total_call,clinic1,clinic2,amSat_clinic4,amSat_clinic1,amSat_clinic3,p) 
   VALUES (3, 4, 6, 7, 3, 2, 1, 2, 1, 1, 3);""")
conn.commit()

# Table for public holidays in 2021
# cur.execute("""INSERT OR IGNORE INTO PublicHoliday(holiday_name, holiday_date, holiday_day) 
#    VALUES 
#    ('New Years Day', '2020-01-01', 'Wednesday'),
#    ('Chinese New Year', '2020-01-25', 'Saturday'),
#    ('Chinese New Year', '2020-01-26', 'Sunday'),
#    ('Good Friday', '2020-04-10', 'Friday'),
#    ('Labour Day', '2020-05-01', 'Friday'),
#    ('Hari Raya Puasa', '2020-05-24', 'Sunday'),
#    ('Vesak Day', '2020-05-07', 'Thursday'),
#    ('Hari Raya Haji', '2020-07-31', 'Friday'),
#    ('National Day', '2020-08-09', 'Sunday'),
#    ('Deepavali', '2020-11-14', 'Saturday'),
#    ('Christmas Day', '2020-12-25', 'Friday')
#    ;""")
# conn.commit()

# Close connection to DB
close_connection(conn, cur)