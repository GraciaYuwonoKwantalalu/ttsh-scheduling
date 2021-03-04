import datetime
from win32com.client import Dispatch
from pprint import pprint

outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
root_folder = outlook.Folders.Item(1)

#for folder in root_folder.Folders:
#   print (folder.Name)    

### customised folder name is 'test'
test_folder = root_folder.Folders['test']
messages=test_folder.Items

email_dict = []
count = 0

for message in messages:
    ### email subjects
    emailSubject = message.Subject
    
    ### email body
    emailBody = message.Body
    
    ### sender name
    emailSender = message.Sender
    
    ### sender email address
    emailSenderAddress = message.Sender.Address
    
    ### Get email date 
    date = message.SentOn.strftime("%d-%m-%y")
    
    count += 1
    
    case = {
        "ID": count,
        "Subject": emailSubject,
        "Body":emailBody,
        "SenderEmail": emailSenderAddress,
        "SenderName":emailSender,
        "Date":date
    }
    
    email_dict.append(case)

#pprint(email_dict)

### format the string
sampleJson = email_dict[3]['Body']
formatJson = sampleJson.split()
formatJson = ''.join(formatJson)

### pull JSON
start = formatJson.find('--StartofJSON--')
end = formatJson.find('--EndofJSON--')
pprint(formatJson[start+15:end])

### filter by dates
#pprint(email_dict)
for email in email_dict:
    theDate = ''
    for i in email['Date']:
        theDate += i
    #print(theDate)
    
    # check for year 2021
    if theDate[6:] == '21':
        # check for month
        if theDate[3:5] =='01':
            print('jan')