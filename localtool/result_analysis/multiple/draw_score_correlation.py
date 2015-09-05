__author__ = 'moonkey'

import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
import sys
import numpy as np
from autoassess.answer_analysis import stats_linear_regression


def draw_scores(scores1, scores2):
    plt.figure(1)
    corr = pearsonr(scores1, scores2)
    print 'scores1', scores1
    print 'scores2', scores2
    print 'Pearson Correlation:', corr[0]
    print 'P-value:', corr[1]
    plt.style.use('ggplot')

    plt.scatter(scores1, scores2)
    lr = stats_linear_regression(scores1, scores2)
    predict_scores2 = lr.predict(np.array(scores1)[:, np.newaxis])
    plt.plot(scores1, predict_scores2)


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


def read_in_student_score(
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
    score_expert = read_in_student_score(
        score_file=open("./scores/student_score_v-1.0.txt", 'r'))
    score_generated_ques = read_in_student_score(
        score_file=open("./scores/student_score_v0.23.txt", 'r'))

    combined = combine_score_dicts_to_score_list(
        [score_expert, score_generated_ques])
    draw_scores(combined[0], combined[1])