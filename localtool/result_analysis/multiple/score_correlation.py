__author__ = 'moonkey'

import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, kendalltau, gaussian_kde
import sys
import numpy as np
from autoassess.answer_analysis import stats_linear_regression
from collections import defaultdict


def scores_kde(m1, m2):
    xmin = m1.min()
    xmax = m1.max()
    ymin = m2.min()
    ymax = m2.max()
    X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([m1, m2])
    kernel = gaussian_kde(values)
    Z = np.reshape(kernel(positions).T, X.shape)
    fig, ax = plt.subplots()
    ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
              extent=[xmin, xmax, ymin, ymax])
    ax.plot(m1, m2, 'k.', markersize=2)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    plt.show()


def draw_scores(
        scores1, scores2, axis_range=(0.0, 1.05),
        overlap_weight=False, count_annotation=False,
        filename=""):
    plt.figure(1)
    pearson_corr = pearsonr(scores1, scores2)
    spearman_corr = spearmanr(scores1, scores2)
    kendalltau_corr = kendalltau(scores1, scores2)

    # print 'scores1', scores1
    # print 'scores2', scores2
    print 'Pearson Correlation:', pearson_corr[0]
    print 'P-value:', pearson_corr[1]
    print 'Spearman Correlation:', spearman_corr[0]
    print 'P-value:', spearman_corr[1]
    print 'Kendall\'s tau Correlation:', kendalltau_corr[0]
    print 'P-value:', kendalltau_corr[1]
    if filename:
        with open(filename + "_info.txt", 'a') as corr_file:
            corr_file.write("Pearson Corr:" + str(pearson_corr) + '\n')
            corr_file.write("Spearman Corr:" + str(spearman_corr) + '\n')
            corr_file.write("Kendall's tau Corr:" + str(kendalltau_corr) + '\n')

    plt.style.use('ggplot')
    if overlap_weight:
        plot_with_overlapping_weight(
            scores1, scores2, count_annotation=count_annotation)
    else:
        plt.scatter(scores1, scores2)

    lr = stats_linear_regression(scores1, scores2, filename + "_info.txt")
    predict_scores2 = lr.predict(np.array(scores1)[:, np.newaxis])
    plt.plot(scores1, predict_scores2, linewidth=4)

    plt.axis('equal')
    plt.xlim(axis_range)
    plt.ylim(axis_range)
    plt.xlabel('Expert Score')
    plt.ylabel('Eduwiki Score')
    plt.title("Expert-Eduwiki Score Comparison")

    if not filename:
        plt.show()
    else:
        filename += '_score_scatter.pdf'
        plt.savefig(filename, bbox_inches='tight')  # bbox_inches=0
    plt.close()
    return pearson_corr, spearman_corr, kendalltau_corr


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


def plot_with_overlapping_weight(x=[], y=[], count_annotation=False):
    """
    deal with the case where scatter points have overlapping
    :param x:
    :param y:
    :return:
    """
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
    if count_annotation:
        for x, y, label in zip(d_x, d_y, count_list):
            plt.annotate(
                label,
                xy=(x, y), xytext=(-10, -10),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='green', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))


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
    print >> sys.stderr, "Guacamole student ability estimation no longer used."
    # Following is for reading in the guacamole score output
    # score_expert = read_in_student_score_khan_format(
    # score_file=open("./scores/student_score_v-1.0.txt", 'r'))
    # score_generated_ques = read_in_student_score_khan_format(
    # score_file=open("./scores/student_score_v0.23.txt", 'r'))
    #
    # combined = combine_score_dicts_to_score_list(
    # [score_expert, score_generated_ques])
    # draw_scores(combined[0], combined[1])