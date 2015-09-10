__author__ = 'moonkey'

import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
import sys
import numpy as np
from autoassess.answer_analysis import stats_linear_regression
from collections import defaultdict


def plot_with_overlapping_weight(x=[], y=[]):
    num = len(x)
    points = [(x[i], y[i]) for i in range(0, num)]
    point_counts = defaultdict(int)
    for p in points:
        point_counts[p] += 1

    distinct_points = point_counts.keys()
    d_x = [p[0] for p in distinct_points]
    d_y = [p[1] for p in distinct_points]

    count_list = [point_counts[p] for p in distinct_points]
    plt.scatter(d_x, d_y, s=[30 * c ^ 2 for c in count_list], marker='o')
    for x, y, label in zip(d_x, d_y, count_list):
        plt.annotate(
            label,
            xy=(x, y), xytext=(-20, -20),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='green', alpha=0.8),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))


def draw_scores(scores1, scores2):
    plt.figure(1)
    corr = pearsonr(scores1, scores2)
    print 'scores1', scores1
    print 'scores2', scores2
    print 'Pearson Correlation:', corr[0]
    print 'P-value:', corr[1]
    plt.style.use('ggplot')

    # plt.scatter(scores1, scores2)
    plot_with_overlapping_weight(scores1, scores2)

    lr = stats_linear_regression(scores1, scores2)
    predict_scores2 = lr.predict(np.array(scores1)[:, np.newaxis])
    plt.plot(scores1, predict_scores2)

    plt.axis('equal')
    plt.xlim(0, 1.05)
    plt.ylim(0, 1.05)
    plt.xlabel('Expert Score')
    plt.ylabel('Eduwiki Score')
    plt.title("Expert-Eduwiki Score Comparison")

    plt.show()

    return corr


def combine_score_dicts_to_score_list(score_dicts=[]):
    # find the subset that overlapps
    key_list = [s.keys() for s in score_dicts]
    overlap_keys = set.intersection(*map(set, key_list))

    combined_list = []  # [[]] * len(score_dicts)
    for k in overlap_keys:
        for idx, score_dict in enumerate(score_dicts):
            if len(combined_list) < idx + 1:
                combined_list.append([])
            combined_list[idx].append(score_dict[k])

    return combined_list


def read_in_student_score_khan_format(
        score_file):
    score_dict = {}
    for idx, line in enumerate(score_file):
        if idx == 0:
            print "Reading", line
            continue
        try:
            name, score = line.strip("\n").split(" ")
            if name in score_dict:
                print >> sys.stderr, name, "is already in score_dict"
            score_dict[name] = float(score)

        except ValueError:
            print "ERROR LINE: ", line

    return score_dict


if __name__ == "__main__":
    # Following is for reading in the guacamole score output
    score_expert = read_in_student_score_khan_format(
        score_file=open("./scores/student_score_v-1.0.txt", 'r'))
    score_generated_ques = read_in_student_score_khan_format(
        score_file=open("./scores/student_score_v0.23.txt", 'r'))

    combined = combine_score_dicts_to_score_list(
        [score_expert, score_generated_ques])
    draw_scores(combined[0], combined[1])