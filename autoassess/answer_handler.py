__author__ = 'moonkey'

from models import *
import datetime

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

    hitId = ans_data.pop('hitId')
    assignmentId = ans_data.pop('assignmentId')
    workerId = ans_data.pop('workerId')
    turkSubmitTo = ans_data.pop('turkSubmitTo')

    topic_confidence = ans_data.pop('topic_confidence', -1)
    question_confidence = ans_data.pop('question_confidence', -1)
    comment = ans_data.pop('comment', "")

    for question_id in ans_data:
        wiki_question = WikiQuestion.objects(id=question_id)[0]
        wiki_ans = WikiQuestionAnswer(
            question=wiki_question,
            topic=wiki_question.topic,
            time=datetime.datetime.now(),

            answer=int(ans_data[question_id]),
            correctness=check_answer_correctness(question_id, ans_data[question_id]),

            hitId=hitId,
            assignmentId=assignmentId,
            workerId=workerId,
            turkSubmitTo=turkSubmitTo,

            topic_confidence=int(topic_confidence),
            question_confidence=int(question_confidence),
            comment=comment
        )
        wiki_ans.save()

