from __future__ import division
__author__ = 'moonkey'

import matplotlib.pyplot as plt
from autoassess.answer_analysis import db_answer_stats


def draw_stats():
    stats = db_answer_stats()
    tc = [s['topic_confidence'] for s in stats]
    qc = [s['question_confidence'] for s in stats]
    correct = [s['correctness'] for s in stats]

    plt.plot(tc, qc, 'o')
    plt.show()


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    draw_stats()