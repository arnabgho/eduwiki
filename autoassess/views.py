from django.shortcuts import render, redirect

from diagnose.util.wikipedia import DisambiguationError
from diagnose import diagnose
from question_db import *
from answer_db import *
from diagnose.util.wikipedia_util import WikipediaWrapper
from diagnose.version_list import *
from answer_analysis import answer_stat


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

    generate_prereq_question = WITH_PREREQ
    if 'pre' in request_data:
        if request_data['pre'].lower() == 't':
            generate_prereq_question = True
        elif request_data['pre'].lower() == 'f':
            generate_prereq_question = False

    set_type = CURRENT_QUESTION_SET
    if 's' in request_data:
        if request_data['s'].lower() == 'm':
            set_type = SET_MENTIONED
        if request_data['s'].lower() == 'p':
            set_type = SET_PREREQ

    version = DIAGNOSE_QUESTION_VERSION
    if 'v' in request_data:
        if request_data['v'] == 'c':
            version = CURRENT_QUESTION_VERSION
        else:
            version = float(request_data['v'])

    if version < 0:
        set_type = SET_SELF_DEFINED

    try:
        questions = None
        if not force_generating_new:
            try:
                # the search term may not corresponds to a wikipedia entry
                quiz_topic = search_term
                questions, quiz_id = load_diagnose_question_set(
                    quiz_topic, version=version, set_type=set_type,
                    with_meta_info=True, question_shuffle=False)
            except Exception as e:
                print >> sys.stderr, e
                try:
                    quiz_topic = WikipediaWrapper.page(search_term).title
                    questions, quiz_id = load_diagnose_question_set(
                        quiz_topic, version=version, set_type=set_type,
                        with_meta_info=True, question_shuffle=False)
                except IndexError or TypeError as e:
                    # this is the error it will raise if no questions is founded
                    # if there is not questions for this topic in the database
                    # then generate and save

                    # Type Error: 'NoneType' object is not iterable
                    print "Failed to load question for", search_term, e

        if not questions:
            questions = diagnose.diagnose(
                search_term,
                generate_prereq_question=generate_prereq_question,
                version=version,
                set_type=set_type)
            save_diagnose_question_set(
                questions=questions,
                version=version,
                force=True,
                set_type=set_type)
    except DisambiguationError as dis:
        return disambiguation(request, dis)

    # display feedback answers for a single question
    if 'qfb' in request_data and bool(request_data['qfb']):
        all_answers = []
        for ques in questions:
            if 'id' in ques:
                answers = WikiQuestionAnswer.objects(question=ques['id'])
                if answers:
                    question_answers = [a for a in answers]
                    stat = answer_stat(question_answers)
                    if stat:
                        question_answers = [stat] + question_answers
                    all_answers += question_answers
        if all_answers:
            response_data['answers'] = all_answers

    # display feedback for a quiz's questions
    if not ('nsfb' in request_data and bool(request_data['nsfb'])):
        try:
            all_stats = []
            all_answers = []
            question_ans = {}
            quiz = QuestionSet.objects(id=quiz_id)[0]
            quiz_answers = QuizAnswers.objects(quiz=quiz)
            for quiz_ans in quiz_answers:
                # quiz_ans = QuizAnswers()
                final_answers = quiz_ans.quiz_final_answers
                for final_ans in final_answers:
                    if final_ans.question.topic not in question_ans:
                        question_ans[final_ans.question.topic] = []
                    question_ans[final_ans.question.topic].append(final_ans)
            for topic in question_ans:
                stat = answer_stat(question_ans[topic])
                all_stats.append(stat)
                all_answers += question_ans[topic]
            response_data['answers'] = all_stats + all_answers
        except Exception as e:
            print "Failed to retrieve the quiz answers"
            print e

    response_data['quiz'] = questions
    response_data['search_term'] = search_term

    return render(request, 'autoassess/quiz.html', response_data)


def quiz_list(request):
    request_data = {}
    if request.method == 'GET':
        request_data = request.GET
    elif request.method == 'POST':
        request_data = request.POST
    response_data = {}

    quizzes = [q for q in QuestionSet.objects(version__gte=0.25)]
    quizzes += [q for q in QuestionSet.objects(version__lte=-1.0)]
    # print type(quizzes[0])
    response_data['quizzes'] = quizzes
    return render(request, 'autoassess/quiz_list.html', response_data)


def disambiguation(request, dis=None):
    """
    The search term may not corresponds to multiple terms, ask the user
    to select the exact term
    :param request:
    :param dis: the object of the DisambiguationError
    :return: a page with multiple related terms returned by Wikipedia API
    """
    if not dis:
        print >> sys.stderr, dis
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
    # for child in d['children']:
    # children.append(json.loads(child, object_hook=recurhook))
    # d['children'] = children
    # return d