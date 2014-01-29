from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('appiedi.views',

                       # url(regex='^network/distance/$',
                       #     view=NetworkDistanceClass.as_view(),
                       #     name='network_distance'),

                       url(r'^hello/$', 'hello'),
                       url(r'^covalue/(?P<lon>[\d.]+)/(?P<lat>[\d.]+)', 'co_values'),
                       url(r'^trendaverage/(?P<date_start>\d{4}\-\d{2}\-\d{2})/(?P<date_end>\d{4}\-\d{2}\-\d{2})', 'trend_average'),
                       # def query_average(request, date_s, date_e, lon_s, lon_e, lat_s, lat_e):
                       url(r'^queryaverage/(?P<date_s>\d{4}\-\d{2}\-\d{2})/(?P<date_e>\d{4}\-\d{2}\-\d{2})/(?P<lon_s>[\d.]+)/(?P<lon_e>[\d.]+)/(?P<lat_s>[\d.]+)/(?P<lat_e>[\d.]+)/','query_average')
)

