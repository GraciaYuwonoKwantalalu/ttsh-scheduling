import pulp, datetime, holidays
import pandas as pd
from pulp import *
from datetime import date, timedelta, datetime
from helperFunctions import create_connection, close_connection, readRoster, readCallRequest, readLeaveApplication, readtraining, readDuties, readpleave, readPrevCalls
from pprint import pprint

def generalmatrix(excelsheet_result,doc_list,sdate,edate,delta):
    """
    Reads from the excel_result variables and displays in matrix format.

    :parameters: excelsheet_result, name, start date, end date, delta. 
    :return: list 
    """

    combined_list = []

    for doc in doc_list:
        doctor_monthly_activity = []
        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)             # 2020-08-02 (datetime object format)

            if doc in excelsheet_result:
                checking_flag = False
                for sdates,detailed in excelsheet_result[doc].items():
                    sdateo = datetime.strptime(sdates, '%Y-%m-%d').date()
                    edateo = datetime.strptime(detailed[2], '%Y-%m-%d').date()
                    if day >= sdateo and day <= edateo:
                        checking_flag = True

                if checking_flag == False:
                    doctor_monthly_activity.append(0)
                else:
                    doctor_monthly_activity.append(1) 

            else:
                doctor_monthly_activity.append(0)

        combined_list.append(doctor_monthly_activity)
    
    return combined_list

def call_matrix(doc_list,query_start_date,query_last_date,delta):
    """
    Generates the call matrix for *run_lp()*.

    :parameters: name, start date, end date, delta. 
    :return: list 
    """

    # List to store the matrix for LP
    combined_list = []

    # Convert datetime objects to string format to query DB
    string_start_date = query_start_date.strftime("%Y-%m-%d")
    string_end_date = query_last_date.strftime("%Y-%m-%d")

    # Obtain the call requests from DB
    cr_dict = readCallRequest(string_start_date,string_end_date)

    # Reading from last 2 day's previous month data from excel
    prev_call_list = readPrevCalls()        # Format: [[A,B,C],[D,E]] where 1st array is 2nd last day of previous month and 2nd array is last day of previous month

    # Creating the call matrix for the request month
    for doc in doc_list:
        doctor_monthly_activity = []
        day_counter = 0
        prev_flag = False       # Means that user does not have calls within the last 2 days of the previous schedule month
        clear_flag = False      # Means that user is no longer constrained by the call restriction of "no every other day call"
        for i in range(delta.days + 1):
            day = query_start_date + timedelta(days=i)             # 2020-08-02 (datetime object format)

            # checks the "no every other day call" constraint from previous month's schedule (last 2 days)
            if day_counter < 2 and prev_flag == False:  
                # When the doctor has done a call in the 2nd last day of the previous month            
                if doc in prev_call_list[0]:
                    doctor_monthly_activity.append(3)
                    prev_flag = True
                # When the doctor has done a call in the last day of the previous month    
                elif doc in prev_call_list[1]:
                    doctor_monthly_activity.append(3)
                # When the doctor has not done a call in the 2nd last day and last day of the previous month    
                else:
                    clear_flag = True
            # When the doctor has cleared the "no every other day call" constraint from previous month's schedule (last 2 days)
            elif prev_flag == True or day_counter >= 2:
                clear_flag = True

            # When a doctor has submitted a FormSG call request and is not constrained by the call restriction of "no every other day call"
            if (clear_flag == True) and (doc in cr_dict):
                temp_list = []
                for sdates,detailed in cr_dict[doc].items():
                    sdateo = datetime.strptime(sdates, '%Y-%m-%d').date()   # 2020-08-02 (datetime object format)

                    # For the current date: Doctor has mentioned this date in the FormSG
                    if (day == sdateo):
                        # Doctor wants call (Positive)
                        if detailed[1] == "OnCall":
                            temp_list.append(2)
                        # Doctor specify to not have call (Negative)
                        elif "NoCallOnly" in detailed[1]:
                            temp_list.append(1)
                        # Doctor specify to not have call (Negative)
                        elif "NoCall&NoWeekendDuty" in detailed[1]:
                            temp_list.append(1)
                    # For the current date: Doctor did not specify whether they want call or don't want call in the FormSG (Neutral)
                    else:
                        temp_list.append(0)   

                # Ensure the cr_dict containing multiple entries for each doctor loops once for each day only
                if 2 in temp_list:
                    doctor_monthly_activity.append(2)
                elif 1 in temp_list:
                    doctor_monthly_activity.append(1)
                else:
                    doctor_monthly_activity.append(0)

            # When a doctor did not submit a FormSG call request
            elif (clear_flag == True) and (doc not in cr_dict):   
                doctor_monthly_activity.append(0)

            # Used for tracking the first 2 days of the current selected schedule month
            day_counter += 1            

        combined_list.append(doctor_monthly_activity)

    return combined_list

def leave_matrix(doc_list,query_start_date,query_last_date,delta):
    """
    Generates the leave matrix for *run_lp()*.

    :parameters: name, start date, end date, delta. 
    :return: list 
    """

    # List to store the matrix for LP
    combined_list = []

    # Convert datetime objects to string format to query DB
    string_start_date = query_start_date.strftime("%Y-%m-%d")
    string_end_date = query_last_date.strftime("%Y-%m-%d")

    # Obtain the leave application from DB
    la_dict = readLeaveApplication(string_start_date, string_end_date)

    for doc in doc_list:
        doctor_monthly_activity = []
        for i in range(delta.days + 1):
            day = query_start_date + timedelta(days=i)             # 2020-08-02 (datetime object format)

            if doc in la_dict:
                checking_flag = False
                for sdates,detailed in la_dict[doc].items():
                    sdateo = datetime.strptime(sdates, '%Y-%m-%d').date()
                    edateo = datetime.strptime(detailed[2], '%Y-%m-%d').date()
                    if day >= sdateo and day <= edateo:
                        checking_flag = True

                if checking_flag == False:
                    doctor_monthly_activity.append(0)
                else:
                    doctor_monthly_activity.append(1) 

            else:
                doctor_monthly_activity.append(0)

        combined_list.append(doctor_monthly_activity)

    return combined_list

def sg_holidays(whichYear,weekDays):
    """
    Obtains the holidays in Singapore.

    :parameters: year, weekdays. 
    :return: list 
    """

    whichYear = int(whichYear)
    
    sg_Holiday = []
    
    for holiday in sorted(holidays.Singapore(years=whichYear).items()):
        ### get the day of that week
        holiday_date = holiday[0]
        holiday_day = holiday_date.weekday()
        holiday_weekday = weekDays[holiday_day]
          
        ### public holiday
        case = {
            "HolidayName":holiday[1],
            "HolidayDate":format(holiday[0]),
            "HolidayDay":format(holiday_weekday) 
        }
        sg_Holiday.append(case)
               
        ### get the holiday eve date
        holiday_eve_date = holiday_date - timedelta(days=1)
        
        ### get the day of that week
        holiday_eve_day = holiday_eve_date.weekday()
        holiday_eve_weekday = weekDays[holiday_eve_day]
        
        ### get the date in str
        holiday_eve_date = str(holiday_eve_date)
        holiday_eve_date = holiday_eve_date.split(" ")
        
        ### public holiday eve 
        case2 = {
            "HolidayName":holiday[1] + " eve",
            "HolidayDate":holiday_eve_date[0],
            "HolidayDay":format(holiday_eve_weekday)
        }
        sg_Holiday.append(case2)
        
    return sg_Holiday

def run_lp(doctor_call_daily, day_off_monthly, max_call_month_4, max_call_month_5, query_start_date, query_last_date, doc_list, doc_email_list, A, B, C, D):
    """
    Generates schedule for the doctors according to the constraints. 

    :parameters: constraints, start date, end date, name, email 
    :return: dictionary 
    """

    # Changing dates from text to datetime object format
    sdate = datetime.strptime(query_start_date, '%Y-%m-%d').date()   # start date
    edate = datetime.strptime(query_last_date, '%Y-%m-%d').date()   # end date
    delta = edate - sdate       # as timedelta

    # Calling the matrix function with the appropriate inputs
    combined_training = generalmatrix(B,doc_list,sdate,edate,delta)
    combined_duty = generalmatrix(C,doc_list,sdate,edate,delta)
    combined_pleave = generalmatrix(D,doc_list,sdate,edate,delta)
    combined_call = call_matrix(doc_email_list,sdate,edate,delta)
    combined_leave = leave_matrix(doc_email_list,sdate,edate,delta)

    request=[]
    doc=[]

    for i in range(0,len(combined_call)):
        for k in range(0,len(combined_call[i])):
            if combined_leave[i][k]==1:
                doc.append(1.5)
            elif combined_call[i][k]==1:
                doc.append(1.5)
            elif combined_call[i][k]==2:
                doc.append(0.5)
            elif combined_call[i][k]==3:
                doc.append(100)
            else:
                doc.append(1)
        request.append(doc)
        doc=[]
    
    # First position of Doctors
    MO1=[]
    MO2=[]
    MO3=[]
    Doctors=[]  # email

    for key in A:
        Doctors.append(key)

    for key in A:
        if A[key][1]=="MO1":
            MO1.append(key)
        elif A[key][1]=="MO2":
            MO2.append(key)
        elif A[key][1]=="MO3":
            MO3.append(key)
    
    weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

    dates_between_Start_N_End_Date = []
    dates_info = []
    pointsList = []
    yearList = []
    loopday =[]
    weekends =[]
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        dateOnly = day.strftime("%Y-%m-%d")
        dates_between_Start_N_End_Date.append(dateOnly)
        yearOnly = day.strftime("%Y")
        yearOnlyInt = int(yearOnly)
        mthOnly = day.strftime("%m")
        dayOnly = day.strftime("%d")

        day = day.weekday()
        weekdayOnly = weekDays[day]
        
        case = {
            "HolidayDate":dateOnly,
            "yearInt":yearOnlyInt,
            "year":yearOnly,
            "mth":mthOnly,
            "day":dayOnly,
            "weekday":weekdayOnly
        }
        
        dates_info.append(case)
        
        if yearOnly not in yearList:
            yearList.append(yearOnly)

    holidate=[]
    for i in dates_info:
        weekdayOnly = i['weekday']
        pointScore = 0
        loopday.append(weekdayOnly)
        if weekdayOnly == "Monday":
            pointScore = 1
        elif weekdayOnly == "Tuesday":
            pointScore = 1
        elif weekdayOnly == "Wednesday":
            pointScore = 1
        elif weekdayOnly == "Thursday":
            pointScore = 1
        elif weekdayOnly == "Friday":
            pointScore = 1.5
        elif weekdayOnly == "Saturday":
            pointScore = 2
        elif weekdayOnly == "Sunday":
            pointScore = 3
        
        for k in yearList:
            for j in sg_holidays(k,weekDays):
                if i['HolidayDate'] in j['HolidayDate']:
                    if 'eve' in str(j['HolidayName']):
                        pointScore = 2.5
                    else:
                        pointScore = 3
                        holidate.append(j['HolidayDate'])             
                else:
                    pass
        
        pointsList.append(pointScore)

    points=[]
    friday=[] 
    saturday=[] 
    sunday=[]
    holidayDay=[]
    SatSun=[]
    dicts=A
    for i in range(0,len(dicts)): 
        points.append(pointsList)

    Days=[]
    for i in range(1,delta.days+2):
        Days.append(i)

    for i in range(delta.days+1):
        if(loopday[i]=="Friday" or loopday[i]=="Saturday" or loopday[i]=="Sunday"):
            weekends.append(Days[i]) 
        if(loopday[i]=="Saturday" or loopday[i]=="Sunday"):
            SatSun.append(Days[i])
        if(loopday[i]=="Friday"):
            friday.append(Days[i]) 
        if(loopday[i]=="Saturday"): 
            saturday.append(Days[i]) 
        if(loopday[i]=="Sunday"):
            sunday.append(Days[i])
    for i in holidate: 
        holidayDay.append(dates_between_Start_N_End_Date.index(i)+1)

    #Vector to assign points per day to each doctor. (refer to line 10)
    Points = points

    # The points data is made into a dictionary
    Points = makeDict([Doctors,Days],Points,0)

    # Vector to assign priority per day to each doctor. (refer to line 6) 
    Requests = request

    # The request data is made into a dictionary
    Requests = makeDict([Doctors,Days],Requests,0)

    # The duty data is made into a dictionary
    #from read_duty import combined_duty
    combined_duty = makeDict([Doctors,Days],combined_duty,0)


    # The training data is made into a dictionary
    combined_training = makeDict([Doctors,Days],combined_training,0)

    # The Priorityleaves data is made into a dictionary
    combined_pleave = makeDict([Doctors,Days],combined_pleave,0)

    # Creates the 'prob' variable to contain the problem data
    prob = LpProblem("Hospital_Scheduling",LpMinimize)

    #Create a list of tuples containing all the possible assignment of days to doctor
    Assignment = [(i,j) for i in Doctors for j in Days]


    # A dictionary called 'Vars' is created to contain the referenced variables(the assignment)
    vars = LpVariable.dicts("Assignment", (Doctors, Days), 0, None, LpBinary)
    
    # The objective function is added to 'prob' first
    prob += lpSum([vars[i][j]*Requests[i][j] for (i,j) in Assignment]), "Sum_of_Calls"

    #Constraints

    #Fairness Contraint 
    for i in Doctors:
        #for j in Days:
        prob+= lpSum([vars[i][j]*Points[i][j] for j in Days]) - lpSum([vars[i][j]*Points[i][j] for (i,j) in Assignment])/len(Doctors) <= 3

    for i in Doctors:
        #for j in Days:
        prob+= lpSum([vars[i][j]*Points[i][j] for j in Days]) - lpSum([vars[i][j]*Points[i][j] for (i,j) in Assignment])/len(Doctors) >= -3

    #One doctor can only have 7 calls in a 31 days month (changed)
    for i in Doctors:
        if len(Days) <= 28:
            lpSum([vars[i][j] for j in Days])<=max_call_month_4, "Sum_of_Calls_per_doctors_%s"%i
        else:
            lpSum([vars[i][j] for j in Days])<=max_call_month_5, "Sum_of_Calls_per_doctors_%s"%i

    #3 doctor are to be on call each day
    for j in Days:
        prob += lpSum([vars[i][j] for i in Doctors])==doctor_call_daily, "Sum_of_Doctors_per_calls%s"%j 

    #priority leaves
    for i in Doctors:
        for j in Days:
            prob+= lpSum([vars[i][j]]) <= 1 - lpSum([combined_pleave[i][j]])

    #no calls on days of duty 
    for i in Doctors:
        for j in Days:
            prob+= lpSum([vars[i][j]]) <= 1 - lpSum([combined_duty[i][j]])

    #no calls on days of training 
    for i in Doctors:
        for j in Days:
            prob+= lpSum([vars[i][j]]) <= 1 - lpSum([combined_training[i][j]])

    #calling of first position (changed)
    for j in Days:
            prob += lpSum(vars[i][j] for i in MO1) <= 1

    for j in Days:
        prob += lpSum(vars[i][j] for i in MO3) <= 1

    for j in Days:
        if lpSum(vars[i][j] for i in MO1) == 1 and lpSum(vars[i][j] for i in MO3) == 1:
            lpSum(vars[i][j] for i in MO2) == 1
        else:
            lpSum(vars[i][j] for i in MO2) == 3

    #no post call on day of duty 
    for i in Doctors:
        for j in Days:
            prob += lpSum(vars[i][j]) <= 1 - lpSum(combined_duty[i][j+1])

    #no every other day call (changed)
    for i in Doctors:
        for j in range(3,len(Days)):
            prob += lpSum(vars[i][j-1] + vars[i][j-2]) <= 1 - lpSum(vars[i][j])

    #doctor should have 4 days off in 4 weeks, post call day is not off (changed)
    for i in Doctors:
        prob += len(SatSun) + len(holidayDay) + lpSum([combined_pleave[i][j]]) - lpSum(vars[i][j] for j in holidayDay) - lpSum(vars[i][j] for j in friday) - lpSum(vars[i][j] for j in saturday)*2 - lpSum(vars[i][j] for j in sunday) - lpSum([combined_duty[i][j]]) - lpSum([combined_training[i][j]]) >= day_off_monthly

    #at most one call on a friday/sat/sun
    for i in Doctors:
            prob += lpSum (vars[i][j] for j in weekends) <= 1

    # The problem data is written to an .lp file
    prob.writeLP("Hospital_Scheduling.lp")

    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    # The status of the solution is printed to the command prompt
    # print ("Status:", LpStatus[prob.status])

    # Each of the variables is printed with it's resolved optimum value (added new till end)
    lpDict={}

    for v in prob.variables():
        doc = v.name.split("_")[1]
        day= int(v.name.split("_")[2])
        output=int(v.varValue)
        if doc not in lpDict:
            lpDict[doc]=[[day,output]]
        else:
            lpDict[doc].append([day,output])

    def Sort(sub_li):
        l = len(sub_li)
        for i in range(0, l):
            for j in range(0, l-i-1):
                if (sub_li[j][0] > sub_li[j + 1][0]):
                    tempo = sub_li[j]
                    sub_li[j]= sub_li[j + 1]
                    sub_li[j + 1]= tempo
        return sub_li
    
    # Sort Array according to day
    for key in lpDict:
        lpDict[key] = Sort(lpDict[key])

    # output with date for database
    lpDict2= lpDict

    # getting call array from LP output & changing of day to date
    callArray=[] #call1
    docArray=[]
    for key in lpDict2:
        for i in range(0,len(lpDict2[key])):
            docArray.append(lpDict2[key][i][1])
            lpDict2[key][i][0]=dates_between_Start_N_End_Date[(lpDict2[key][i][0])-1]
        callArray.append(docArray)
        docArray=[]
    # pprint(lpDict2)
    return lpDict2
