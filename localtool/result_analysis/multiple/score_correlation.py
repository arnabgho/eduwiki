__author__ = 'moonkey'

import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, kendalltau, gaussian_kde
import sys
import numpy as np
from autoassess.answer_analysis import stats_linear_regression
from collections import defaultdict
from sklearn import mixture

GAUSSIAN_KDE = 'gaussian_kde'
SINGLE_GAUSSIAN = 'gaussian_fit'


def scores_gaussian(
        m1, m2, bbox=(0, 1, 0, 1), fit_type=SINGLE_GAUSSIAN,
        filename='', fig_title=""):
    m1 = np.asarray(m1)
    m2 = np.asarray(m2)
    if bbox:
        x_min, x_max, y_min, y_max = bbox
    else:
        x_min = m1.min()
        x_max = m1.max()
        y_min = m2.min()
        y_max = m2.max()
    x_discrete, y_discrete = np.mgrid[x_min:x_max:100j, y_min:y_max:100j]
    grid_positions = np.vstack([x_discrete.ravel(), y_discrete.ravel()])
    values = np.vstack([m1, m2])

    if fit_type == GAUSSIAN_KDE:
        """KDE"""
        kernel = gaussian_kde(values)
        pdf_at_grid = np.reshape(kernel(grid_positions).T, x_discrete.shape)
    else:  # elif type == SINGLE_GAUSSIAN:
        """
        fit a Gaussian Mixture Model with one components
        """
        clf = mixture.GMM(n_components=1, covariance_type='full')
        clf.fit(values.T)

        log_prob, resp_ = clf.score_samples(grid_positions.T)
        pdf_at_grid = np.reshape(np.exp(log_prob), x_discrete.shape)

    # fig, ax = plt.subplots()

    plt.style.use('ggplot')
    plt.imshow(np.rot90(pdf_at_grid),
               cmap=plt.cm.gist_earth_r,
               extent=[x_min, x_max, y_min, y_max])
    plot_with_overlapping_weight(
        m1.tolist(), m2.tolist(), count_annotation=False)
    # ax.plot(m1, m2, 'k.', markersize=2)
    plt.xlim([x_min, x_max])
    plt.ylim([y_min, y_max])

    if fig_title:
        plt.title(fig_title)
    if not filename:
        plt.show()
    else:
        filename += '_' + fit_type + '.pdf'
        plt.savefig(filename, bbox_inches='tight')  # bbox_inches=0
    plt.close()
    return


def draw_scores(
        scores1, scores2, axis_range=(0.0, 1.05),
        overlap_weight=False, count_annotation=False,
        filename="", fig_title=""):
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
    if not fig_title:
        plt.title("Expert-Eduwiki Score Comparison")
    else:
        plt.title(fig_title + '%.4f' % pearson_corr[0])

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