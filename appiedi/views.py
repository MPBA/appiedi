from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render


# Create your views here.
def hello(request):
    return HttpResponse('Hello Mondo', mimetype='text/plain')


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

