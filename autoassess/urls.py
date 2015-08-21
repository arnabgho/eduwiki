from django.conf.urls import patterns, url
from django.conf import settings

from autoassess import views
from autoassess import test_views
from autoassess import add_question_view
from autoassess import edit_question_set

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='home'),
    url(r'^index/$', views.index, name='index'),
    url(r'^quiz/$', views.quiz, name='quiz'),
    url(r'^disambiguation/$', views.disambiguation, name='disambiguation'),
    url(r'^learn/$', views.learn, name='learn'),


    url(r'^single_question$', test_views.single_question,
        name='single_question'),
    url(r'^single_question_submit$', test_views.single_question_submit,
        name='single_question_submit'),

    url(r'^multiple_questions$', test_views.multiple_questions,
        name='multiple_questions'),
    url(r'^multiple_questions_submit$', test_views.multiple_questions_submit,
        name='multiple_questions_submit'),
    url(r'^multiple_questions_single_update$',
        test_views.multiple_questions_single_update,
        name='multiple_questions_single_update'),

    url(r'^add_question$', add_question_view.add_question, name='add_question'),
    url(r'^add_question_submit$', add_question_view.add_question_submit,
        name='add_question_submit'),

    url(r'^edit_manual_question_set$',
        edit_question_set.edit_manual_question_set,
        name='edit_manual_question_set'),
    url(r'^edit_manual_question_set_submit$',
        edit_question_set.edit_manual_question_set_submit,
        name='edit_manual_question_set_submit'),

)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
         'serve',
         {'document_root': settings.MEDIA_ROOT}), )