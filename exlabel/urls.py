__author__ = 'moonkey'

from django.conf.urls import patterns, url
from django.conf import settings

from exlabel import views

urlpatterns = patterns(
    '',
    url(r'^$', views.label_guess, name='exlabel'),
    url(r'^label_submit$', views.label_submit, name='exlabel_submit'),

)