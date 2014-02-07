#!/usr/bin/env python

import argparse
import time
import os
import sys
import subprocess
import psycopg2

from datetime import datetime

from telecomsync import fetch_telecom_data, insert_data
from generatemaps import generate_map
from utils import postgres_timestamp_format, get_avg_co2_value
from local_settings import DB_SETTINGS
from generate_adj_list import generate_adj_list


def v_print(s, v=True):
    """
    'Cuz logging is for suckers!
    """
    if v:
        print s


def call_command(command, environment=None, shell=False):
    """
    Call an os command,
    return a tuple with (stdout, stderr, unix_process_exit_code)
    """
    env = os.environ.copy()
    if environment:
        env.update(environment)

    if type(command) is str:
        command = command.split(' ')

    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env, shell=shell)
    streamdata = process.communicate()

    if len(streamdata[1].strip()) > 0:
        print("WARNING: STDERR: {errs}".format(errs=streamdata[1]))

    return streamdata[0], streamdata[1], process.returncode


def gen_map(t_start, t_end, map_name, dow=-1, default_val=None, testing=False):
    """
    Helper function to call 'generatemap' passing timestamp instead of
    formatted string
    If testing is True, do nothing.
    """
    if testing:
        return
    return generate_map(
        postgres_timestamp_format(t_start),
        postgres_timestamp_format(t_end),
        map_name,
        day=dow,
        default_val=default_val
    )


def move_to_db(map_name, table_name=None):
    table_name = table_name or map_name

    cmd = ['-c',
           '/usr/local/share/pgsql93stable/bin/raster2pgsql -s 32632 -I -t 5x5 '
           '-d /hardmnt/geopg0/db93stable/appiedi/grass_output/{0}.tiff {1} |  psql -U appiedi -h geopg -p 50003 '
           '-d appiedi'.format(map_name, table_name)
           ]

    env = dict(PGPASSWORD=DB_SETTINGS['password'])
    out, err, ret = call_command(cmd, environment=env, shell=True)
    if ret != 0:
        print('ERROR: retval <> 0, something went wrong')


def raster_values_to_graph():
    with psycopg2.connect(**DB_SETTINGS) as conn:
        with conn.cursor() as cur:
            cur.callproc('raster_values_to_graph')


def main():
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    testing = '-t' in sys.argv or '--testing' in sys.argv
    os.environ['PGPASSWORD'] = DB_SETTINGS['password']
    t = time.time()
    dt = datetime.fromtimestamp(t)

    data = fetch_telecom_data(t - 26 * 60 * 60, t)  # last 26 hours
    v_print('Telecom Italia\'s data fetched.', verbose)

    insert_data(data)
    v_print('Data inserted into DB.', verbose)

    # generate maps

    # all inclusive map
    v_print('Generating general map...', verbose)
    avg_val = get_avg_co2_value()
    gen_map(0.0, t, 'general', default_val=avg_val, testing=testing)
    v_print('Moving to db general...', verbose)
    move_to_db('general', 'co_general')
    v_print('Moving to db general_avg', verbose)
    move_to_db('general_avg', 'co_general_avg')
    raster_values_to_graph()
    v_print('Done.', verbose)

    # last 7 days
    # week_start = time.mktime(
    #     datetime.fromtimestamp(t - (dt.weekday()*24*60*60)).date().timetuple()
    # )
    v_print('Generating weekly map...', verbose)
    #gen_map(week_start, t, 'week')
    gen_map(t - (7 * 24 * 60 * 60), t, 'week', testing=testing)
    v_print('Moving to db...', verbose)
    move_to_db('week', 'co_weekly')
    v_print('Done.', verbose)

    # day of the week
    dow = (dt.weekday() + 1) % 7
    v_print('Generating DOW map for dow n. {0}'.format(dow), verbose)
    gen_map(0.0, t, 'dow_{0}'.format(dow), dow, testing=testing)
    v_print('Moving to db...', verbose)
    move_to_db('dow_{0}'.format(dow), 'co_dow{0}'.format(dow))
    v_print('Done.', verbose)

    v_print('Generating adj list...', verbose)
    generate_adj_list()
    v_print('Done.', verbose)


if __name__ == '__main__':
    main()

