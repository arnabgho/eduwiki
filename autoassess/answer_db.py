from __future__ import division

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

    # ######## FOR THE WHOLE QUIZ
    topic_confidence = ans_data.pop('topic_confidence', -1)
    topic_confidence_time_delta = ans_data.pop(
        'topic_confidence_time_delta', -1)
    comment = ans_data.pop('comment', "")
    submit_time_delta = ans_data.pop('submit_time_delta', -1)


    # #### question specific
    question_confidence = ans_data.pop('question_confidence', -1)
    comment_guess = ans_data.pop('comment_guess', "")

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

    question_id = ans_data_keys[0][len('question_answer_'):]
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


def save_answers(ans_data):
    if not ans_data:
        return

    # ##### Extract fields
    hitId = ans_data.pop('hitId')
    assignmentId = ans_data.pop('assignmentId')
    workerId = ans_data.pop('workerId')
    turkSubmitTo = ans_data.pop('turkSubmitTo')


    # ######## FOR THE WHOLE QUIZ
    # topic_confidence = ans_data.pop('topic_confidence', -1)
    # topic_confidence_time_delta = ans_data.pop(
    #     'topic_confidence_time_delta', -1)
    comment = ans_data.pop('comment', "")
    submit_time_delta = ans_data.pop('submit_time_delta', -1)

    # TODO:: check validity
    quiz_id = ans_data.pop('quiz_id', '')
    # just use the submit_time_delta??
    # quiz_time_delta = ans_data.pop('quiz_time_delta', 0)
    # is the order reflected in the form element order??
    # question_order = ans_data.pop('question_order', None)

    quiz = QuestionSet.objects(id=quiz_id)[0]

    quiz_answers = QuizAnswers(
        quiz=quiz,
        workerId=workerId,
        assignmentId=assignmentId,

        quiz_submit_time=datetime.datetime.now(),
        quiz_time_delta=int(submit_time_delta),
        comment=comment
    )
    quiz_final_answers = []

    # ## All the left keys are question specific keys
    ans_data_keys = ans_data.keys()

    # ## get all the questions ids that are with an answer
    question_ids = [k[len("question_answer_"):] for k in ans_data_keys if
                    k.startswith("question_answer_")]

    for question_id in question_ids:

        wiki_question = WikiQuestion.objects(id=question_id)[0]

        # # in fact all the question answers should be able to be retrieved
        old_ans_retrieval = WikiQuestionAnswer.objects(
            question=wiki_question,
            assignmentId=assignmentId,
            workerId=workerId,
            answer=int(ans_data['question_answer_' + question_id]),
        )

        if old_ans_retrieval:
            wiki_ans = old_ans_retrieval[0]
        else:
            wiki_ans = WikiQuestionAnswer(
                question=wiki_question,
                topic=wiki_question.topic,
                time=datetime.datetime.now(),

                answer=int(ans_data['question_answer_' + question_id]),
                correctness=check_answer_correctness(
                    question_id, ans_data['question_answer_' + question_id]),

                hitId=hitId,
                assignmentId=assignmentId,
                workerId=workerId,
                turkSubmitTo=turkSubmitTo,

                submit_time_delta=int(submit_time_delta),

            )

            wiki_ans.save()
            # ##  SKIP for now: get other attributes for each question,
            # like confidence, time
        quiz_final_answers.append(wiki_ans)

    quiz_answers['quiz_final_answers'] = quiz_final_answers

    #TODO:: question_order

    quiz_answers.save()

    return True


def save_or_update_question_answer():
    #TODO:: quiz_answer_procedure
    pass





















