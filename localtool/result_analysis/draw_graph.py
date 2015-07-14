__author__ = 'moonkey'

import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

from bokeh.plotting import *
from bokeh.models import Range1d, HoverTool
from collections import OrderedDict

import numpy as np
from autoassess.answer_analysis import db_answer_stats, stats_linear_regression


def draw_stats():
    stats = db_answer_stats()
    tc = [s['topic_confidence'] for s in stats]
    qc = [s['question_confidence'] for s in stats]
    correct_rate = [s['correctness'] for s in stats]

    plt.style.use('ggplot')
    fig = plt.figure()

    subplt = plt.subplot(2, 2, 1)
    # subplt.title("Question Confidence v.s. Topic Confidence")
    subplt.set_xlabel("Topic Confidence")
    subplt.set_ylabel("Question Confidence")
    subplt.scatter(tc, qc)
    subplt.axis([0, 5, 0, 5])
    print "Question Confidence v.s. Topic Confidence"
    lr = stats_linear_regression(tc, qc)
    predict_qc = lr.predict(np.array(tc)[:, np.newaxis])
    subplt.plot(tc, predict_qc)
    # subplt.set_title("a: " + str(lr.coef_[0]) + ", b:" + str(lr.intercept_))

    subplt = fig.add_subplot(2, 2, 2)
    # subplt.title("Correct Rate v.s. Topic Confidence")
    subplt.set_xlabel("Topic Confidence")
    subplt.set_ylabel("Correct Rate")
    subplt.axis([0, 5, 0, 1])
    subplt.scatter(tc, correct_rate)
    print "Correct Rate v.s. Topic Confidence"
    lr = stats_linear_regression(tc, correct_rate)
    predict_cr = lr.predict(np.array(tc)[:, np.newaxis])
    subplt.plot(tc, predict_cr)
    # subplt.set_title("a: " + str(lr.coef_[0]) + ", b:" + str(lr.intercept_))

    subplt = fig.add_subplot(2, 2, 3)
    # subplt.title("Correct Rate v.s. Question Confidence")
    subplt.set_xlabel("Question Confidence")
    subplt.set_ylabel("Correct Rate")
    subplt.axis([0, 5, 0, 1])
    subplt.scatter(qc, correct_rate)
    print "Correct Rate v.s. Question Confidence"
    lr = stats_linear_regression(qc, correct_rate)
    predict_cr = lr.predict(np.array(qc)[:, np.newaxis])
    subplt.plot(qc, predict_cr)
    # subplt.set_title("a: " + str(lr.coef_[0]) + ", b:" + str(lr.intercept_))

    subplt = fig.add_subplot(224, projection='3d')
    subplt.scatter(tc, qc, correct_rate)
    # subplt.axis([0, 5, 0, 5, 0, 1])

    plt.show()


def html_stats():
    stats = db_answer_stats()
    tc = [s['topic_confidence'] for s in stats]
    qc = [s['question_confidence'] for s in stats]
    correct_rate = [s['correctness'] for s in stats]
    topics = [s['topic'] for s in stats]

    output_file("answer_stats.html", title="Eduwiki Question Answer Plot")
    TOOLS = "crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"

    def draw2d(x, y, label, x_range, y_range, title='plot'):
        p = figure(title=title, tools=TOOLS, x_range=x_range, y_range=y_range)
        source = ColumnDataSource(
            data=dict(
                x=x,
                y=y,
                label=label
            ))
        p.circle('x', 'y', fill_alpha=0.2, size=10, source=source)
        hover = p.select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("(xx,yy)", "(@x, @y)"),
            ("label", "@label"),
        ])
        lr = stats_linear_regression(x, y)
        predicted_y = lr.predict(np.array(x)[:, np.newaxis])
        p.line(x, predicted_y, alpha=0.5, line_width=4, color='red')
        return p

    p1 = draw2d(tc, qc, topics, [0, 5], [0, 5],
                title="Question Confidence v.s. Topic Confidence")
    p2 = draw2d(correct_rate, tc, topics, [0, 1], [0, 5],
                title="Correct Rate v.s. Topic Confidence")
    p3 = draw2d(correct_rate, qc, topics, [0, 1], [0, 5],
                title="Correct Rate v.s. Question Confidence")
    show(VBox(p3, p2, p1))


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    draw_stats()
    # html_stats()