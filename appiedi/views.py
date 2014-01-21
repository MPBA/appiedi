from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from tojson import render_to_json
from models import TelecomDataset
from pyhive.extra.django import DjangoModelSerializer
from pyhive.serializers import ListSerializer
from pyhive.modifiers import exclude_fields
import requests
import json


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

