from django.shortcuts import render, redirect

from diagnose.util.wikipedia import DisambiguationError
from diagnose import diagnose
from answer_handler import *
from diagnose.util.wikipedia_util import WikipediaWrapper
from question_db import *

from diagnose.verison_list import CURRENT_QUESTION_VERSION
from diagnose.verison_list import DIAGNOSE_QUESTION_VERSION

def index(request):
    return search_page(request)


def search_page(request):
    """
    A search box, directed to /quiz/ page with the search term
    """
    context_dict = {}
    return render(request, 'autoassess/index.html', context_dict)


def quiz(request):
    """
    The intro view\n
    Requires Input: a search term in request.GET["q"].
    """
    
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}
    
    if 'q' not in request_data or not request_data['q']:
        return redirect('index')
    search_term = request_data['q']

    force_generating_new = False
    if 'f' in request_data and bool(request_data['f']):
        force_generating_new = True
    generate_prereq_question = False
    if 'pre' in request_data and bool(request_data['pre']):
        generate_prereq_question = True
        print 'generate_pre_question'

    version = DIAGNOSE_QUESTION_VERSION
    if 'v' in request_data:
        if request_data['v'] == 'c':
            version = CURRENT_QUESTION_VERSION
        else:
            version = float(request_data['v'])

    try:
        questions = None
        if not force_generating_new:
            try:
                # the search term may not corresponds to a wikipedia entry
                wiki_topic = WikipediaWrapper.page(search_term).title
                questions = load_diagnose_question_set(
                    wiki_topic,
                    version=version)
            except IndexError as e:
                # this is the error it will raise if no questions is founded
                # if there is not questions for this topic in the database
                # then generate and save
                pass
                # questions = diagnose.diagnose(
                #     search_term,
                #     generate_prereq_question=generate_prereq_question)
                # save_diagnose_question_set(
                #     questions,
                #     question_version=CURRENT_QUESTION_VERSION,
                #     force=True)
        if not questions:
            questions = diagnose.diagnose(
                search_term,
                generate_prereq_question=generate_prereq_question,
                version=version)
            save_diagnose_question_set(
                questions=questions,
                version=version,
                force=True)
    except DisambiguationError as dis:
        return disambiguation(request, dis)

    #display feedback answers
    if not('nfb' in request_data and bool(request_data['nfb'])):
        all_answers = []
        for ques in questions:
            answers = WikiQuestionAnswer.objects(question=ques['id'])
            if answers:
                all_answers += [a for a in answers]
        stats = answer_stats(all_answers)
        if stats:
            all_answers = [stats] + all_answers
        response_data['answers'] = all_answers


    response_data['quiz'] = questions
    response_data['search_term'] = search_term

    return render(request, 'autoassess/quiz.html', response_data)


def disambiguation(request, dis=[]):
    """
    The search term may not corresponds to multiple terms, ask the user
    to select the exact term
    :param request:
    :param dis: the object of the DisambiguationError
    :return: a page with multiple related terms returned by Wikipedia API
    """
    if not dis:
        return redirect('index')
    pages = [{'title': option, 'text': description, 'link': link}
             for option, description, link in
             zip(dis.options, dis.descriptions, dis.links)]
    context_dict = {'pages': pages}
    return render(request, 'autoassess/disambiguation.html', context_dict)


def learn(request):
    """
    the learn view, this is displayed after the quiz is completed to display
    the information the user needs
    :param request:
    :return:
    """

    response_data = {}
    response_data['topics'] = []

    user_answers = request.GET
    if 'main_topic' in user_answers:
        main_topic = user_answers['main_topic']
        response_data['topics'].append({
            'title': main_topic,
            'wikipage': WikipediaWrapper.page(main_topic),
            # in the template a summary section is used
            'is_main_topic': True
        })
        # user_answers.pop('main_topic')
    else:
        main_topic = None

    topics_to_learn = []
    # get a list of which questions had correct responses
    for ques_id in user_answers:
        if ques_id == 'main_topic':
            continue
        try:
            if not check_answer_correctness(question_id=ques_id,
                                            ans=user_answers[ques_id]):
                topic = WikiQuestion.objects(id=ques_id)[0].topic
                if topic.lower() == main_topic.lower():
                    continue
                else:
                    topics_to_learn.append(topic)
        except:
            continue

            # if user_answers[ques_id] == 'False' \
            # and ques_id.lower() != main_topic.lower():
            # topics_to_learn.append(ques_id)

    for topic in topics_to_learn:
        response_data['topics'].append(
            {
                'title': topic,
                'wikipage': WikipediaWrapper.page(topic)
            })
    print topics_to_learn
    print response_data
    return render(request, 'autoassess/learn.html', response_data)


# (Deprecated) saving this just in case I will need to use it again
# tree = json.loads(prereq_tree, object_hook=recurhook)
#
# def recurhook(d):
# """
# extra code to fix issues with the way json.loads processes this
# :param d:
# :return:
# """
# if d['children']:
# # d['children'] = json.loads(d['children'], recurhook)
# children = []
#         for child in d['children']:
#             children.append(json.loads(child, object_hook=recurhook))
#         d['children'] = children
#     return d