from __future__ import division

__author__ = 'moonkey'

from models import *
import datetime
from collections import Counter


def check_answer_correctness(question_id, ans):
    try:
        question = WikiQuestion.objects(id=question_id)[0]
        if question.correct_answer == int(ans):
            correctness = True
        else:
            correctness = False

        return correctness
    except Exception:
        raise ValueError("No corresponding question found for the answer.")


def save_answer(ans_data):
    if not ans_data:
        return

    # ##### Extract fields
    hitId = ans_data.pop('hitId')
    assignmentId = ans_data.pop('assignmentId')
    workerId = ans_data.pop('workerId')
    turkSubmitTo = ans_data.pop('turkSubmitTo')

    topic_confidence = ans_data.pop('topic_confidence', -1)
    question_confidence = ans_data.pop('question_confidence', -1)
    comment = ans_data.pop('comment', "")
    comment_guess = ans_data.pop('comment_guess', "")

    topic_confidence_time_delta = ans_data.pop('topic_confidence_time_delta',
                                               -1)
    submit_time_delta = ans_data.pop('submit_time_delta', -1)

    is_reasonable_question = ans_data.pop('is_reasonable_question', None)
    if is_reasonable_question == 'True':
        is_reasonable_question = True
    elif is_reasonable_question == 'False':
        is_reasonable_question = False
    else:
        is_reasonable_question = None

    grammatical_errors = []
    for idx in range(0, 4):
        if ans_data.pop('grammatical_errors_' + str(idx), None):
            grammatical_errors.append(idx)
    semantic_errors = []
    for idx in range(0, 4):
        if ans_data.pop('semantic_errors_' + str(idx), None):
            semantic_errors.append(idx)

    # ####################################

    ans_data_keys = ans_data.keys()
    # Note there is supposed to be ONLY ONE element in ans_data now !!! !!!
    if len(ans_data_keys) != 1:
        raise ValueError("The form has redudant data that are not allowed.")

    question_id = str(ans_data_keys[0].lstrip('question_answer_'))

    wiki_question = WikiQuestion.objects(id=question_id)[0]

    old_ans_retrieval = WikiQuestionAnswer.objects(assignmentId=assignmentId)
    if old_ans_retrieval:
        old_ans = old_ans_retrieval[0]
        try:
            old_ans.update(
                question=wiki_question,
                topic=wiki_question.topic,
                time=datetime.datetime.now(),

                answer=int(ans_data['question_answer_' + question_id]),
                correctness=check_answer_correctness(question_id, ans_data[
                    'question_answer_' + question_id]),

                hitId=hitId,
                assignmentId=assignmentId,
                workerId=workerId,
                turkSubmitTo=turkSubmitTo,

                topic_confidence=int(topic_confidence),
                question_confidence=int(question_confidence),
                comment=comment,
                comment_guess=comment_guess,
                is_reasonable_question=is_reasonable_question,
                grammatical_errors=grammatical_errors,
                semantic_errors=semantic_errors,

                submit_time_delta=int(submit_time_delta),
                topic_confidence_time_delta=int(topic_confidence_time_delta),
            )
        except Exception as e:
            print str(e)
            raise e
    else:
        wiki_ans = WikiQuestionAnswer(
            question=wiki_question,
            topic=wiki_question.topic,
            time=datetime.datetime.now(),

            answer=int(ans_data['question_answer_' + question_id]),
            correctness=check_answer_correctness(question_id, ans_data[
                'question_answer_' + question_id]),

            hitId=hitId,
            assignmentId=assignmentId,
            workerId=workerId,
            turkSubmitTo=turkSubmitTo,

            topic_confidence=int(topic_confidence),
            question_confidence=int(question_confidence),
            comment=comment,
            comment_guess=comment_guess,
            is_reasonable_question=is_reasonable_question,
            grammatical_errors=grammatical_errors,
            semantic_errors=semantic_errors,

            submit_time_delta=int(submit_time_delta),
            topic_confidence_time_delta=int(topic_confidence_time_delta),
        )
        try:
            wiki_ans.save()
        except NotUniqueError, e:
            print str(e)
            raise e
    return True


def answer_stats(answers):
    # ans/correct/tc/qc/GE/SE/guess/tt/st/comment
    if len(answers) == 0:
        return None
    stats = {}
    for key in answers[0]:
        if key in ['comment', 'comment_guess']:
            stats[key] = "\n".join([a[key] for a in answers if key in a])
        elif key in [
            'topic_confidence',
            'question_confidence',
            'topic_confidence_time_delta',
            'submit_time_delta'
        ]:
            li = [a[key] for a in answers if key in a]
            stats[key] = sum(li) / len(li)
        elif key in ['grammatical_errors', 'semantic_errors']:
            lili = [a[key] for a in answers if key in a]
            merged_li = []
            for li in lili:
                merged_li.extend(li)
            stats[key] = Counter(merged_li).most_common()
        else:
            stats[key] = Counter(
                [a[key] for a in answers if key in a]).most_common()

    return stats