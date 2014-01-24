import os
import requests
import psycopg2
import time
import json
import sys
import argparse
from datetime import datetime

from local_settings import DB_SETTINGS


def stdout_w(s, v=True):
    """
    print a string on stdout, without newline.
    if v is set to False, do nothing.
    """
    if v:
        sys.stdout.write(s)
        sys.stdout.flush()


def fetch_telecom_data(t_start=None, t_end=None):
    """
    fetch telecom data (as json).
    If no timestamps are provided, default to last 26h.
    """
    # set default value here in order to be able to handle 'None' value
    t_start = t_start or time.time()-(60*60*26)
    t_end = t_end or time.time()

    url = 'http://collector-svil.mobileterritoriallab.eu/sensordrone/api/'
    payload = {
        'timestamp_start': timestamp_format(t_start),
        'timestamp_end': timestamp_format(t_end)
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.ok:
        return r.json()
    raise requests.ConnectionError('Request failed.')


def timestamp_format(timestamp):
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


def telecom_to_postgres_timestamp(timestamp):
    """
    convert <dd/mm/yyyy hh:mm> into <yyyy-mm-dd hh:mm:ss>
    """
    # make sure 'timestamp' is not a float timestamp
    timestamp = timestamp_format(timestamp)
    # convert to time_struct...
    _t = time.strptime(timestamp, '%d/%m/%Y %H:%M')
    # ...and format it
    return time.strftime('%Y-%m-%d %H:%M:%S', _t)


def build_query(cur, obj):
    return cur.mogrify(
        (
            'INSERT INTO telecom_dataset (mtl_timestamp, '
            'longitude, provider, latitude, speed, co, accuracy'
            ') VALUES (%s, %s, %s, %s, %s, %s, %s);'
        ),
        (
            telecom_to_postgres_timestamp(obj['timestamp']),
            obj['longitude'], obj['provider'],
            obj['latitude'], obj['speed'],
            obj['co_value'], obj['accuracy']
        )
    )


def insert_data(json_data=None, verbose=False):
    if json_data is None:
        json_data = fetch_telecom_data()
    if type(json_data) == str:
        json_data = json.dumps(json_data)

    with psycopg2.connect(**DB_SETTINGS) as conn:
        with conn.cursor() as cur:
            cur.execute('SAVEPOINT sp;')
            for obj in json_data:
                try:
                    cur.execute(build_query(cur, obj))
                    # conn.commit()
                    cur.execute('SAVEPOINT sp;')
                    stdout_w('.', verbose)
                except psycopg2.IntegrityError, psycopg2.Error:
                    # conn.rollback()
                    cur.execute('ROLLBACK TO SAVEPOINT sp;')
                    stdout_w('s', verbose)
                except(KeyboardInterrupt, SystemExit):
                    conn.commit()
                    raise
            conn.commit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update appiedi db with data from Telecom Italia'
    )
    parser.add_argument('timestamp_start', default=None, nargs='?')
    parser.add_argument('timestamp_end', default=None, nargs='?')
    parser.add_argument('-c', '--cron', help='cron mode', dest='cron',
                        action='store_true')
    parser.add_argument('-q', '--quiet', help='quiet output',
                        dest='quiet', action='store_true')
    args = parser.parse_args()

    timestamp_start = args.timestamp_start
    if timestamp_start is None and args.cron:
        timestamp_start = os.environ.get('LAST_FETCH_TIMESTAMP')

    _t = time.time()
    data = fetch_telecom_data(args.timestamp_start, args.timestamp_end)

    if not args.quiet:
        print 'Got the data'
    insert_data(data, not args.quiet)

    if args.cron:
        os.environ['LAST_FETCH_TIMESTAMP'] = _t
