__author__ = 'moonkey'

from django.conf.urls import patterns, url
from django.conf import settings

from nameall import views

urlpatterns = patterns(
    '',
    url(r'^$', views.name_home, name='name_home'),
    url(r'^name_submit', views.name_submit, name='name_submit'),
    url(r'^name_report', views.name_report, name='name_report'),
)