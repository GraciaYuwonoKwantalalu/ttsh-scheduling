from datetime import date, timedelta, datetime
import dateutil.parser
from win32com.client import Dispatch
from pprint import pprint
import json
from time import strptime
import sqlite3
from helperFunctions import create_connection, close_connection, check_weekend, check_day, check_month_num, is_constraint_met, readRoster, readDuties, readtraining, readpleave, readPh, clashes, exportPoints, exportSchedule, exportICU1Duty, exportICU2Duty

def email_json():

    outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
    root_folder = outlook.Folders.Item(1)   

    ### customised folder name = 'test'
    test_folder = root_folder.Folders['test']
    emails = test_folder.Items

    email_list = []
    email_body_list = []    # list for email body
    needed_emails = []
    latest_emails = []
    check_latest = []

    count = 0

    #start_dateA = datetime.datetime(2020, 10, 1)
    #start_date = start_dateA.strftime("%Y-%m-%d")
    start_dateA = '2020-10-01'
    start_dateA = datetime.strptime(start_dateA, '%Y-%m-%d').strftime('%Y-%m-%d')
    start_date = start_dateA.split('-')
    start_date_mth, start_date_year = start_date[1], start_date[0]

    #end_dateA = datetime.datetime(2021, 12, 1)
    #end_date = end_dateA.strftime("%Y-%m-%d")
    end_dateA = '2021-12-01'
    end_dateA = datetime.strptime(end_dateA, '%Y-%m-%d').strftime('%Y-%m-%d')
    end_date = end_dateA.split('-')
    end_date_mth, end_date_year = end_date[1], end_date[0]

    for email in emails: 
        
        ### email subjects
        emailSubject = email.Subject
        emailSubject = str(emailSubject)
              
        ### sender name
        emailSender = email.Sender
        emailSender = str(emailSender)
        
        ### sender email address
        emailSenderAddress = email.Sender.Address
        emailSenderAddress = str(emailSenderAddress)

        ### email body
        emailBody = email.Body
        emailBody = emailBody.encode('ascii', 'ignore')
        emailBody = str(emailBody)
        
        ### email received date
        emailReceivedDate = email.SentOn
        emailReceivedDateStr = str(email.SentOn)
        
        ### filter the JSON
        formatJson = emailBody.split()
        formatJson = ''.join(formatJson)
        start = formatJson.find('--StartofJSON--') + 15
        end = formatJson.find('--EndofJSON--')
        myJson = formatJson[start:end]
        myQuestion = myJson.split('{"question":')
     
        #pprint(myJson)
        
        count += 1
        myRequestMonth = ''
        
        ### get the questions and answers
        for i in myQuestion:
            myAnswerPosition = i.find('"answer"')
            myQuestion = i[1:myAnswerPosition-2]            
            
            if r'r\n\r' in myQuestion:
                myQuestion = myQuestion.replace(r'r\n\r','')
            
            #print(myQuestion)
            
            myAns = i[myAnswerPosition:]
            myAnswerPosition = myAns.find('},')
            myAns = myAns[:myAnswerPosition]
            myAnswerPosition = myAns.find('"answer":"') + 10
            myAns = myAns[myAnswerPosition:]
            myAns = myAns[:len(myAns)-1]
            myAns = str(myAns)
            
            myAns = myAns.replace(r'\r','')
            myAns = myAns.replace(r'\n','')
            myAns = myAns.replace('}','')
            myAns = myAns.replace(']','')
            myAns = myAns.replace('"','')
            
            if r'\r\n\r' in myAns:
                myAns = myAns[:len(myAns)-9]
            
            #print(myAns)
            
            if 'RequestMonth' in myQuestion:
                myRequestMonth = myAns
                   
            case2 = {
                "question":myQuestion,
                "answer":myAns
            }
                  
            ### save all question & answer in the list called email_body_list
            email_body_list.append(case2)
        
        myRequestMonthList = myRequestMonth.split(',')
        request_year_name = myRequestMonthList[1]  
        request_month_name = myRequestMonthList[0]
        if len(request_month_name) > 3:
            request_month_name = request_month_name[:3]
        month_number = strptime(request_month_name,'%b').tm_mon
        month_number = str(month_number)
        
        ### check if request month is within start date and end date         
        ### assumption: start date & end date are in the same month same year
        ### thus, we cannot accept start date this year, end date next year
        if int(start_date_year) <= int(request_year_name) <= int(end_date_year):
            if int(start_date_mth) <= int(month_number) <= int(end_date_mth):
                
                case = [emailReceivedDate, emailSenderAddress, request_year_name, month_number]
                check_latest.append(case)
                
                case2 = {
                    "Subject": emailSubject,
                    "Body":email_body_list,
                    "SenderEmail": emailSenderAddress,
                    "SenderName":emailSender,
                    "Date":myRequestMonth,
                    "ReceivedDate":emailReceivedDate
                }
                
                ### to prevent appending from old emails
                email_body_list = []
                
                email_list.append(case2)
                               
                new_email_body = email_list[count-1]['Body']
                
                myQnA = []
                leaveRequest = []
                callRequest = []
                otherRequest = []
                
                for thread in new_email_body:
                
                    if "LeaveRequest" in thread['question']:
                        leaveRequest.append(thread['answer'])
                    elif "CallRequests" in thread['question']:
                        callRequest.append(thread['answer'])
                
                for thread in new_email_body:
                    if "LeaveRequest" in thread['question']:
                        pass
                    elif "CallRequests" in thread['question']:
                        pass
                    else:
                        myQnA.append(thread)
                
                myQnA.append({"question":"leaveRequest", "answer":leaveRequest})
                myQnA.append({"question":"callRequest", "answer":callRequest})
                
                needed_emails.append([
                    #"Email":
                    myQnA, 
                    #"Subject":
                    email_list[count-1]['Subject'], 
                    #"SenderEmail":
                    email_list[count-1]['SenderEmail'], 
                    #"SenderName":
                    email_list[count-1]['SenderName'], 
                    #"RequestMonth":
                    email_list[count-1]['Date'],
                    #"ReceivedDate":
                    emailReceivedDate
                ])
            
    #pprint(needed_emails)
    #pprint(check_latest)

    delete_index = []  

    for i in range(len(needed_emails)):
        receivedDate = str(needed_emails[i][5])
        receivedDate = receivedDate.split(' ')
        receivedDate_date = receivedDate[0]
        receivedDate_date = dateutil.parser.parse(receivedDate_date)
        receivedDate_time = receivedDate[1]
        receivedDate_time = receivedDate_time[:-6]
        receivedDate_time = receivedDate_time.split(':')

        senderEmail = needed_emails[i][2]
        
        for j in range(len(check_latest)):
            
            check_receivedDate = str(check_latest[j][0])
            check_receivedDate = check_receivedDate.split(' ')
            check_receivedDate_date = check_receivedDate[0]
            check_receivedDate_date = dateutil.parser.parse(check_receivedDate_date)
            check_receivedDate_time = check_receivedDate[1]
            check_receivedDate_time = check_receivedDate_time[:-6]
            check_receivedDate_time = check_receivedDate_time.split(':')

            check_senderEmail = check_latest[j][1]
            
            if senderEmail == check_senderEmail:
                
                receivedDate_time_hr = int(receivedDate_time[0])
                receivedDate_time_min = int(receivedDate_time[1])
                receivedDate_time_sec = int(receivedDate_time[2])
                
                check_receivedDate_time_hr = int(check_receivedDate_time[0])
                check_receivedDate_time_min = int(check_receivedDate_time[1])
                check_receivedDate_time_sec = int(check_receivedDate_time[2])
                       
                if receivedDate_date == check_receivedDate_date:              
                    if receivedDate_time_hr == check_receivedDate_time_hr:
                        if receivedDate_time_min == check_receivedDate_time_min:
                            if receivedDate_time_sec > check_receivedDate_time_sec:
                                delete_index.append([i])
                            
                        elif receivedDate_time_min > check_receivedDate_time_min:
                            delete_index.append([i])
                        
                    elif receivedDate_time_hr > check_receivedDate_time_hr:
                        delete_index.append([i])
                    
                elif receivedDate_date > check_receivedDate_date:
                    delete_index.append([i])

    sorted_delete_index = []
    for i in delete_index:
        if i not in sorted_delete_index:
            sorted_delete_index.append(i)

    final_emails = []

    for i in reversed(sorted_delete_index):
        needed_emails.pop(i[0])
        
    #pprint(needed_emails)
    
    ### Establish connection to DB
    conn, cur = create_connection() 
    
    ### delete existing table, create new table
    #cur.execute('''DROP TABLE IF EXISTS CallRequest;''')
    #cur.execute('''DROP TABLE IF EXISTS LeaveApplication;''')
    
    #cur.execute("""CREATE TABLE IF NOT EXISTS CallRequest;""")
    #conn.commit()
    #cur.execute("""CREATE TABLE IF NOT EXISTS LeaveApplication;""")
    #conn.commit()
        
    for i in range(len(needed_emails)):
        #pprint(needed_emails[i])
        
        ### from JSON
        # -------------
        # CallRequests(Date,RequestType,Remarkse.g.ReasonforCallBlock)
        # LeaveRequest(LeaveStartDate,LeaveEndDate,AM/PM,TypeofLeave,RemarksE.g.NameofCourse/Conference,ReasonforAL)
        
        ### from SQITE3
        # -------------
        # CallRequest(email, name, date, request_type, remark)
        # LeaveRequest(email, name, start_date, end_date, duration, leave_type, remark)
        
        myStartDate = start_dateA
        myEndDate = end_dateA
        
        myEmail = needed_emails[i][2]
        myName = needed_emails[i][3]
        
        for j in needed_emails[i][0]:
            if j['question'] == 'leaveRequest':
                #print(j['answer'])
                for k in j['answer']:
                    mySplit = k.split(',')
                                       
                    #if mySplit[0] == '':    # leave start date
                    #    mySplit[0] = 'null'
                    #if mySplit[1] == '':    # leave end date
                    #    mySplit[1] = 'null'
                    #if mySplit[2] == '':    # duration
                    #    mySplit[2] = 'null'
                    #if mySplit[3] == '':    # leave type
                    #    mySplit[3] = 'null'
                    #if mySplit[4] == '':    # remarks
                    #    mySplit[4] = 'null'
                    
                    if mySplit[0] != '' and mySplit[1] != '' and mySplit[2] != '' and mySplit[3] != '':
                        
                        #if mySplit[4] == '':    # remarks
                        #    mySplit[4] = NULL
                    
                        #print(mySplit[0],mySplit[1],mySplit[2],mySplit[3],mySplit[4])
                        print('-- prepare DB for leave request --')
                        
                        cur.execute("""INSERT OR IGNORE INTO LeaveApplication(email, name, start_date, end_date, duration, leave_type, remark) 
                           VALUES
                           (?, ?, ?, ?, ?, ?, ?)
                           ;""",(myEmail,myName,mySplit[0],mySplit[1],mySplit[2],mySplit[3],mySplit[4]))
                           
                           
                        # VALUES('Q', 'Q', '2020-03-17', '2020-03-17', 'wcgao', 'MC/Hospitalisation Leave', 'wcgao')
                        conn.commit()
                    
            if j['question'] == 'callRequest':
                #print(j['answer'])
                for m in j['answer']:
                    mySplit = m.split(',')
                    
                    #if mySplit[0] == '':    # date
                    #    mySplit[0] = 'null'
                    #if mySplit[1] == '':    # request type
                    #    mySplit[1] = 'null'
                    #if mySplit[2] == '':    # remark
                    #    mySplit[2] = 'null'
                        
                    if mySplit[0] != '' and mySplit[1] != '':
                        #print(mySplit[0],mySplit[1],mySplit[2])
                        
                        #if mySplit[2] == '':    # remarks
                        #    mySplit[2] = NULL
                        
                        print('-- prepare DB for call request --')
                    
                        cur.execute("""INSERT OR IGNORE INTO CallRequest(email, name, date, request_type, remark) 
                            VALUES
                            (?, ?, ?, ?, ?)
                            ;""",(myEmail,myName,mySplit[0],mySplit[1],mySplit[2]))
                           
                        conn.commit()
                        
                        # ('W', 'W', '2020-07-21', 'try02 & no weekend duty', 'wcgao'),
    
    # Close connection to DB
    close_connection(conn, cur)
        
    print('--- end ---')
    
    return needed_emails


email_json()