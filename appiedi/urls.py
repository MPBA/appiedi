from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('appiedi.views',

                       # url(regex='^network/distance/$',
                       #     view=NetworkDistanceClass.as_view(),
                       #     name='network_distance'),

                       url(r'^hello/$', 'hello'),
)

