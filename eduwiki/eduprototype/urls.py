from django.conf.urls import patterns, url
from eduprototype import views
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^intro/$', views.intro, name='intro'),
    url(r'^quiz/$', views.quiz, name='quiz'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )