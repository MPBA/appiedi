from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from tojson import render_to_json
from models import TelecomDataset
from pyhive.extra.django import DjangoModelSerializer
from pyhive.serializers import ListSerializer
from pyhive.modifiers import exclude_fields
from datetime import datetime, timedelta

import requests
import json
import psycopg2

from local_settings import DB_SETTINGS


# Create your views here.
@render_to_json(mimetype='application/json')
def hello(request):
    td = TelecomDataset.objects.filter(pressure__gte=1)

    #ser = ListSerializer(item_serializer=DjangoModelSerializer(
        #[exclude_fields(['is_staff', 'is_superuser', 'password'])]
    #))
    #jsondata = ser.serialize(td)

    url = 'http://collector-svil.mobileterritoriallab.eu/sensordrone/api/'
    payload = {'timestamp_start': '21/01/2014 00:00', 'timestamp_end': '22/01/2014 00:00'}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    #a = {'asd': 'asd', 'rec': 1, 'timestamp': '2014-01-21 11:11:11', 'data': jsondata, 'telecom': r.json()}
    return r.json()


@render_to_json(mimetype='application/json')
def co_values(request, lon, lat):
    res = {'error': None, 'results': {}}
    # query = \
    #     'SELECT ST_Value(rast, 1, st_transform(st_setsrid(st_makepoint({long},{lat}),4326),32632),' \
    #     ' FALSE) FROM raster_co3 WHERE raster_co3.rid = {rid};'
    try:
        lon = float(lon)
        lat = float(lat)
    except ValueError:
        # wtf? this should definitely NOT happen.
        return {'error:': 'Coordinates are not valid.'}

    conn = psycopg2.connect(**DB_SETTINGS)
    try:
        # total
        # cur.callproc('query_raster', ['1', lon, lat])
        cur = conn.cursor()
        cur.callproc('query_raster', ['co_general', lon, lat])
        res['results']['total'] = cur.fetchone()[0]
        cur.close()

        # weekly
        cur = conn.cursor()
        cur.callproc('query_raster', ['co_weekly', lon, lat])
        res['results']['weekly'] = cur.fetchone()[0]
        cur.close()

        # dow
        cur = conn.cursor()
        dow = (datetime.now().weekday() + 1) % 7
        cur.callproc('query_raster', ['co_dow{0}'.format(dow), lon, lat])
        res['results']['dow'] = cur.fetchone()[0]
        cur.close()

        # yesterday daily average
        cur = conn.cursor()
        yesterday = (datetime.now() - timedelta(days=1)).date()
        cur.callproc('get_daily_average', [yesterday])
        res['results']['daily_average'] = cur.fetchone()[0]
        cur.close()

        # trend average
        cur = conn.cursor()
        ta_start = (datetime.now() - timedelta(days=8)).date()
        ta_end = (datetime.now() - timedelta(days=1)).date()
        cur.callproc('get_trend_average', [ta_start, ta_end])
        res['results']['trend_average'] = dict(cur.fetchall())
        cur.close()
        conn.commit()
    except Exception as e:
        res['error'] = str(e)
    finally:
        conn.close()

    return res


@render_to_json(mimetype='application/json')
def trend_average(request, date_start, date_end):
    res = {'error:': None, 'results': {}}

    conn = psycopg2.connect(**DB_SETTINGS)
    cur = conn.cursor()
    try:
        cur.callproc('get_trend_average', [date_start, date_end])
        res['results'] = dict(cur.fetchall())
        conn.commit()
    except Exception as e:
        res['error'] = str(e)
    finally:
        cur.close()
        conn.close()

    return res


@render_to_json(mimetype='application/json')
def query_average(request, date_s, date_e, lon_s, lon_e, lat_s, lat_e):
    res = {'error': None, 'result': None}

    # I hate to split between lines
    query = 'SELECT AVG(co) FROM telecom_dataset_trento WHERE latitude >= ' \
            '%s AND latitude <= %s AND longitude >= %s AND' \
            ' longitude <= %s AND mtl_timestamp >=' \
            ' %s::DATE::TIMESTAMP AND mtl_timestamp <= ' \
            '(%s::DATE + 1)::TIMESTAMP;'

    conn = psycopg2.connect(**DB_SETTINGS)
    cur = conn.cursor()
    try:
        cur.execute(query, (lat_s, lat_e, lon_s, lon_e, date_s, date_e))
        res['result'] = cur.fetchone()[0]
        conn.commit()

    except (TypeError, psycopg2.Error) as e:
        res['error'] = str(e)
    finally:
        cur.close()
        conn.close()
    return res


@render_to_json(mimetype='application/json')
def pathfinder(request, lon_s, lat_s, lon_e, lat_e):
    try:
        (lon_s, lat_s, lon_e, lat_e) = map(float, (lon_s, lat_s, lon_e, lat_e))
    except ValueError:
        return {'result': None, 'error': 'Coordinates are not valid.'}
    return {
        'result': [
            [11.12040, 46.06962, 1.12]
            [11.12118, 46.06970, 4.34]
            [11.12120, 46.06898, 10.43]
            [11.12122, 46.06888, 15.545]
            [11.12129, 46.06851, 3.12]
            [11.12139, 46.06800, 4.234]
            [11.12147, 46.06773, 3.00]
            [11.12186, 46.06765, 6.975]
            [11.12178, 46.06758, 7.432]
            [11.12187, 46.06716, 8.22]
            [11.12102, 46.06706, 0]
        ],
        'error': None
    }

# def process_list(request):
#     try:
#         session = request.session.get('runp', [])
#
#         if len(session):
#             runp = RunningProcess.objects.filter(pk__in=session)
#         else:
#             runp = []
#
#         context = {
#             'runp': runp
#         }
#
#         return render(request, 'engine/my_process_list.html', context)
#     except ConnectionError, e:
#         context = None
#         messages.add_message(request, messages.ERROR, 'Sorry, error connecting to server. Try again.')
#     except Exception, e:
#         context = None
#         messages.add_message(request, messages.ERROR, 'Sorry, unexpected error occured. Try again.')
#     return render(request, 'engine/my_process_list.html', context)
#
#
# def process_graph(request, uuid, key, idx):
#     try:
#         runp = RunningProcess.objects.get(task_id=uuid)
#     except RunningProcess.DoesNotExist:
#         raise Http404
#
#     result = runp.result
#     try:
#         url = result[key]['json_files'][int(idx)]
#         context = {
#             'url': url,
#             'key': key,
#             'idx': idx,
#             'runp':runp
#         }
#     except KeyError:
#         context = None
#         messages.add_message(request, messages.ERROR, 'No json available for graph visualization.')
#
#     return render(request, 'engine/json_preview.html', context)

