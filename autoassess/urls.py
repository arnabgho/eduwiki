from django.conf.urls import patterns, url
from django.conf import settings

from autoassess import views
from autoassess import test_views
from autoassess import quiz_display

from autoassess import edit_question_view
from autoassess import edit_question_set


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='home'),
    url(r'^index/$', views.index, name='index'),
    url(r'^quiz_gen/$', views.quiz, name='quiz'),
    url(r'^disambiguation/$', views.disambiguation, name='disambiguation'),
    url(r'^learn/$', views.learn, name='learn'),
    url(r'^quiz_list/$', views.quiz_list, name='quiz_list'),

    url(r'^consent_form$', test_views.consent_form, name='consent_form'),

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

    url(r'^edit_question$', edit_question_view.edit_question, name='edit_question'),
    url(r'^edit_question_submit$', edit_question_view.edit_question_submit,
        name='edit_question_submit'),

    url(r'^edit_manual_question_set$',
        edit_question_set.edit_manual_question_set,
        name='edit_manual_question_set'),
    url(r'^edit_manual_question_set_submit$',
        edit_question_set.edit_manual_question_set_submit,
        name='edit_manual_question_set_submit'),

    url(r'^quiz/$', quiz_display.quiz_new, name='quiz'),
    url(r'^quiz_display/$', quiz_display.quiz_new, name='quiz_display'),
    url(r'^quiz_check/$', quiz_display.quiz_check, name='quiz_check'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
         'serve',
         {'document_root': settings.MEDIA_ROOT}), )