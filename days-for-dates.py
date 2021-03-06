from datetime import date, timedelta
import datetime
from pprint import pprint

# format: (yyyy, m, d) or (yyyy,m,dd) or (yyyy,mm,dd)
start_date  = datetime.datetime(2021, 3, 1)

end_date  = datetime.datetime(2021, 3, 6)

# as timedelta
delta = end_date - start_date

datesList = []

### weekdays as a tuple
weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

for i in range(delta.days + 1):
    day = start_date + timedelta(days=i)
    dateOnly = day.strftime("%Y-%m-%d")
    #print(dateOnly)
    day = day.weekday()
    day_weekday = weekDays[day]
    #print(day_weekday)
    
    case = {
            "DATE": dateOnly,
            "Day": day_weekday,
        }
    
    datesList.append(case)
    
pprint(datesList)
