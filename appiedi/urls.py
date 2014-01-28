from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('appiedi.views',

                       # url(regex='^network/distance/$',
                       #     view=NetworkDistanceClass.as_view(),
                       #     name='network_distance'),

                       url(r'^hello/$', 'hello'),
                       url(r'^covalue/(?P<lat>[\d.]+)/(?P<lon>[\d.]+)', 'co_values'),
                       url(r'^trendaverage/(?P<date_start>\d{4}\-\d{2}\-\d{2})/(?P<date_end>\d{4}\-\d{2}\-\d{2})', 'trend_average'),
)

