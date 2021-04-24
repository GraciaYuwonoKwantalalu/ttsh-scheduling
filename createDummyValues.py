import sqlite3
from helperFunctions import create_connection, close_connection

# ASSUME 2020-07-16 --> 2020-08-15 IS THE PERIOD OF SCHEDULING

# Create connection to DB
conn, cur = create_connection()

# Table for the doctor roster
cur.execute("""INSERT OR IGNORE INTO Roster(email, name, first_position, second_position, posting, type) 
   VALUES
   ('V', 'A', 'A1', 'A2', 'P1', 'S'),
   ('W', 'B', 'B1', 'B2', 'P2', 'S'),
   ('X', 'C', 'C1', 'C2', 'P3', 'S'),
   ('Y', 'D', 'D1', 'D2', 'P4', 'S'),
   ('Z', 'E', 'E1', 'E2', 'P5', 'S'),
   ('A', 'F', 'F1', 'F2', 'P6', 'S'),
   ('B', 'G', 'G1', 'G2', 'P7', 'S'), 
   ('C', 'H', 'H1', 'H2', 'P8', 'S'),
   ('D', 'I', 'I1', 'I2', 'P9', 'S'),
   ('E', 'J', 'J1', 'J2', 'P10', 'S'),
   ('F', 'K', 'K1', 'K2', 'P11', 'S'),
   ('G', 'L', 'L1', 'L2', 'P12', 'S'),
   ('H', 'M', 'M1', 'M2', 'P13', 'S'),
   ('I', 'N', 'N1', 'N2', 'P14', 'S'),
   ('J', 'O', 'O1', 'O2', 'P15', 'J'),
   ('K', 'P', 'P1', 'P2', 'P16', 'J'),
   ('L', 'Q', 'Q1', 'Q2', 'P17', 'J'),
   ('M', 'R', 'R1', 'R2', 'P18', 'J'),
   ('N', 'S', 'S1', 'S2', 'P19', 'J'),
   ('O', 'T', 'T1', 'T2', 'P20', 'J'),
   ('P', 'U', 'U1', 'U2', 'P21', 'J'),
   ('Q', 'V', 'V1', 'V2', 'P22', 'J'),
   ('R', 'W', 'W1', 'W2', 'P23', 'J'),
   ('S', 'X', 'X1', 'X2', 'P24', 'J'),
   ('T', 'Y', 'Y1', 'Y2', 'P25', 'J'),
   ('U', 'Z', 'Z1', 'Z2', 'P26', 'J')
   ;""")
conn.commit()

# Table for the doctor's skills
cur.execute("""INSERT OR IGNORE INTO Skill(email, skill) 
   VALUES
   ('A', 'Skill1'),
   ('B', 'Skill2'),
   ('C', 'Skill3'),
   ('D', 'Skill4'),
   ('E', 'Skill5'),
   ('F', 'Skill6'),
   ('G', 'Skill7'),  
   ('H', 'Skill8'),
   ('I', 'Skill9'), 
   ('J', 'Skill10'),
   ('K', 'Skill11'),
   ('L', 'Skill12'),
   ('M', 'Skill13'),
   ('N', 'Skill14'),
   ('O', 'Skill15'),
   ('P', 'Skill16'),
   ('Q', 'Skill17'),
   ('R', 'Skill18'),
   ('S', 'Skill19'),
   ('T', 'Skill20'),
   ('U', 'Skill21'),
   ('V', 'Skill22'),
   ('W', 'Skill23'),
   ('X', 'Skill24'),
   ('Y', 'Skill25'),
   ('Z', 'Skill26'),
   ('A', 'Skill27'),
   ('B', 'Skill28'),
   ('C', 'Skill29'),
   ('D', 'Skill30')
   ;""")
conn.commit()

# NOTICE: date should be in YYYY-MM-DD format
cur.execute("""INSERT OR IGNORE INTO Training(email, name, training, start_date, end_date) 
   VALUES
   ('Z', 'Z', 'Trianing0', '2020-07-21', '2020-07-22'),
   ('Y', 'Y', 'Trianing1', '2020-07-21', '2020-08-22'),
   ('X', 'X', 'Trianing2', '2020-07-10', '2020-07-15'),
   ('W', 'W', 'Trianing3', '2020-07-13', '2020-07-17'),
   ('V', 'V', 'Trianing4', '2020-08-16', '2020-08-20')
   ;""")
conn.commit()

# NOTICE: date should be in YYYY-MM-DD format
cur.execute("""INSERT OR IGNORE INTO Duty(email, name, duty_name, start_date, end_date) 
   VALUES
   ('A', 'A', 'ICU 1', '2020-07-16', '2020-08-15'),
   ('B', 'B', 'ICU 2', '2020-07-13', '2020-07-17'),
   ('C', 'C', 'ICU 3', '2020-07-16', '2020-07-18'),
   ('D', 'D', 'ICU 4', '2020-08-14', '2020-08-16'),
   ('E', 'E', 'Clinic 1', '2020-08-17', '2020-08-18'),
   ('F', 'F', 'Clinic 2', '2020-07-11', '2020-07-15'),
   ('G', 'G', 'Clinic 3', '2020-07-21', '2020-07-22'),
   ('H', 'H', 'Clinic 4', '2020-07-29', '2020-07-30'),
   ('I', 'I', 'amSat Clinic 1', '2020-07-17', '2020-08-18'),
   ('J', 'J', 'amSat Clinic 2', '2020-08-11', '2020-08-12'),
   ('K', 'K', 'amSat Clinic 3', '2020-08-17', '2020-07-18'),
   ('L', 'L', 'amSat Clinic 4', '2020-07-21', '2020-08-22'),
   ('M', 'M', 'p', '2020-07-21', '2020-08-22')
   ;""")
conn.commit()

# NOTICE: date should be in YYYY-MM-DD format
cur.execute("""INSERT OR IGNORE INTO PriorityLeave(email, name, reason, start_date, end_date) 
   VALUES
   ('G', 'G', 'MC', '2020-07-23', '2020-07-23'),
   ('H', 'H', 'Reservist', '2020-07-14', '2020-07-28'),
   ('I', 'I', 'Compassionate Leave', '2020-07-12', '2020-07-16'),
   ('J', 'J', 'Reservist', '2020-08-14', '2020-08-28'),
   ('K', 'K', 'Reservist', '2020-07-02', '2020-07-16'),
   ('N', 'N', 'Operation Recovery', '2020-07-14', '2020-09-14')
   ;""")
conn.commit()

# This table data should be obtained from employee emails 
cur.execute("""INSERT OR IGNORE INTO LeaveApplication(email, name, start_date, end_date, duration, leave_type, remark) 
   VALUES
   ('O', 'O', '2020-03-23', '2020-03-23', 'PM', 'Child Care Leave', 'PSLE Results Collection'),
   ('P', 'P', '2020-02-25', '2020-03-25', 'AM', 'Others', 'Medical Appointment'),
   ('Q', 'Q', '2020-03-17', '2020-03-17', 'Whole Day', 'MC/Hospitalisation Leave', 'Flu'),
   ('R', 'R', '2020-03-16', '2020-03-19', 'Whole Day', 'Maternity Leave', NULL),
   ('S', 'S', '2020-03-13', '2020-03-15', 'Whole Day', 'Paternity Leave', NULL),
   ('T', 'T', '2020-04-12', '2020-04-17', 'Whole Day', 'Marriage Leave', NULL),
   ('U', 'U', '2020-03-15', '2020-03-20', 'Whole Day', 'Annual Leave', 'Holiday')
   ;""")
conn.commit()

# This table data should be obtained from employee emails 
cur.execute("""INSERT OR IGNORE INTO CallRequest(email, name, date, request_type, remark) 
   VALUES
   ('V', 'V', '2020-07-21', 'No call only', 'Busy'),
   ('W', 'W', '2020-07-21', 'No call & no weekend duty', 'Very busy'),
   ('X', 'X', '2020-07-21', 'On Call', NULL)
   ;""")
conn.commit()

# Original Constraints set by admin
cur.execute("""INSERT OR IGNORE INTO Constraints(doctor_call_daily, day_off_monthly, max_call_month_four, max_call_month_five,
   total_call, clinic_1, clinic_2, amSat_clinic_4, amSat_clinic_1, amSat_clinic_3, P) 
   VALUES (3, 4, 6, 7, 3, 2, 1, 2, 1, 1, 3);""")
conn.commit()

# Table for public holidays in 2020
cur.execute("""INSERT OR IGNORE INTO PublicHoliday(holiday_name, holiday_date, holiday_day) 
   VALUES 
   ('New Years Day', '2020-01-01', 'Wednesday'),
   ('Chinese New Year', '2020-01-25', 'Saturday'),
   ('Chinese New Year', '2020-01-26', 'Sunday'),
   ('Good Friday', '2020-04-10', 'Friday'),
   ('Labour Day', '2020-05-01', 'Friday'),
   ('Hari Raya Puasa', '2020-05-24', 'Sunday'),
   ('Vesak Day', '2020-05-07', 'Thursday'),
   ('Hari Raya Haji', '2020-07-31', 'Friday'),
   ('National Day', '2020-08-09', 'Sunday'),
   ('Deepavali', '2020-11-14', 'Saturday'),
   ('Christmas Day', '2020-12-25', 'Friday')
   ;""")
conn.commit()

# Close connection to DB
close_connection(conn, cur)