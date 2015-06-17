__author__ = 'moonkey'

from django.shortcuts import render, redirect, Http404
from diagnose.util.wikipedia import DisambiguationError
from diagnose import diagnose
from diagnose import search_wikipage
from .models import *


def single_question(request):
    """
    The intro view\n
    Requires Input: a search term in request.GET["q"].
    """
    response_data = {}
    if 'q' not in request.GET or not request.GET['q']:
        raise Http404
    search_term = request.GET['q']

    try:
        try:
            # the search term may not corresponds to a wikipedia entry
            wiki_topic = search_wikipage.get_wikipage(search_term).title
            questions = load_questions(wiki_topic)
        except IndexError as e:
            # this is the error it will raise if no questions is founded
            # if there is not questions for this topic in the database
            # then generate and save
            questions = diagnose.diagnose(search_term, depth=1)
            save_questions(questions)
    except DisambiguationError as dis:
        raise dis

    response_data['quiz'] = questions
    response_data['search_term'] = search_term

    return render(request, 'autoassess/single_question.html', response_data)


def question_submit(request):
    response_data = {}
    return render(request, 'autoassess/single_question.html', response_data)