from django.shortcuts import render
from answer_db import *
import random
from diagnose.version_list import *


def edit_manual_question_set(request):
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET.dict()
    elif request.method == 'POST':
        request_data = request.POST.dict()
    response_data = {}

    ### Retrieve all the question sets that are manually added
    manual_sets = QuestionSet.objects(version=MANUALLY_ADDED)
    response_data['all_manual_sets'] = manual_sets
    ### End

    question_set = None
    id = request_data.get('id', None)
    if id:
        try:
            question_set = QuestionSet.objects(id=id)[0]
        except Exception as e:
            print e

    if request.method == 'GET':
        pass

    if request.method == 'POST':
        set_topic = request_data.get('set_topic', None)
        version = float(request_data.get('version', -1.0))

        questions = []
        question_id_keys = [k for k in request_data if k.startswith('question')]
        question_number = len(question_id_keys)
        for idx in range(0, question_number):
            question_id = request_data['question' + str(idx)]
            if question_id:
                try:
                    question = WikiQuestion.objects(id=question_id)[0]
                    questions.append(question)
                except Exception as e:
                    print e
        random_shuffle = request_data.get('random_shuffle', False)
        if random_shuffle:
            random.shuffle(questions)

        if not question_set:
            question_set = QuestionSet(
                set_topic=set_topic,
                questions=questions,
                version=version
            )
        else:
            question_set.update(
                set_topic=set_topic,
                questions=questions,
                version=version
            )

        question_set.save()
        question_set.reload()
        response_data['success'] = True

    if question_set:
        response_data['question_set'] = question_set
        response_data['question_ids'] = [q.id for q in question_set.questions]
    else:
        response_data['question_ids'] = []

    response_data['question_ids'] += [''] * 5

    return render(request, 'test_pages/edit_manual_question_set.html',
                  response_data)
    # TODO:: show all the manually added question sets on the top (or bottom)


def edit_manual_question_set_submit(request):
    return edit_manual_question_set(request)