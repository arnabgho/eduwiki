__author__ = 'moonkey'

from answer_io_util import *
from bayesian_irt import birt
from score_correlation import draw_scores


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

    # return a, b, theta
    return question_params


def plot_questions(questions, a, b, filename='', fig_title=''):
    question_params = {}
    for q_idx, q in enumerate(questions):
        question_params[q.topic] = {'a': a.trace().mean(0)[q_idx][0],
                                    'b': b.trace().mean(0)[q_idx]}
    birt.plot_sigmoid(question_params, filename, fig_title=fig_title)
    birt.plot_a_trace(a.trace(), filename)
    return question_params


def compare_separate_student_ability(
        student_quiz_ans, expert_verison=-1.0,
        filename='', fig_title=''):
    quiz_ans_by_v = separate_student_answers_by_version(student_quiz_ans)

    ans_mtx_version = {}
    students_version = {}
    questions_version = {}
    # fit data_with
    ans_mtx, students, questions = answer_dict_to_arrays(
        quiz_ans_by_v[expert_verison])
    ans_mtx_version[expert_verison] = ans_mtx
    students_version[expert_verison] = students
    questions_version[expert_verison] = questions

    a, b, theta = birt.bayesian_irt(ans_mtx)

    # if filename:
    # temp_filename = filename + '_irt_ability_' + str(expert_verison)
    # birt.plot_theta_trace(theta, filename=temp_filename)


    # # Fix theta, and fit for the other (non-expert) questions
    for v in quiz_ans_by_v:
        if v == expert_verison:
            continue
        ans_mtx_version[v], students_version[v], questions_version[v] = \
            answer_dict_to_arrays(quiz_ans_by_v[v])

        assert students_version[v] == students_version[expert_verison]
        a, b, theta2 = birt.bayesian_irt(ans_mtx_version[v])

        if filename:
            temp_filename = filename + '_student_ability_' + str(v)
        else:
            temp_filename = filename
        draw_scores(
            theta.trace().mean(0)[0], theta2.trace().mean(0)[0],
            axis_range=(-3, 3), overlap_weight=False,
            filename=temp_filename, fig_title=fig_title)
        # mean(0).shape=(1,40)


def compare_quizzes_with_expert_quiz(
        student_quiz_ans, expert_verison=-1.0, filename='', fig_title=''):
    quiz_ans_by_v = separate_student_answers_by_version(student_quiz_ans)

    ans_mtx_version = {}
    students_version = {}
    questions_version = {}
    # fit data_with
    ans_mtx, students, questions = answer_dict_to_arrays(
        quiz_ans_by_v[expert_verison])
    ans_mtx_version[expert_verison] = ans_mtx
    students_version[expert_verison] = students
    questions_version[expert_verison] = questions

    a, b, theta = birt.bayesian_irt(ans_mtx)

    ##################
    ##### Sigmoids
    ##################
    # if filename:
    #     temp_filename = filename.replace(' ', '_') + '_irt_ability_' \
    #                     + str(expert_verison).replace('.', '_')
    #     birt.plot_theta_trace(theta, filename=temp_filename)

    temp_filename = filename.replace(' ', '_') + '_expert' \
                    + str(expert_verison).replace('.', '_')
    question_params_expert = plot_questions(
        questions, a, b,
        filename=temp_filename,
        fig_title=fig_title  # + 'v:' + str(expert_verison)
    )

    # [DONE] A SPECIFIC TEST
    # test whether the estimation of the parameters for expert question is stable
    # with/without theta fixed
    # Result: there is some shift, but the main trends of the curves are
    # basically same for all of these. So it is the same for all the cases.
    # a, b, theta = birt.bayesian_irt(ans_mtx, theta.trace().mean(0))
    # plot_questions(questions, a, b)

    # # Fix theta, and fit for the other (non-expert) questions
    question_params = {}
    for v in quiz_ans_by_v:
        if v == expert_verison:
            continue
        ans_mtx_version[v], students_version[v], questions_version[v] = \
            answer_dict_to_arrays(quiz_ans_by_v[v])

        assert students_version[v] == students_version[expert_verison]
        a_v, b_v, theta_v = birt.bayesian_irt(
            ans_mtx_version[v], theta.trace().mean(0))
        temp_filename = filename.replace(' ', '_') + "_eduwiki" \
                        + str(v).replace('.', '_')
        question_params = plot_questions(
            questions_version[v], a_v, b_v,
            filename=temp_filename,
            fig_title=fig_title  # + 'v:' + str(v)
        )
    return question_params, question_params_expert


def test():
    quiz = QuestionSet.objects(
        set_topic="Customer satisfaction", version=-1.0)[0]
    student_quiz_ans = read_student_answers_from_db(quiz)
    # answer_irt(student_quiz_ans)
    compare_quizzes_with_expert_quiz(student_quiz_ans, expert_verison=-1.0)
    # compare_separate_student_ability(student_quiz_ans, expert_verison=-1.0)


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')

    test()