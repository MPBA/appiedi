from datetime import datetime, timedelta
import time

from telecomsync import fetch_telecom_data, insert_data
from utils import telecom_timestamp_format, postgres_timestamp_format


def utc_mktime(utc_tuple):
    """Returns number of seconds elapsed since epoch
    Note that no timezone are taken into consideration.
    utc tuple must be: (year, month, day, hour, minute, second)
    """

    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))

def datetime_to_timestamp(dt):
    """Converts a datetime object to UTC timestamp"""
    return int(utc_mktime(dt.timetuple()))

def insert(date1, date2):
    print '{0} -> {1}'.format(date1, date2)
    json_data = fetch_telecom_data(datetime_to_timestamp(date1), datetime_to_timestamp(date2))
    insert_data(json_data)
    if not date2 > datetime.now():
        insert(date2 - timedelta(hours=2), date2 + timedelta(days=1))


def main(date1=None):
    date1 = date1 or datetime(2013, 11, 20)
    insert(date1, date1 + timedelta(days=1))
    
if __name__ == '__main__':
    main()
