from django.conf.urls import patterns, url
from django.conf import settings

from autoassess import views
from autoassess import test_views

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^index/$', views.index, name='index'),
    url(r'^quiz/$', views.quiz, name='quiz'),
    url(r'^disambiguation/$', views.disambiguation, name='disambiguation'),
    url(r'^learn/$', views.learn, name='learn'),
    url(r'^single_question$', test_views.single_question, name='single_question'),
    url(r'^question_submit$', test_views.question_submit, name='question_submit'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )