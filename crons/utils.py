import sys
import time
from datetime import datetime


def stdout_w(s, v=True):
    """
    print a string on stdout, without newline.
    if v is set to False, do nothing.
    """
    if v:
        sys.stdout.write(s)
        sys.stdout.flush()


def telecom_timestamp_format(timestamp):
    """
    Format unix timestamp (floating point value) to telecom-friendly string.
    If the value provided is already a string, do nothing (assuming it is a
    correctly formatted one).
    """
    # %Y-%m-%d %H:%M:%S'
    try:
        _ts = float(timestamp)
        return datetime.fromtimestamp(_ts).strftime('%d/%m/%Y %H:%M')
    except ValueError:
        # assume that timestamp is already correctly formatted
        return timestamp


def postgres_timestamp_format(timestamp):
    """
    convert <dd/mm/yyyy hh:mm> or unix timestamp to <yyyy-mm-dd hh:mm:ss>
    """
    # make sure 'timestamp' is not a float timestamp
    timestamp = telecom_timestamp_format(timestamp)
    # convert to time_struct...
    t_struct = time.strptime(timestamp, '%d/%m/%Y %H:%M')
    # ...and format it
    return time.strftime('%Y-%m-%d %H:%M:%S', t_struct)

