from datetime import datetime
import datetime
from win32com.client import Dispatch
from pprint import pprint
import json
from time import strptime

outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
root_folder = outlook.Folders.Item(1)   

### customised folder name is named 'test'
test_folder = root_folder.Folders['test']
emails = test_folder.Items

email_list = []
email_body_list = []
count = 0

start_date = datetime.datetime(2021, 2, 1)
start_date = start_date.strftime("%Y-%m-%d")

end_date = datetime.datetime(2021, 4, 20)
end_date = end_date.strftime("%Y-%m-%d")

needed_emails = []

for email in emails:

    count += 1
    
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

    ### Get email date
    date2_year = str(email.SentOn.year)
    date2_mth = str(email.SentOn.month)
    
    if len(date2_mth) < 2:
        date2_mth = '0' + date2_mth
    
    date2_day = str(email.SentOn.day)
    
    if len(date2_day) < 2:
        date2_day = '0' + date2_day
    
    date2 = date2_year + '-' + date2_mth + '-' + date2_day
    
    if start_date <= date2 <= end_date:

        formatJson = emailBody.split()
        formatJson = ''.join(formatJson)
        start = formatJson.find('--StartofJSON--') + 15
        end = formatJson.find('--EndofJSON--')
        myJson = formatJson[start:end]
        myQuestion = myJson.split('{"question":')
        
        count2 = 0        
        
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
            
            count2 +=1
            
            case2 = {
                "ID": count2,
                "question":myQuestion,
                "answer":myAns
            }
            
            email_body_list.append(case2)
        
        case = {
            "ID": count,
            "Subject": emailSubject,
            "Body":email_body_list,
            "SenderEmail": emailSenderAddress,
            "SenderName":emailSender,
            "Date":date2
        }
        
        ### to prevent appending from old emails
        email_body_list = []
        
        email_list.append(case)

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

        
        needed_emails.append({
            "ID": count, 
            "Email":myQnA, 
            "Subject":email_list[count-1]['Subject'], 
            "SenderEmail":email_list[count-1]['SenderEmail'], 
            "SenderName":email_list[count-1]['SenderName'], 
            "Date":email_list[count-1]['Date']
        })
    
    else:
        pass

#pprint(needed_emails)


final_output = []

for i in needed_emails:
    myEmails = i['Email']
    myDate = i['Date'].split('-')
    #print(myDate[0], myDate[1])
    
    #requestedMonth = []
    
    for j in myEmails:
        question = j['question']
        if 'RequestMonth' in question:
            text = j['answer']
            text = text.split(',')
            
            #month = monthToNum(text[0].lower())
            month = strptime(text[0],'%b').tm_mon
            year = text[1]
            
            requestedMonth = [month, year]
    
    #print(requestedMonth[1], requestedMonth[0])
    
    if str(requestedMonth[1]) < str(myDate[0]):
        final_output.append(i)
    elif str(requestedMonth[1]) == str(myDate[0]):
        if str(requestedMonth[0]) < str(myDate[1]):
            final_output.append(i)

pprint(final_output)
            