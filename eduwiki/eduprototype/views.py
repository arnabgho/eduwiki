from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpRequest
from django.template import RequestContext
from diagnose.diagnose import query
from random import randint
import json

#the index page view
def index(request):
    context = RequestContext(request)
    context_dict = {}
    """
    if 'tree' in request.session:
        context_dict = {'tree': request.session['tree']}
        #return render_to_response('eduprototype/intro.html', context_dict, context)
        request.GET['q'] = request.session['tree']
        return intro(request, context_dict)
    else:
        return render_to_response('eduprototype/index.html', context_dict, context)
    """
    return render_to_response('eduprototype/index.html', context_dict, context)

#the intro view
def intro(request, context_dict_in={}):
    if not 'q' in request.GET or not request.GET['q']:
        return render_to_response('eduprototype/index.html')
    search_name_url = request.GET['q']
    context = RequestContext(request)
    context_dict = context_dict_in
    json_tree = query(search_name_url)  #comes out in a JSON string
    tree = json.loads(json_tree, object_hook=recurhook)  #converted into a python dictionary
    context_dict['quiz'] = make_quiz(tree)
    context_dict['tree'] = tree          #save it to context
    return render_to_response('eduprototype/intro.html', context_dict, context)

def quiz(request):
    context = RequestContext(request)
    #tree = request.session['tree']
    #context_dict = {'tree': tree}
    context_dict = {}
    return render_to_response('eduprototype/quiz.html', context_dict, context)


#code for assembling the dicts needed for the quizzes

def make_quiz(topic):
    children = topic['children']
    quiz = []
    for i, child in enumerate(children):
        quiz.append(make_question(child, i))
    return quiz

def make_question(topic, num):
    #a whole bunch of ugly code to randomize the answers but keep
    #track of which one is correct
    answers_prerand = topic['distractors']
    description = topic['description']
    answers_prerand.insert(0, description)
    answers = []
    l = len(answers_prerand)
    found = False
    for i in range(l):
        correct = "false"
        rand = randint(0, len(answers_prerand) - 1)
        if rand == 0 and found == False:
            correct = "true"
            found = True
        answers.append({ 'text' : answers_prerand.pop(rand), 'correct' : correct })
    return { 'title': topic['title'], 'number': num, 'answers' : answers }


#extra code to fix issues with the way json.loads processes this

def recurhook(d):
    if d['children']:
        #d['children'] = json.loads(d['children'], recurhook)
        children = []
        for child in d['children']:
            children.append(json.loads(child, object_hook = recurhook))
        d['children'] = children
    return d