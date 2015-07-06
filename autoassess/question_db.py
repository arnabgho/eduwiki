__author__ = 'moonkey'

from models import *


def load_diagnose_question_set(topic, version):
    questions = [load_question(topic, version=version)]
    try:
        prereqs = Prereq.objects(
            topic=topic,
            version=version)[0].prereqs
        for pre in prereqs:
            questions.append(load_question(topic=pre, version=version))
    except Exception:
        # error loading prereqs
        # just return the question related to the topic
        pass
    return questions


def save_diagnose_question_set(questions, version, force=False):
    """
    :param questions: topics of later questions are prereqs
            for the topic for the first question
    :return:
    """

    # save prerequisites
    topics = [q['topic'] for q in questions]
    if len(topics) > 1:  # there are prereqs
        main_topic = topics[0]
        prereqs = topics
        if main_topic in prereqs:
            prereqs.remove(main_topic)  # the first topic is the main_topic


        old_prereqs = Prereq.objects.filter(topic=main_topic, version=version)
        if old_prereqs:
            if not force:
                return False
            tosave_prereq = old_prereqs[0]
        else:
            tosave_prereq = Prereq(topic=main_topic, version=version)

        tosave_prereq.prereqs = prereqs
        # ListField([StringField(p) for p in prereqs])
        tosave_prereq.save()

    # save questions
    for q in questions:
        save_question(q, version=version, force=force)
    return True


def load_question(topic, version):
    """
    Note there is a mismatch between "load" and "save.
    We may saved questions with different types, but in "load",
    we only require topic as the input, and return the first questions
    :param topic:
    :return:
    """
    try:
        # # Version checking
        if version is None:
            wiki_question = \
                WikiQuestion.objects(topic=topic).order_by("-version")[0]
        else:
            wiki_question = WikiQuestion.objects(topic=topic, version=version)[
                0]

        ##
        question = {
            'id': wiki_question.id,
            'topic': wiki_question.topic,
            'type': wiki_question.type,
            'question_text': wiki_question.question_text,
            'choices': []
        }

        ## Answers with idx, and correctness
        possible_answers = []
        for idx, c in enumerate(wiki_question['choices']):
            possible_answers.append({
                'text': c,
                'correct': True if idx == wiki_question[
                    'correct_answer'] else False,
                'idx': idx,
            })

        # Random shuffle, the answer order will be different from time to time
        # random.shuffle(possible_answers)
        question['choices'] = possible_answers
    except Exception as e:
        raise e
    return question


def save_question(question, version, force=False):
    """
    Note there is a mismatch between "load" and "save.
    We may saved questions with different types, but in "load",
    we only require topic as the input, and return the first questions
    :param question:
    :param force:
    :return:
    """

    old_questions = WikiQuestion.objects.filter(
        topic=question['topic'],
        type=question['type'],
        version=version
    )
    if old_questions:
        if force:
            wiki_question = old_questions[0]
        else:
            return False
    else:
        wiki_question = WikiQuestion(
            topic=question['topic'],
            type=question['type'],
        )
    if version:
        wiki_question.version = version

    wiki_question.question_text = question['question_text']
    wiki_question.choices = [a['text'] for a in question['choices']]
    for idx, c in enumerate(question['choices']):
        if c['correct']:
            wiki_question.correct_answer = idx

    wiki_question.save()
    return True