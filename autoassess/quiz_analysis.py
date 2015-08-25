from __future__ import division
__author__ = 'moonkey'

from models import *


def quiz_stat(quiz):
    quiz_answers = QuizAnswers.objects(quiz=quiz)

    # quiz = QuestionSet()
    quiz_questions = quiz.questions

    question_ans = {}
    for quiz_ans in quiz_answers:
        # quiz_ans = QuizAnswers()
        final_answers = quiz_ans.quiz_final_answers
        for final_ans in final_answers:
            if final_ans.question.topic not in question_ans:
                question_ans[final_ans.question.topic] = []
            question_ans[final_ans.question.topic].append(final_ans.correctness)

    ans_arries = []
    for q in quiz.questions:
        ans_arries.append(question_ans[q.topic])

    print len(ans_arries), len(ans_arries[0])
    correctness = [{
                       q: question_ans[q].count(True) / len(question_ans[q])
                   } for q in question_ans]
    for q in question_ans:
        print question_ans[q], q
    return correctness


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
    stats = db_quiz_stats()
    print stats