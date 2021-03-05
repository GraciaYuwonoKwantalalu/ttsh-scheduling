from datetime import datetime
import datetime
from win32com.client import Dispatch
from pprint import pprint
import json


outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
root_folder = outlook.Folders.Item(1)   


### customised folder name is named 'test'
test_folder = root_folder.Folders['test']
messages=test_folder.Items


email_list = []
email_body_list = []
count = 0


start_date = datetime.datetime(2021, 1, 1)
start_date = start_date.strftime("%Y-%m-%d")

end_date = datetime.datetime(2021, 12, 31)
end_date = end_date.strftime("%Y-%m-%d")


for message in messages:

    count += 1

    ### Get email date 
    date = str(message.SentOn) 
    date = date[:10]
    
    if start_date <= date <= end_date:
        print("PASS !")
    
    
        ### email subjects
        emailSubject = message.Subject
        emailSubject = str(emailSubject)   

         
         
        ### sender name
        emailSender = message.Sender
        emailSender = str(emailSender)
        
        
        
        ### sender email address
        emailSenderAddress = message.Sender.Address
        emailSenderAddress = str(emailSenderAddress)



        ### email body
        emailBody = message.Body
        emailBody = str(emailBody)
        
        

        ### format email body, pull the needed stuff
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
        
        
        
        # each case represents an email
        case = {
            "ID": count,
            "Subject": emailSubject,
            "Body":email_body_list,
            "SenderEmail": emailSenderAddress,
            "SenderName":emailSender,
            "Date":date
        }
        
        email_list.append(case)
    
    
    else:
        print("Date out of range, i.e. no emails found within that range")

pprint(email_list)