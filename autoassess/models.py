from mongoengine import *
import random
# Create your models here.

# TODO:: rewrite all the cached terms to database
# TODO:: use mongodb... things are so easy


class WikiQuestion(Document):
    """
    save generated questions,
    """
    WikiQuestionType = (
        "WHAT_IS",
    )
    type = StringField(choices=WikiQuestionType)

    topic = StringField(required=True)
    question_text = StringField(required=True)

    # We can make the options a EmbeddedDocument if needed as we may want to
    # know and store how the options are generated.
    choices = ListField(StringField(), required=True)
    # by deafult, the first option is the right answer
    correct_answer = IntField(required=True)


class Prereq(Document):
    """
    for linking question topics
    """
    topic = StringField(required=True)
    prereqs = ListField(StringField(), required=True)


def load_questions(topic):
    questions = [load_question(topic)]
    prereqs = Prereq.objects.filter(topic=topic)[0].prereqs
    for pre in prereqs:
        questions.append(load_question(topic=pre))
    return questions


def save_questions(questions, force=True):
    """
    :param questions: topics for later topics are prereqs for the question for the first topic
    :return:
    """

    # save prerequisites
    topics = [q['topic'] for q in questions]
    print topics
    main_topic = topics[0]
    old_prereqs = Prereq.objects.filter(topic=main_topic)
    if old_prereqs:
        if not force:
            return False
        tosave_prereq = old_prereqs[0]
    else:
        tosave_prereq = Prereq(topic=main_topic)
    prereqs = topics
    prereqs.pop(0)
    tosave_prereq.prereqs = prereqs  # ListField([StringField(p) for p in prereqs])
    tosave_prereq.save()

    # save questions
    for q in questions:
        save_question(q)

    return True


def load_question(topic):
    """
    Note there is a mismatch between "load" and "save.
    We may saved questions with different types, but in "load",
    we only require topic as the input, and return the first questions
    :param topic:
    :return:
    """
    try:
        wiki_question = WikiQuestion.objects.filter(topic=topic)[0]
        question = {
            'topic': wiki_question.topic,
            'type': wiki_question.type,
            'question_text': wiki_question.question_text,
            'choices': []
        }

        possible_answers = []
        for idx, c in enumerate(wiki_question['choices']):

            possible_answers.append({
                'text': c,
                'correct': True if idx == wiki_question['correct_answer'] else False
            })
        random.shuffle(possible_answers)
        question['choices'] = possible_answers
    except Exception as e:
        raise e
    return question


def save_question(question, force=True):
    old_questions = WikiQuestion.objects.filter(
        topic=question['topic'],
        type=question['type']
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

    wiki_question.question_text = question['question_text']
    wiki_question.choices = [a['text'] for a in question['choices']]
    for idx, c in enumerate(question['choices']):
        if c['correct']:
            wiki_question.correct_answer = idx

    wiki_question.save()
    return True