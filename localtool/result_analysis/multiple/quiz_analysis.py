from __future__ import division

__author__ = 'moonkey'

from autoassess.models import *
from draw_score_correlation import *


def read_answers_from_db(quiz):
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


def quiz_stat(quiz):
    question_ans, student_ans, question_version = read_answers_from_db(quiz)

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


def db_quiz_stats():
    answered_quizzes = QuizAnswers.objects().distinct('quiz')

    stats = []
    for quiz in answered_quizzes:
        stat = quiz_stat(quiz)
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
    question_stat, expert_scores, eduwiki_scores = quiz_stat(quiz)

    combined = combine_score_dicts_to_score_list(
        [expert_scores, eduwiki_scores])
    draw_scores(combined[0], combined[1])