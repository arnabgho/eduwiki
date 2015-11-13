__author__ = 'moonkey'

from django.shortcuts import render, redirect, Http404, HttpResponse

from diagnose.util.wikipedia import DisambiguationError
from diagnose import diagnose
from question_db import *
from answer_db import *
from diagnose.util.wikipedia_util import WikipediaWrapper
from diagnose.version_list import *
from answer_analysis import answer_stat
from visitorlog import log_visitor_ip
from error_db import save_error
import string
from test_views import id_generator
import json


def quiz_new(request):
    """

    :param request:
    :return:
    """
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
            #TODO:: change this to google site search with the title in it
            try:
                quiz_topic = search_term
                questions, quiz_id = load_diagnose_question_set(
                    quiz_topic, version=version, set_type=set_type,
                    with_meta_info=True, question_shuffle=True)
            except Exception as e:
                print >> sys.stderr, e
                quiz_topic = WikipediaWrapper.page(search_term).title
                questions, quiz_id = load_diagnose_question_set(
                    quiz_topic, version=version, set_type=set_type,
                    with_meta_info=True, question_shuffle=True)
                # try:
                #     quiz_topic = WikipediaWrapper.page(search_term).title
                # except Exception as e:
                #   #  if connecting to wikipedia server fails
                # quiz_topic = search_term
            # questions, quiz_id = load_diagnose_question_set(
            #     quiz_topic, version=version, set_type=set_type,
            #     with_meta_info=True, question_shuffle=True)

            response_data['quiz_id'] = quiz_id

        except IndexError as e:
            # this is the error it will raise if no questions is founded
            # if there is not questions for this topic in the database
            # then generate and save
            # Do not generate question on server side
            raise Http404("Page Not Found. Please contact webmaster to fix.")

    except DisambiguationError as dis:
        raise dis

    if not questions:
        # no question loaded,
        # put this in the request queue, instead of generating it.
        return quiz_request(request)

    response_data['quiz'] = questions
    response_data['search_term'] = search_term

    response_data['question_order'] = [str(q['id']) for q in questions]

    return render(request, 'autoassess/quiz_display.html', response_data)


def quiz_check(request):
    log_visitor_ip(request)
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET.dict()
    elif request.method == 'POST':
        request_data = request.POST.dict()

    print request_data
    response_data = check_answers(request_data)
    print response_data
    return render(request, 'autoassess/learn.html', response_data)


def check_answers(ans_data):
    response_data = {}
    # ##### Extract fields
    hitId = ans_data.pop('hitId')
    assignmentId = ans_data.pop('assignmentId')
    workerId = ans_data.pop('workerId')
    turkSubmitTo = ans_data.pop('turkSubmitTo')

    # ######## FOR THE WHOLE QUIZ
    # quiz_id = ans_data.pop('quiz_id', '')
    # quiz = QuestionSet.objects(id=quiz_id)[0]

    # ## All the left keys are question specific keys
    ans_data_keys = ans_data.keys()
    # ## get all the questions ids that are with an answer
    question_ids = [k[len("question_answer_"):] for k in ans_data_keys if
                    k.startswith("question_answer_")]

    print question_ids
    # ###############################
    # ### Answer Display Part
    # ###############################
    response_data['right_answers'] = []
    for question_id in question_ids:
        try:
            wiki_question = WikiQuestion.objects(id=question_id)[0]

            if question_id not in question_ids:
                print >> sys.stderr, "Question answer missing:", question_id
                continue
            question_with_answer = {}

            user_answer = int(ans_data['question_answer_' + question_id])

            question_with_answer['question_text'] = wiki_question.question_text
            question_with_answer['right_answer'] = wiki_question.choices[
                wiki_question.correct_answer]
            if wiki_question.correct_answer != user_answer:
                question_with_answer['learner_answer'] = wiki_question.choices[
                    user_answer]
            response_data['right_answers'].append(question_with_answer)
        except:
            continue

    ################################
    #### Topic Learning Part
    ################################
    response_data['topics'] = []
    if 'main_topic' in ans_data:
        main_topic = ans_data['main_topic']
        response_data['topics'].append({
            'title': main_topic,
            'wikipage': WikipediaWrapper.page(main_topic),
            # in the template a summary section is used
            'is_main_topic': True
        })
        # request_data.pop('main_topic')
    else:
        main_topic = None

    topics_to_learn = []
    # get a list of which questions had correct responses
    for question_id in question_ids:
        try:
            wiki_question = WikiQuestion.objects(id=question_id)[0]
            if wiki_question.topic == main_topic:
                continue
            user_answer = int(ans_data['question_answer_' + question_id])
            if not check_answer_correctness(question_id=question_id,
                                            ans=user_answer):
                topic = WikiQuestion.objects(id=question_id)[0].topic
                if topic.lower() == main_topic.lower():
                    continue
                else:
                    topics_to_learn.append(topic)
        except:
            continue

    for topic in topics_to_learn:
        response_data['topics'].append(
            {
                'title': topic,
                'wikipage': WikipediaWrapper.page(topic)
            })
    return response_data


def quiz_request(request):
    log_visitor_ip(request)

    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}

    search_term = request_data.get('q', None)
    try:
        if search_term:
            old_qr = QuizRequest.objects(request_topic=search_term)
            if not old_qr:
                qr = QuizRequest(request_topic=search_term)
                qr.save()
            response_data['search_term'] = search_term
    except:
        pass
    return render(request, 'autoassess/quiz_request.html', response_data)