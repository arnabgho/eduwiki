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

    # ##### Extract fields
    hitId = ans_data.pop('hitId')
    assignmentId = ans_data.pop('assignmentId')
    workerId = ans_data.pop('workerId')
    turkSubmitTo = ans_data.pop('turkSubmitTo')

    topic_confidence = ans_data.pop('topic_confidence', -1)
    question_confidence = ans_data.pop('question_confidence', -1)
    comment = ans_data.pop('comment', "")
    comment_guess = ans_data.pop('comment_guess', "")

    topic_confidence_time_delta = ans_data.pop('topic_confidence_time_delta', -1)
    submit_time_delta = ans_data.pop('submit_time_delta', -1)

    # ##### Temporary fields
    # rating_overhead = ans_data.pop("rating_overhead", None)
    # rating_confusion = ans_data.pop("rating_confusion", None)
    # comment_temp = ans_data.pop("comment_temp", None)
    #
    # if rating_confusion is not None or rating_confusion is not None or comment_temp is not None:
    #     comment = "Rating Overhead:" + str(rating_overhead) + "\nRating Confusion:" + str(
    #         rating_confusion) + "\nRating Comment:" + str(comment_temp) + "\nComment:" + str(comment)

    # ####################################
    ans_data_keys = ans_data.keys()
    # Note there is supposed to be ONLY ONE element in ans_data now !!! !!!
    if len(ans_data_keys) != 1:
        raise ValueError("The form has redudant data that are not allowed.")

    question_id = ans_data_keys[0]

    wiki_question = WikiQuestion.objects(id=question_id)[0]

    old_ans_retrieval = WikiQuestionAnswer.objects(assignmentId=assignmentId)
    if old_ans_retrieval:
        old_ans = old_ans_retrieval[0]
        try:
            old_ans.update(
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
                comment=comment,
                comment_guess=comment_guess,

                submit_time_delta=int(submit_time_delta),
                topic_confidence_time_delta=int(topic_confidence_time_delta),
            )
        except Exception, e:
            print str(e)
            raise e
    else:
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
            comment=comment,
            comment_guess=comment_guess,

            submit_time_delta=int(submit_time_delta),
            topic_confidence_time_delta=int(topic_confidence_time_delta),
        )
        try:
            wiki_ans.save()
        except NotUniqueError, e:
            print str(e)
    return True