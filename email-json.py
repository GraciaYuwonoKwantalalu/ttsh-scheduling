from datetime import datetime
from win32com.client import Dispatch
from pprint import pprint
import json

outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
root_folder = outlook.Folders.Item(1)

#for folder in root_folder.Folders:
#   print (folder.Name)    

### customised folder name is 'test'
test_folder = root_folder.Folders['test']
messages=test_folder.Items

email_list = []
email_body_list = []
count = 0

for message in messages:

    count += 1

    ### Get email date 
    date = str(message.SentOn)  
    date = date[:8]    
    year_of_date = date[6:]
    month_of_date = date[3:5]
    
    if year_of_date == '21':
        if month_of_date == "05":

    
            ### email subjects
            emailSubject = message.Subject
            
            
            ### email body
            emailBody = message.Body
            emailBody = emailBody.encode("utf-8")

            
            
            ### sender name
            emailSender = message.Sender
            
            
            ### sender email address
            emailSenderAddress = message.Sender.Address
            

            formatJson = emailBody.split()
            formatJson = ''.join(formatJson)
            start = formatJson.find('--StartofJSON--') + 15
            end = formatJson.find('--EndofJSON--')
            myJson = formatJson[start:end]
            #print(myJson)   
            #print(type(myJson)) # str
            myQuestion = myJson.split('{"question":')
            #pprint(myQuestion) # list
            
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

pprint(email_list)