from __future__ import division

__author__ = 'moonkey'

from collections import Counter
from models import *
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
import numpy as np
import statsmodels.api as sm


def answer_stat(answers):
    """
    show the following fields when viewing answered questions
    :param answers:
    :return:
    """
    # ans/correct/tc/qc/GE/SE/guess/tt/st/comment
    if len(answers) == 0:
        return None
    stats = {}
    for key in answers[0]:
        if key == 'topic':
            stats[key] = Counter([a[key] for a in answers if key in a])
            if len(stats[key]) == 1:
                stats[key] = answers[0][key]
        elif key in ['comment', 'comment_guess']:
            stats[key] = "<br>".join([a[key] for a in answers if key in a])
        elif key in [
            'topic_confidence',
            'question_confidence',
            'topic_confidence_time_delta',
            'submit_time_delta'
        ]:
            li = [a[key] for a in answers if key in a]
            stats[key] = 0
            if len(li) > 0:
                stats[key] = sum(li) / len(li)
        elif key == 'correctness':
            li = [a[key] for a in answers if key in a]
            stats[key] = li.count(True) / len(li)
        elif key in ['grammatical_errors', 'semantic_errors']:
            lili = [a[key] for a in answers if key in a]
            merged_li = []
            for li in lili:
                merged_li.extend(li)
            stats[key] = Counter(merged_li).most_common()
        elif key in ['choice_order']:
            stats[key] = None
        else:
            stats[key] = Counter(
                [a[key] for a in answers if key in a]).most_common()

    return stats


def db_answer_stats():
    """
    wrapper for answer_stat()
    :return:
    """
    answered_questions = WikiQuestionAnswer.objects().distinct('question')
    stats = []
    for question in answered_questions:
        answers = WikiQuestionAnswer.objects(question=question)
        stat = answer_stat(answers)
        stats.append(stat)
    return stats


def stats_linear_regression(x, y):
    sm_fit = sm.OLS(y, sm.add_constant(x)).fit()
    print sm_fit.summary()

    lr = LinearRegression()
    lr.fit(np.array(x)[:, np.newaxis], np.array(y))
    return lr


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    stats = db_answer_stats()
    print stats