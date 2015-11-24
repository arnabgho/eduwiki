__author__ = 'moonkey'

from django.shortcuts import render, redirect, Http404, HttpResponse
from django.http.response import JsonResponse
from diagnose.util.wikipedia import DisambiguationError
from diagnose import diagnose
from diagnose.util.wikipedia_util import WikipediaWrapper
from django.views.decorators.clickjacking import xframe_options_exempt
from question_db import *
from answer_db import *
from visitorlog import log_visitor_ip
from test_views import id_generator
from diagnose.version_list import *
from models import QuestionLabel


@xframe_options_exempt
def quiz_label(request):
    log_visitor_ip(request)

    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST

    response_data = {}

    # ###### read data from request
    if 'q' not in request_data or not request_data['q']:
        raise Http404
    search_term = request_data['q']

    set_type = CURRENT_QUESTION_SET
    if 's' in request_data:
        if request_data['s'].lower() == 'm':
            set_type = SET_MENTIONED
        if request_data['s'].lower() == 'p':
            set_type = SET_PREREQ

    version = MTURK_QUESTION_VERSION
    if 'v' in request_data:
        if request_data['v'] == 'c':
            version = CURRENT_QUESTION_VERSION
        else:
            version = float(request_data['v'])

    if version < 0:
        set_type = SET_SELF_DEFINED

    if 'assignmentId' not in request_data:
        # user visiting mode not from mturk
        response_data['hitId'] = None

        response_data['assignmentId'] = "EDUWIKI_" + id_generator()
        response_data['workerId'] = "EDUWIKI_" + id_generator()
        response_data['turkSubmitTo'] = '/'
    else:
        assignmentId = request_data['assignmentId'].strip(" ")
        hitId = request_data['hitId']

        if "ASSIGNMENT_ID_NOT_AVAILABLE" == assignmentId:
            # preview mode
            response_data['assignmentId'] = assignmentId
            response_data['hitId'] = hitId
        else:
            # question form mode
            workerId = request_data['workerId']
            turkSubmitTo = request_data['turkSubmitTo']

            response_data['assignmentId'] = assignmentId
            response_data['hitId'] = hitId
            response_data['workerId'] = workerId
            response_data['turkSubmitTo'] = turkSubmitTo
    # ###########################

    try:
        try:
            # the search term may not corresponds to a wikipedia entry
            # TODO:: change this to google site search with the title in it
            try:
                quiz_topic = search_term
                questions, quiz_id = load_diagnose_question_set(
                    quiz_topic, version=version, set_type=set_type,
                    with_meta_info=True, question_shuffle=False)
            except Exception as e:
                print >> sys.stderr, e
                quiz_topic = WikipediaWrapper.page(search_term).title
                questions, quiz_id = load_diagnose_question_set(
                    quiz_topic, version=version, set_type=set_type,
                    with_meta_info=True, question_shuffle=False)
            response_data['quiz_id'] = quiz_id

        except IndexError as e:
            # this is the error it will raise if no questions is founded
            # if there is not questions for this topic in the database
            # then generate and save
            # Do not generate question on server side
            raise Http404("Page Not Found. Please contact webmaster to fix.")

    except DisambiguationError as dis:
        raise dis

    response_data['quiz'] = questions
    response_data['search_term'] = search_term

    response_data['question_order'] = [str(q['id']) for q in questions]

    return render(request, 'test_pages/label_question.html', response_data)


def quiz_label_submit(request):
    log_visitor_ip(request)

    request_data = {}
    if request.method == 'GET':
        request_data = request.GET.dict()
    elif request.method == 'POST':
        request_data = request.POST.dict()

    print request_data

    # save it to db
    qid = request_data['question_id']
    label = QuestionLabel(
        question_id=qid,
        quiz_id=request_data['quiz_id'],
        workerId=request_data['workerId'],
        typo=('grammar_' + qid in request_data),
        multi_answer=('multi_answer_' + qid in request_data),
        pedagogical_utility=int(request_data.pop('pedagogical_' + qid)),
        comment=request_data.pop('comment_' + qid),
    )
    label.save()

    response_data = {}

    return JsonResponse(response_data)