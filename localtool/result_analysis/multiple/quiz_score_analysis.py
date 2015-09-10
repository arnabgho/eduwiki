from __future__ import division

__author__ = 'moonkey'

from autoassess.models import *
from score_correlation import *
import math


def read_answers_from_db_by_question_and_student(quiz):
    quiz_answers = QuizAnswers.objects(quiz=quiz)

    # ###########
    # ### stat for each question
    # ###########
    question_ans = {}
    # ###########
    # ### stat for each student
    # ###########
    student_ans = {}
    question_version = {}

    for quiz_ans in quiz_answers:
        # quiz_ans = QuizAnswers()
        final_answers = quiz_ans.quiz_final_answers
        workerId = quiz_ans.workerId

        for final_ans in final_answers:
            question = final_ans.question

            if question.topic not in question_ans:
                question_ans[question.topic] = []
                question_version[question.topic] = question.version
            question_ans[question.topic].append(final_ans.correctness)

            if workerId not in student_ans:
                student_ans[workerId] = {}
            student_ans[workerId][question.topic] = final_ans.correctness

    return question_ans, student_ans, question_version


def quiz_correct_rate(quiz):
    question_ans, student_ans, question_version = \
        read_answers_from_db_by_question_and_student(quiz)

    question_correct_rate = {
        q: question_ans[q].count(True) / len(question_ans[q])
        for q in question_ans
    }

    manual_questions = [q for q in question_version if
                        question_version[q] < 0]
    automatic_questions = [q for q in question_version if
                           question_version[q] > 0]

    student_correct_rate_manual = {
        s: [student_ans[s][q] for q in student_ans[s] if q
            in manual_questions].count(True) / len(manual_questions)
        for s in student_ans
    }

    student_correct_rate_automatic = {
        s: [student_ans[s][q] for q in student_ans[s] if q
            in automatic_questions].count(True) / len(automatic_questions)
        for s in student_ans
    }

    return question_correct_rate, \
           student_correct_rate_manual, \
           student_correct_rate_automatic


def expert_fit_expert(quiz):
    question_ans, student_ans, question_version = \
        read_answers_from_db_by_question_and_student(quiz)

    expert_questions = [q for q in question_version if question_version[q] < 0]
    random.shuffle(expert_questions)
    first_half = expert_questions[:int(len(expert_questions) / 2)]
    second_half = expert_questions[int(len(expert_questions) / 2):]
    first_half_scores = {
        s: [student_ans[s][q] for q in student_ans[s] if q
            in first_half].count(True) / len(first_half)
        for s in student_ans
    }

    second_half_scores = {
        s: [student_ans[s][q] for q in student_ans[s] if q
            in second_half].count(True) / len(second_half)
        for s in student_ans
    }

    return first_half_scores, second_half_scores


def db_quiz_stats():
    answered_quizzes = QuizAnswers.objects().distinct('quiz')

    stats = []
    for quiz in answered_quizzes:
        stat = quiz_correct_rate(quiz)
        stats.append(stat)
    return stats


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    # stats = db_quiz_stats()
    # for stat in stats:
    # for p in stat:
    # print p

    quiz = QuestionSet.objects(
        set_topic="Customer satisfaction", version=-1.0)[0]
    question_stat, expert_scores, eduwiki_scores = quiz_correct_rate(quiz)

    print len(expert_scores), len(eduwiki_scores)

    combined = combine_score_dicts_to_score_list(
        [expert_scores, eduwiki_scores])
    corr = draw_scores(combined[0], combined[1])

    # # Separate expert questions to two groups, and
    # corrs = []
    # for idx in range(0, 50):
    #     first_scores, second_scores = expert_fit_expert(quiz)
    #     combined = combine_score_dicts_to_score_list(
    #         [first_scores, second_scores])
    #     corr = draw_scores(combined[0], combined[1])
    #     corrs.append(corr)
    # average_pearson_corr = np.mean([c[0] for c in corrs])
    # std_pearson_corr = np.std([c[0] for c in corrs])
    # average_p_value = np.mean([c[1] for c in corrs])
    # std_p_value = np.std(([c[1] for c in corrs]))
    # for c in corrs:
    #     print c
    # print 'avg pearson corr', average_pearson_corr, std_pearson_corr
    # print 'avg p value', average_p_value, std_p_value
