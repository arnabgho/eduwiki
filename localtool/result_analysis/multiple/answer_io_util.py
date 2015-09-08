__author__ = 'moonkey'

from autoassess.models import *
import csv
from score_resampling import resample_students
import numpy as np


def read_student_answers_from_db(quiz):
    quiz_answers = QuizAnswers.objects(quiz=quiz)

    # ###########
    # ### stat for each student
    # ###########
    student_quiz_answers = {}

    for quiz_ans in quiz_answers:
        final_answers = quiz_ans.quiz_final_answers
        workerId = quiz_ans.workerId

        for final_ans in final_answers:
            if workerId not in student_quiz_answers:
                student_quiz_answers[workerId] = []
            student_quiz_answers[workerId].append(final_ans)
    return student_quiz_answers


def separate_student_answers_by_version(student_quiz_answers):
    student_ans_of_version = {}
    for workerId in student_quiz_answers:
        for s_quiz_ans in student_quiz_answers[workerId]:
            version = s_quiz_ans.question.version

            if version not in student_ans_of_version:
                student_ans_of_version[version] = {}

            if workerId not in student_ans_of_version[version]:
                student_ans_of_version[version][workerId] = []

            student_ans_of_version[version][workerId].append(s_quiz_ans)

    return student_ans_of_version


def answer_dict_to_arrays(student_quiz_answers):
    """
    For IRT analysis and other tasks.
    :param student_quiz_answers: format from read_student_answers_from_db()
    :return: a numpy ndarray and the corresponding student/question labels
    """
    students = [s for s in student_quiz_answers]
    num_students = len(student_quiz_answers)

    first_student = student_quiz_answers.keys()[0]
    questions = [ans.question for ans in student_quiz_answers[first_student]]
    num_questions = len(questions)

    ans_mtx = np.zeros((num_questions, num_students))

    question_idx = {q: idx for idx, q in enumerate(questions)}
    for s_idx, s in enumerate(student_quiz_answers):
        s_answers = student_quiz_answers[s]
        assert len(s_answers) == num_questions
        for s_q_ans in s_answers:
            q_idx = question_idx[s_q_ans.question]
            ans_mtx[q_idx][s_idx] = float(s_q_ans.correctness)

    return ans_mtx, students, questions


def student_ans_dict_to_khan_record(student_quiz_answers):
    record_list = []
    for workerId in student_quiz_answers:
        for sq_ans in student_quiz_answers[workerId]:
            # Note workerId does not match the sq_ans.workerId
            # if this is from bootstrap sampling with changed names
            exercise = sq_ans.question.topic
            time_taken = sq_ans.submit_time_delta
            correct = sq_ans.correctness

            record = (workerId, exercise, time_taken, correct)

            record_list.append(record)

    if not record_list:
        print "No record !!!"
        return False
    return record_list



if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')

    quiz = QuestionSet.objects(
        set_topic="Customer satisfaction", version=-1.0)[0]
    student_ans = read_student_answers_from_db(quiz)
    ans_mtx, students, questions = answer_dict_to_arrays(student_ans)
    print len(questions), [q.topic for q in questions]
    print len(students), students