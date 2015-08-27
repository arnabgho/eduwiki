from django.shortcuts import render
from answer_db import *
from diagnose.version_list import *


def edit_question(request):
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET.dict()
    elif request.method == 'POST':
        request_data = request.POST.dict()
    response_data = {}

    # ## Retrieve all the question sets that are manually added
    manual_questions = WikiQuestion.objects(version=MANUALLY_ADDED)
    response_data['all_manual_questions'] = manual_questions
    ### End


    question = None
    id = request_data.get('id', None)
    if id:
        try:
            question = WikiQuestion.objects(id=id)[0]
        except Exception as e:
            print e

    if request.method == 'GET':
        pass

    if request.method == 'POST':
        type = request_data.get('type', '')
        topic = request_data.get('topic', '')
        quiz_topic = request_data.get('quiz_topic', '')
        question_text = request_data.get('question_text', '')

        choices = []
        choice_keys = [k for k in request_data if k.startswith('choice')]
        choice_number = len(choice_keys)
        for idx in range(0, choice_number):
            choice = request_data.get('choice' + str(idx), '')
            if choice:
                choices.append(choice)
        print choices
        random_shuffle = request_data.get('random_shuffle', False)
        if random_shuffle:
            random.shuffle(choices)

        # by default, the first option is the right answer
        correct_answer = int(request_data.pop('correct_answer', 0))

        # for question generation
        version = float(request_data.pop('version', MANUALLY_ADDED))

        if not question:
            question = WikiQuestion(
                type=type,
                topic=topic,
                quiz_topic=quiz_topic,
                question_text=question_text,
                choices=choices,
                correct_answer=correct_answer,
                version=version
            )
        else:
            if not question_text:
                question_text = question.question_text

            question.type = type
            question.topic = topic
            question.quiz_topic = quiz_topic
            question.question_text = question_text
            question.choices = choices
            question.correct_answer = correct_answer
            question.version = version
            # question.update(
            #     type=type,
            #     topic=topic,
            #     quiz_topic=quiz_topic,
            #     question_text=question_text,
            #     choices=choices,
            #     correct_answer=correct_answer,
            #     version=version
            # )

        question.save()

        question.reload()

        response_data['success'] = True

    if question:
        response_data['question'] = question
        response_data['choices'] = question.choices
    else:
        response_data['choices'] = []

    response_data['choices'] += [''] * 4

    # response_data = {
    #     'type': type,
    #     'topic': topic,
    #     'quiz_topic': quiz_topic,
    #     'question_text': question_text,
    #     'choices': choices,
    #     'correct_answer': correct_answer,
    #     'version': version
    # }

    return render(request, 'test_pages/edit_question.html', response_data)


def edit_question_submit(request):
    return edit_question(request)