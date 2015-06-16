from django.shortcuts import render, redirect
from diagnose.util.wikipedia import DisambiguationError
from diagnose import diagnose
from diagnose import search_wikipage
from .models import *


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
    response_data = {}
    if 'q' not in request.GET or not request.GET['q']:
        return redirect('index')
    search_term = request.GET['q']

    force_generating_new = False
    if 'f' in request.GET and bool(request.GET['f']):
        force_generating_new = True

    try:
        # TODO:: load question[s] | save&load prereq hierarchy
        if not force_generating_new:
            try:
                # the search term may not corresponds to a wikipedia entry
                wiki_topic = search_wikipage.get_wikipage(search_term).title
                questions = load_questions(wiki_topic)
            except IndexError as e:
                # this is the error it will raise if no questions is founded
                # if there is not questions for this topic in the database
                # then generate and save
                questions = diagnose.diagnose(search_term)
                save_questions(questions)
        else:
            questions = diagnose.diagnose(search_term)
            save_questions(questions)
    except DisambiguationError as dis:
        return disambiguation(request, dis)
    # converted into a python dictionary

    # TODO:: why use session here? Way to substitute?
    # request.session['tree'] = prereq_tree
    response_data['quiz'] = questions
    response_data['search_term'] = search_term
    # save it to context

    return render(request, 'autoassess/quiz.html', response_data)


def disambiguation(request, dis=[]):
    """
    The search term may not corresponds to multiple terms, ask the user to select the exact term
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
            'wikipage': search_wikipage.get_wikipage(main_topic),
            'is_main_topic': True
        })
    else:
        main_topic = None

    topics_to_learn = []
    # get a list of which questions had correct responses
    for ans in user_answers:
        if user_answers[ans] == 'False' and ans.lower() != main_topic.lower():
            topics_to_learn.append(ans)

    for topic in topics_to_learn:
        response_data['topics'].append(
            {
                'title': topic,
                'wikipage': search_wikipage.get_wikipage(topic)
            })
    print topics_to_learn
    print response_data
    return render(request, 'autoassess/learn.html', response_data)


# (Deprecated) saving this just in case.
# tree = json.loads(prereq_tree, object_hook=recurhook)
# def recurhook(d):
# """
# extra code to fix issues with the way json.loads processes this
# :param d:
#     :return:
#     """
#     if d['children']:
#         # d['children'] = json.loads(d['children'], recurhook)
#         children = []
#         for child in d['children']:
#             children.append(json.loads(child, object_hook=recurhook))
#         d['children'] = children
#     return d
