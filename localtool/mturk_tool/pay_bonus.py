from __future__ import division

__author__ = 'moonkey'

from botowrapper import connect_mturk, get_bonus_payments
from boto.mturk.price import Price
from autoassess.models import *
from collections import OrderedDict


def pay_bonus(budget_with_amazon_fee=1000):
    # Read in data
    mtc = connect_mturk(sandbox=False)
    mix_quizzes = QuestionSet.objects(version__lte=0.0)
    mix_quizzes = list(mix_quizzes)  # [q for q in mix_quizzes]

    answers_for_quiz = {}
    for quiz in mix_quizzes:
        stats = QuizAnswers.objects(
            quiz=quiz, workerId__exists=True, assignmentId__exists=True)

        stats = [
            a for a in stats
            if len(a.quiz_final_answers) > 0 and
            'sandbox' not in a.quiz_final_answers[0].turkSubmitTo]
        answers_for_quiz[quiz] = stats

    # calculate scores for each quiz answer, get stats for each quiz
    # mean/variance/
    stats_for_quiz = {}
    for quiz in answers_for_quiz:
        question_num = len(quiz.questions)
        if question_num > 0:
            quiz_correct_answer = {}
            for question in quiz.questions:
                quiz_correct_answer[question] = question.correct_answer
        else:
            assert (question_num > 0)
            quiz_correct_answer = {}
            question_num = len(quiz.related_topics) + 1
        stats_for_quiz[quiz] = OrderedDict()

        stats = answers_for_quiz[quiz]
        for student_answer in stats:
            student_score = quiz_answer_score(student_answer,
                                              quiz_correct_answer)
            stats_for_quiz[quiz][student_answer.assignmentId] = {
                'score': student_score, 'bonus': 0,
                'workerId': student_answer.workerId}
        stats_for_quiz[quiz] = OrderedDict(
            sorted(stats_for_quiz[quiz].iteritems(),
                   key=lambda k: k[1]['score'],
                   reverse=True))
        # print stats_for_quiz[quiz]

    # Calculate money portion of each person
    budget = int(budget_with_amazon_fee / 1.4)
    num_answers_per_quiz = [len(stats_for_quiz[q]) for q in stats_for_quiz]
    all_answer_num = sum(num_answers_per_quiz)
    for quiz in stats_for_quiz:
        quiz_budget = budget / all_answer_num * len(stats_for_quiz[quiz])

        left_budget = quiz_budget
        num_answers = len(stats_for_quiz[quiz])
        stats = stats_for_quiz[quiz]
        min_bonus_score = stats.items()[max(
            0, int(0.4 * num_answers - 1))][1]['score']
        # distribute 1$
        for a in stats:
            if left_budget < 1:
                break
            if stats[a]['score'] >= min_bonus_score:
                stats[a]['bonus'] += 1
                left_budget -= 1
            else:
                break

        current_rewarded_score = stats.items()[0][1]['score']
        while left_budget > 1:
            for a in stats:
                if left_budget < 1:
                    break
                if stats[a]['score'] >= current_rewarded_score:
                    if stats[a]['bonus'] < 4:
                        stats[a]['bonus'] += 1
                        left_budget -= 1
                else:
                    current_rewarded_score = stats[a]['score']
                    break
            # find the next score threshold
            if left_budget < 1:
                break

    # TODO:: Test in sandbox first
    # (1) Get bonus already granted
    # (2) Actually pay them
    sum_bouns = 0
    sum_paid = 0
    for quiz in stats_for_quiz:
        print quiz.set_topic
        stats = stats_for_quiz[quiz]
        for a in stats:
            # hack for an assignment that does not exist
            if a == '36WLNQG78ZAOX7BPH0ZJD7N53XGBEM':
                continue
            bonus_payment = get_bonus_payments(mtc, assignment_id=a)
            if bonus_payment:
                assert (len(bonus_payment) == 1)
                assert (bonus_payment[0].currency_code == 'USD')
                bonus_paid = bonus_payment[0].amount
                # print 'Before Paid:', bonus_paid
            else:
                bonus_paid = 0

            bonu_to_pay = stats[a]['bonus'] - bonus_paid
            if stats[a]['workerId'] == 'A5EU1AQJNC7F2':
                print a, stats[a], bonu_to_pay
            sum_bouns += stats[a]['bonus']
            sum_paid += bonu_to_pay
            # if bonu_to_pay > 0:
            #     mtc.grant_bonus(stats[a]['workerId'], a, Price(bonu_to_pay),
            #                     'Thanks for your participation in our HIT.')
            # break
        # break
    print sum_bouns, sum_paid, sum_paid * 1.4


def quiz_answer_score(quiz_answer, correct_answers):
    score = 0
    for ans in quiz_answer.quiz_final_answers:
        if ans.answer == correct_answers[ans.question]:
            score += 1
    return score


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db')
    pay_bonus()