__author__ = 'moonkey'

from answer_io_util import *
from bayesian_irt import birt


def answer_irt(student_quiz_ans):
    ans_mtx, students, questions = answer_dict_to_arrays(student_quiz_ans)
    a, b, theta = birt.bayesian_irt(ans_mtx)
    birt.plot_theta_trace(theta)
    #
    question_params = {}
    for q_idx, q in enumerate(questions):
        question_params[q.topic] = {
            'a': a.trace.mean(0)[q_idx][0],
            'b': b.trace.mean(0)[q_idx]
        }
    birt.plot_sigmoid(question_params)

    return a, b, theta


def compare_quiz(student_quiz_ans, ground_truth_verison=-1.0):
    quiz_ans_by_v = separate_student_answers_by_version(student_quiz_ans)

    ans_mtx_version = {}
    students_version = {}
    questions_version = {}
    # fit data_with
    ans_mtx, students, questions = answer_dict_to_arrays(
        quiz_ans_by_v[ground_truth_verison])
    ans_mtx_version[ground_truth_verison] = ans_mtx
    students_version[ground_truth_verison] = students
    questions_version[ground_truth_verison] = questions

    def plot_questions(questions, a, b):
        question_params = {}
        for q_idx, q in enumerate(questions):
            question_params[q.topic] = {'a': a.trace().mean(0)[q_idx][0],
                                        'b': b.trace().mean(0)[q_idx]}
        birt.plot_sigmoid(question_params)

    a, b, theta = birt.bayesian_irt(ans_mtx)

    # plot_questions(questions, a, b)
    birt.plot_theta_trace(theta)


    # test whether the estimation of the parameters for expert question is stable
    # with/without theta fixed
    # Result: there is some shift, but the main trends of the curves are
    # basically same for all of these. So it is the same for all the cases.
    # a, b, theta = birt.bayesian_irt(ans_mtx, theta.trace().mean(0))
    # plot_questions(questions, a, b)

    # # Fix theta, and fit for the other (non-expert) questions
    # for v in quiz_ans_by_v:
    #     if v == ground_truth_verison:
    #         continue
    #     ans_mtx_version[v], students_version[v], questions_version[v] = \
    #         answer_dict_to_arrays(quiz_ans_by_v[v])
    #
    #     a, b, theta = birt.bayesian_irt(
    #         ans_mtx_version[v], theta.trace().mean(0))
    #     plot_questions(questions_version[v], a, b)


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')

    quiz = QuestionSet.objects(
        set_topic="Customer satisfaction", version=-1.0)[0]
    student_quiz_ans = read_student_answers_from_db(quiz)
    # answer_irt(student_quiz_ans)
    compare_quiz(student_quiz_ans, ground_truth_verison=-1.0)
