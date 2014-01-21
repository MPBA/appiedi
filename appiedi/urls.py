from django.conf.urls import patterns, include, url

from django.contrib import admin
from .views import (NetworkDistanceClass, NetworkDistanceStep2Class, NetworkDistanceStep3Class,
                    ProcessStatus, download_zip_file,
                    NetworkInferenceClass, NetworkInferenceStep2Class, NetworkInferenceStep3Class,
                    NetworkStabilityClass, NetworkStabilityStep2Class, NetworkStabilityStep3Class)

admin.autodiscover()

urlpatterns = patterns('appiedi.views',

                       # url(regex='^network/distance/$',
                       #     view=NetworkDistanceClass.as_view(),
                       #     name='network_distance'),

                       url(r'^hello/$', 'hello'),
)

