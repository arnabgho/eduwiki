from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpRequest
from django.template import RequestContext
from diagnose.diagnose import query
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
    tree = json.loads(json_tree, object_hook=recurhook)
    #tree = json2obj(json_tree)          #convert to python object
    #request.session['tree'] = tree      #save it to session  
    context_dict['tree'] = tree          #save it to context
    return render_to_response('eduprototype/intro.html', context_dict, context)

def quiz(request):
    context = RequestContext(request)
    if not request.session.get('tree'):
        return HttpResponse("Sorry, something went wrong. (views.intro)")
    tree = request.session['tree']
    context_dict = {'tree': tree}
    return render_to_response('eduprototype/quiz.html', context_dict, context)

def search(request, searchstring):
    #send searchstring to diagnose
    tree = None #get response from searchstring
    request.session['tree'] = tree
    return intro(HttpRequest())


#extra code to enable making JSON-style dictionaries into objects

def recurhook(d):
    if d['children']:
        #d['children'] = json.loads(d['children'], recurhook)
        children = []
        for child in d['children']:
            children.append(json.loads(child, object_hook = recurhook))
        d['children'] = children
    return d