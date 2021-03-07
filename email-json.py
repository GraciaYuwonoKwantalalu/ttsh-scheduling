from datetime import datetime
import datetime
from win32com.client import Dispatch
from pprint import pprint
import json

outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
root_folder = outlook.Folders.Item(1)   

### customised folder name is named 'test'
test_folder = root_folder.Folders['test']
emails = test_folder.Items

email_list = []
email_body_list = []
count = 0

start_date = datetime.datetime(2021, 1, 1)
start_date = start_date.strftime("%Y-%m-%d")

end_date = datetime.datetime(2021, 12, 31)
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
    emailBody = str(emailBody)

    ### Get email date 
    date = str(email.SentOn) 
    date = date[:10]
    
    if start_date <= date <= end_date:  

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
            #print(myQuestion)
            myAns = i[myAnswerPosition:]
            myAnswerPosition = myAns.find('},')
            myAns = myAns[:myAnswerPosition]
            myAnswerPosition = myAns.find('"answer":"') + 10
            myAns = myAns[myAnswerPosition:]
            myAns = myAns[:len(myAns)-1]
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
            "Date":date
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
        myQnA.append({"question":"callRequest","answer":callRequest})

        
        needed_emails.append({"ID": count, "Email":myQnA, "Subject":email_list[count-1]['Subject'], "SenderEmail":email_list[count-1]['SenderEmail'], "SenderName":email_list[count-1]['SenderName'], "Date":email_list[count-1]['Date']})       
    
    else:
        pass

pprint(needed_emails)

### to get request month
#for i in needed_emails:
#    email_info = i['Email']
#    for j in email_info:
#        if "RequestMonth" in j['question']:
#            print(j)
    