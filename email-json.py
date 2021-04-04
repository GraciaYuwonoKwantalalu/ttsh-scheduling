from datetime import date, timedelta, datetime
import dateutil.parser
from win32com.client import Dispatch
from pprint import pprint
import json
from time import strptime
import pandas as pd
import sqlite3
from helperFunctions import create_connection, close_connection

def email_json(start_dateA,end_dateA):
    outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
    root_folder = outlook.Folders.Item(1)   

    ### note: change the folder name 'test' to the one in TTSH
    test_folder = root_folder.Folders['test']
    emails = test_folder.Items

    email_list = []
    email_body_list = []
    needed_emails = []
    check_latest = []

    start_dateA = datetime.strptime(start_dateA, '%Y-%m-%d').strftime('%Y-%m-%d')
    start_date = start_dateA.split('-')
    start_date_mth, start_date_year = start_date[1], start_date[0]

    end_dateA = datetime.strptime(end_dateA, '%Y-%m-%d').strftime('%Y-%m-%d')
    end_date = end_dateA.split('-')
    end_date_mth, end_date_year = end_date[1], end_date[0]
    
    months_between = pd.date_range(start_dateA,end_dateA, freq='MS').strftime("%b,%Y").tolist()

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
        
        formatJson = emailBody.split()
        formatJson = ''.join(formatJson)
        start = formatJson.find('--StartofJSON--') + 15
        end = formatJson.find('--EndofJSON--')
        myJson = formatJson[start:end]
        myQuestion = myJson.split('{"question":')
     
        myRequestMonth = ''
        
        ### get the questions and answers
        for i in myQuestion:
            myAnswerPosition = i.find('"answer"')
            myQuestion = i[1:myAnswerPosition-2]            
            
            if r'r\n\r' in myQuestion:
                myQuestion = myQuestion.replace(r'r\n\r','')
            
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
            
            if 'RequestMonth' in myQuestion:
                myRequestMonth = myAns
                   
            case2 = {
                "question":myQuestion,
                "answer":myAns
            }

            email_body_list.append(case2)
        
        
        myRequestMonthList = myRequestMonth.split(',')
        request_year_name = myRequestMonthList[1]  
        request_month_name = myRequestMonthList[0]
        if len(request_month_name) > 3:
            request_month_name = request_month_name[:3]
            myRequestMonth = request_month_name + ',' + request_year_name
        month_number = strptime(request_month_name,'%b').tm_mon
        month_number = str(month_number)
        
        if myRequestMonth in months_between:
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
            
            ### note: don't delete this empty list  --> it is needed to prevent appending from old emails
            email_body_list = []
            
            email_list.append(case2)
            
            new_email_body = email_list[(len(email_list))-1]['Body']
            
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
                myQnA,
                email_list[len(email_list)-1]['Subject'], 
                email_list[len(email_list)-1]['SenderEmail'], 
                email_list[len(email_list)-1]['SenderName'], 
                email_list[len(email_list)-1]['Date'],
                emailReceivedDate
            ]) 
            
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
                            if receivedDate_time_sec < check_receivedDate_time_sec:
                                delete_index.append([i])
                            
                        elif receivedDate_time_min < check_receivedDate_time_min:
                            delete_index.append([i])
                        
                    elif receivedDate_time_hr < check_receivedDate_time_hr:
                        delete_index.append([i])
                    
                elif receivedDate_date < check_receivedDate_date:
                    delete_index.append([i])

    sorted_delete_index = []
    for i in delete_index:
        if i not in sorted_delete_index:
            sorted_delete_index.append(i)
    
    for i in reversed(sorted_delete_index):
        needed_emails.pop(i[0])
      
    conn, cur = create_connection() 
    
    for i in range(len(needed_emails)):
        
        myEmail = needed_emails[i][2]
        myName = needed_emails[i][3]
        
        myStartDate = start_dateA
        myEndDate = end_dateA
        
        for j in needed_emails[i][0]:
            if j['question'] == 'leaveRequest':
                for k in j['answer']:
                    mySplit = k.split(',')
                    
                    leaveStartDate = mySplit[0]
                    leaveEndDate = mySplit[1]
                    
                    if leaveStartDate != '':
                        leaveStartDate_List = leaveStartDate.split('/')
                        L_sDate_day = leaveStartDate_List[0]
                        L_sDate_mth = leaveStartDate_List[1]
                        
                        if len(leaveStartDate_List[0]) == 1:
                            L_sDate_day = '0' + L_sDate_day
                        if len(leaveStartDate_List[1]) == 1:
                            L_sDate_mth = '0' + L_sDate_mth
                            
                        L_sDate = request_year_name + '-' + L_sDate_mth + '-' + L_sDate_day
                    
                    if leaveEndDate != '':
                        leaveEndDate_List = leaveEndDate.split('/')                   
                        L_eDate_day = leaveEndDate_List[0]
                        L_eDate_mth = leaveEndDate_List[1]
                        
                        if len(leaveEndDate_List[0]) == 1:
                            L_eDate_day = '0' + L_eDate_day
                        if len(leaveEndDate_List[1]) == 1:
                            L_eDate_mth = '0' + L_eDate_mth
                        
                        L_eDate = request_year_name + '-' + L_eDate_mth + '-' + L_eDate_day
                    
                    if mySplit[0] != '' and mySplit[1] != '' and mySplit[2] != '' and mySplit[3] != '':
                                               
                        cur.execute("""INSERT OR IGNORE INTO LeaveApplication(email, name, start_date, end_date, duration, leave_type, remark) 
                           VALUES
                           (?, ?, ?, ?, ?, ?, ?)
                           ;""",(myEmail,myName,L_sDate,L_eDate,mySplit[2],mySplit[3],mySplit[4]))
                                                  
                        conn.commit()

            if j['question'] == 'callRequest':
                C_Date = ''
                for m in j['answer']:
                    mySplit = m.split(',')
                    if mySplit[0] != '':
                        C_Date = mySplit[0]
                        C_Date = C_Date.split('/')
                        if len(C_Date[0]) == 1:
                            C_Date[0] = '0' + C_Date[0]
                        if len(C_Date[1]) == 1:
                            C_Date[1] = '0' + C_Date[1]
                        C_Date = request_year_name + '-' + C_Date[0] + '-' + C_Date[1]
                    
                    if mySplit[0] != '' and mySplit[1] != '':    
                        cur.execute("""INSERT OR IGNORE INTO CallRequest(email, name, date, request_type, remark) 
                            VALUES
                            (?, ?, ?, ?, ?)
                            ;""",(myEmail,myName,C_Date,mySplit[1],mySplit[2]))
                           
                        conn.commit()
                        
    close_connection(conn, cur) 
    return needed_emails

email_json()