import argparse
import time
import os
import sys
import subprocess
import psycopg2

from datetime import datetime

from telecomsync import fetch_telecom_data, insert_data
from generatemaps import generate_map
from utils import postgres_timestamp_format
from local_settings import DB_SETTINGS


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


def gen_map(t_start, t_end, map_name, dow=-1, testing=False):
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
        map_name
    )


def move_to_db(map_name, rid):
    cmd = ['-c',
           '/usr/local/share/pgsql93stable/bin/raster2pgsql -s 32632 -I -C -d '
           '/hardmnt/geopg0/db93stable/appiedi/grass_output/{0}.tiff'
           ' raster_temp |  psql -U appiedi -h geopg -p 50003 '
           '-d appiedi'.format(map_name)
           ]
    out, err, ret = call_command(cmd, shell=True)
    if ret != 0:
        print('ERROR: retval <> 0, something went wrong')
        return
        # move temp_table to definitive one
    with psycopg2.connect(**DB_SETTINGS) as conn:
        with conn.cursor() as cur:
            query = 'WITH r AS (SELECT rast FROM raster_temp LIMIT 1) UPDATE' \
                    ' raster_co3 SET rast=r.rast FROM r WHERE' \
                    ' raster_co3.rid={0};'.format(rid)
            cur.execute(query)


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
    yesterday = \
        time.mktime(datetime.fromtimestamp(t - 24 * 60 * 60).date().timetuple())

    # all inclusive map
    v_print('Generating general map...', verbose)
    gen_map(0.0, t, 'general', testing=testing)
    v_print('Moving to db...')
    move_to_db('general', 1)
    v_print('Done.', verbose)

    # last 7 days
    # week_start = time.mktime(
    #     datetime.fromtimestamp(t - (dt.weekday()*24*60*60)).date().timetuple()
    # )
    v_print('Generating weekly map...', verbose)
    #gen_map(week_start, t, 'week')
    gen_map(t - (7 * 24 * 60 * 60), t, 'week', testing=testing)
    v_print('Moving to db...')
    move_to_db('week', 2)
    v_print('Done.', verbose)

    # day of the week
    dow = (dt.weekday() + 1) % 7
    v_print('Generating DOW map for dow n. {0}'.format(dow), verbose)
    gen_map(0.0, t, 'dow_{0}'.format(dow), dow, testing=testing)
    v_print('Moving to db...')
    move_to_db('dow_{0}'.format(dow), 3 + dow)
    v_print('Done.', verbose)


if __name__ == '__main__':
    main()
