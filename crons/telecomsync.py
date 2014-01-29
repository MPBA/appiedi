#!/usr/bin/env python

import os
import requests
import psycopg2
import time
import json
import argparse

from utils import stdout_w, postgres_timestamp_format, telecom_timestamp_format

from local_settings import DB_SETTINGS


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
        'timestamp_start': telecom_timestamp_format(t_start),
        'timestamp_end': telecom_timestamp_format(t_end)
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.ok:
        return r.json()
    raise requests.ConnectionError('Request failed.')


def build_query(cur, obj):
    return cur.mogrify(
        (
            'INSERT INTO telecom_dataset (mtl_timestamp, '
            'longitude, provider, latitude, speed, co, accuracy'
            ') VALUES (%s, %s, %s, %s, %s, %s, %s);'
        ),
        (
            postgres_timestamp_format(obj['timestamp']),
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
    parser.add_argument('-v', '--verbose', help='verbose output',
                        dest='verbose', action='store_true')
    args = parser.parse_args()

    timestamp_start = args.timestamp_start
    if timestamp_start is None and args.cron:
        timestamp_start = os.environ.get('LAST_FETCH_TIMESTAMP')

    _t = time.time()
    data = fetch_telecom_data(args.timestamp_start, args.timestamp_end)

    if args.verbose:
        print 'Got the data'

    insert_data(data, args.verbose)

    if args.verbose:
        print()

    if args.cron:
        os.environ['LAST_FETCH_TIMESTAMP'] = _t

