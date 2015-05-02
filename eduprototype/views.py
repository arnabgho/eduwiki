from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpRequest
from django.template import RequestContext
from diagnose.diagnose import query
from diagnose.wikipedia import DisambiguationError, page
from random import randint
import json


# the index page view
def index(request):
    context = RequestContext(request)
    context_dict = {}
    return render_to_response('eduprototype/index.html', context_dict, context)


# the intro view
def quiz(request):
    if 'q' not in request.GET or not request.GET['q']:
        return redirect('index')
    searchterm = request.GET['q']
    context_dict = {}
    context = RequestContext(request)
    try:
        json_tree = query(searchterm)  # comes out in a JSON string
    except DisambiguationError as dis:
        return disambiguation(request, dis)
    # converted into a python dictionary
    tree = json.loads(json_tree, object_hook=recurhook)
    request.session['tree'] = tree
    context_dict['quiz'] = make_quiz(tree)
    context_dict['tree'] = tree          # save it to context
    return render_to_response('eduprototype/quiz.html', context_dict, context)


def disambiguation(request, dis=[]):
    if not dis:
        return redirect('index')
    pages = [{'title': option, 'text': description, 'link': link}
             for option, description, link in
             zip(dis.options, dis.descriptions, dis.links)]
    context_dict = {'pages': pages}
    context = RequestContext(request)
    return render_to_response('eduprototype/disambiguation.html',
                              context_dict, context)


# the learn view, this is displayed after the quiz is completed to display
# the information the user needs
def learn(request):
    context = RequestContext(request)
    if 'q0' not in request.GET or not request.GET['q0']:
        return redirect('index')
    # get a list of which questions had correct responses
    responses = quiz_correctness(request)

    # note: this is weird because it pulls from session vars, maybe fix later
    # other note: it's also kinda hard-codey
    tree = request.session['tree']
    # get the topics of the main subject
    main_topic = tree['text']
    subtopics = [child if not correct else None for child, correct in
                 zip(tree['children'], responses)]

    context_dict = {'tree': tree, "subtopics": subtopics}
    return render_to_response('eduprototype/learn.html', context_dict, context)


# code for assembling the dicts needed for the quizzes
def make_quiz(topic):
    # goes though the quizzes and returns a list of dicts for the quiz page
    children = topic['children']
    quiz = []
    for i, child in enumerate(children):
        quiz.append(make_question(child, i))
    return quiz


def make_question(topic, num):
    # a whole bunch of ugly code to randomize the answers but keep
    # track of which one is correct
    answers_prerand = topic['distractors']
    description = topic['description']
    answers_prerand.insert(0, description)
    answers = []
    l = len(answers_prerand)
    found = False
    for i in range(l):
        correct = "incorrect"
        rand = randint(0, len(answers_prerand) - 1)
        if rand == 0 and not found:
            correct = "correct"
            found = True
        answers.append({'text': answers_prerand.pop(rand), 'correct': correct})
    return {'title': topic['title'], 'number': num, 'answers': answers}


# really ugly code to take the request to learn and get back a list
# of booleans representing whether or not the user answered correctly
def quiz_correctness(request):
    i = 0
    while ('q'+str(i)) in request.GET:
        i += 1
    responses_raw = [request.GET['q'+str(j)] for j in range(i)]
    responses = []
    for response in responses_raw:
        if response == "correct":
            responses.append(True)
        else:
            responses.append(False)
    return responses


# extra code to fix issues with the way json.loads processes this

def recurhook(d):
    if d['children']:
        # d['children'] = json.loads(d['children'], recurhook)
        children = []
        for child in d['children']:
            children.append(json.loads(child, object_hook=recurhook))
        d['children'] = children
    return d
