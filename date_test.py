from datetime import datetime, timedelta
from dateutil import parser

def convert_to_epoch(date_str):
    # Parse the date string using dateutil
    date_obj = parser.parse(date_str)

    # Convert to Unix epoch time
    epoch_time = int(date_obj.timestamp())
    return epoch_time

# Examples
print(convert_to_epoch("10-10-1"))      # Assuming it's meant for 2001
print(convert_to_epoch("10/10/1"))      # Assuming it's meant for 2001
print(convert_to_epoch((datetime.now()).strftime("%Y-%m-%d")))  # Today's date
print(convert_to_epoch((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")))  # Yesterday's date

# Example with "month" (first day of current month)
first_of_month = datetime(datetime.now().year, datetime.now().month, 1)
print(int(first_of_month.timestamp()))
