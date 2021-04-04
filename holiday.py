import holidays
import datetime
from pprint import pprint

### weekdays as a tuple
weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

sg_Holiday = []
count = 0

### Singapore Holidays - 2021
for holiday in sorted(holidays.Singapore(years=2021).items()):
    ### get the day of that week
    holiday_date = holiday[0]
    holiday_day = holiday_date.weekday()
    holiday_weekday = weekDays[holiday_day]
    
    count += 1
    
    case = {
        "ID": count,
        "HolidayName":holiday[1],
        "HolidayDate":format(holiday[0]),
        "HolidayDay":format(holiday_weekday)
    }

    sg_Holiday.append(case)

pprint(sg_Holiday)