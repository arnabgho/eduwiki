__author__ = 'moonkey'

from quiz_score_analysis import *
from answer_irt_analysis import *
import numpy as np

SCORE_OLS = 'score_ols'
SCORE_GAUSSIAN = 'score_gaussian'
IRT_SIGMOID = 'irt_sigmoid'
ABILITY_OLS = 'ability_ols'


def analysis_pipeline(
        quiz,
        steps=list([SCORE_OLS, IRT_SIGMOID, ABILITY_OLS]),
        write_output=True,
        root_folder='./analysis_result/'):
    if write_output:
        filename = root_folder + quiz.set_topic.replace(' ', '_') + \
                   '_v' + str(quiz.version).replace('.', '_')
    else:
        filename = ''

    fig_title = quiz.set_topic.replace('Quiz', '[Expert-Expert2]')
    corr = None
    """
    Step : quiz_score_analysis (correlation analysis)
    """
    if SCORE_OLS in steps or SCORE_GAUSSIAN in steps:
        question_stat, expert_scores, eduwiki_scores = quiz_correct_rate(quiz)

        assert len(expert_scores) == len(eduwiki_scores)
        print "Number of answers:", len(expert_scores), len(eduwiki_scores)

        # record the context into a txt file, also in draw_scores()
        if write_output and SCORE_OLS in steps:
            with open(filename + "_info.txt", 'w') as corr_file:
                corr_file.write(
                    "Num of quiz answers:" + str(len(expert_scores)) + '\n')

        combined = combine_score_dicts_to_score_list(
            [expert_scores, eduwiki_scores])

    if SCORE_OLS in steps:
        corr = draw_scores(
            combined[0], combined[1],
            axis_range=[0.0, 1.0], overlap_weight=True,
            count_annotation=False, filename=filename, fig_title=fig_title)
        fig_title += ' (Corr: %.4f)' % corr[0][0]

    """
    Step : kde with 2 scores as the 2 dimensions
    """
    if SCORE_GAUSSIAN in steps:
        scores_gaussian(
            combined[0], combined[1],
            fit_type=SINGLE_GAUSSIAN,
            # fit_type=GAUSSIAN_KDE,
            filename=filename,
            fig_title=fig_title)

    """
    Step : IRT analysis and plot the sigmoid curves for questions
    """
    student_quiz_ans = read_student_answers_from_db(quiz)
    question_params = {}
    question_params_expert = {}
    if IRT_SIGMOID in steps:
        question_params, question_params_expert \
            = compare_quizzes_with_expert_quiz(
            student_quiz_ans, expert_verison=-1.0,
            filename=filename, fig_title=fig_title)

    # # correlation analysis of student ability?
    if ABILITY_OLS in steps:
        compare_separate_student_ability(
            student_quiz_ans, expert_verison=-1.0,
            filename=filename, fig_title=fig_title)

    if question_params:
        return question_params, question_params_expert
    if corr:
        return corr
    else:
        return True


def corr_form(all_corrs, root_folder='./analysis_result/'):
    # rank all_corrs
    quiz_names = all_corrs.keys()
    sorted_quiz_names = sorted(
        quiz_names, key=lambda x: all_corrs[x][0][0], reverse=True)

    fieldnames = [
        'Quiz',
        'Pearson Correlation',
        # 'P-value',
        # 'participants',
        # 'Spearman Correlation', 'P-value',
        # 'Kendall\'s tau Correlation', 'P-value'
    ]
    with open(root_folder + "all_score_correlations.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for quiz in sorted_quiz_names:
            corr = all_corrs[quiz]
            postfix = ""
            if corr[0][1] < 0.01:
                postfix = '**'
            elif corr[0][1] < 0.05:
                postfix = '*'

            writer.writerow([
                quiz.replace("Quiz", "[Expert-Expert2]"),
                '%.4f' % corr[0][0] + postfix,
                # '%.4f' % corr[0][1],
                # '%d' % corr[1],
                # '%.4f' % corr[1][0], '%.4f' % corr[1][1],
                # '%.4f' % corr[2][0], '%.4f' % corr[2][1],
            ])


def irt_form(all_irts, root_folder='./analysis_result/', expert=False):
    quiz_names = all_irts.keys()
    # calculate average 'a's
    alphas_stat = {}
    for q in quiz_names:
        print "Question Topics:", all_irts[q].keys()
        q_a_list = [all_irts[q][ques]['a'] for ques in all_irts[q]]
        q_a_avg = float(sum(q_a_list)) / float(len(q_a_list))
        q_a_median = np.median(q_a_list)
        q_a_positive_ratio = float(sum([a > 0 for a in q_a_list])) / float(
            len(q_a_list))
        q_a_ratio2 = float(sum([a > 0.5 for a in q_a_list])) / float(
            len(q_a_list))
        alphas_stat[q] = (q_a_avg, q_a_median, q_a_positive_ratio, q_a_ratio2)

    sorted_quiz_names = sorted(
        quiz_names, key=lambda x: alphas_stat[x], reverse=True)

    fieldnames = [
        'Quiz',
        'Average Discrimination',
        # 'Median Discrimination',
        # '# Discrimination > 0',
        # '# Discrimination > 0.5',
    ]
    filename = root_folder + "all_irt_discriminations.csv"
    if expert:
        filename = root_folder + "all_irt_discriminations_expert.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for quiz in sorted_quiz_names:
            a_stat = alphas_stat[quiz]
            writer.writerow([
                quiz.replace("Quiz", "[Expert-Expert2]"),
                '%.4f' % a_stat[0],
                # '%.4f' % a_stat[1],
                # '%.4f' % a_stat[2],
                # '%.4f' % a_stat[3],
            ])


def analyze_all(all_in_one=False):
    quiz_topic_list = [
        # "Earthquake Quiz",
        # "Vietnam War Quiz",
        "Customer satisfaction",
        # "Developmental psychology",
        # "Earthquake",
        # "Market structure",
        # "Metaphysics",
        # "Vietnam War",
        # "Stroke",
        # "Waste management",
        # "Cell (biology)",
        "Elasticity (physics)",
    ]
    steps = [
        # SCORE_OLS,
        IRT_SIGMOID,
        # SCORE_GAUSSIAN,
    ]
    root_folder = './analysis_result/'
    all_results = {}
    all_results_expert = {}
    for quiz_topic in quiz_topic_list:
        quiz = QuestionSet.objects(
            set_topic=quiz_topic, version=-1.0)[0]
        res = analysis_pipeline(
            quiz,
            steps=steps,
            write_output=True,
            root_folder=root_folder
        )
        if IRT_SIGMOID in steps:
            all_results[quiz_topic] = res[0]
            all_results_expert[quiz_topic] = res[1]
        else:
            all_results[quiz_topic] = res

    try:
        if IRT_SIGMOID in steps and all_in_one:
            irt_form(all_results, root_folder=root_folder)
            irt_form(all_results_expert, root_folder=root_folder, expert=True)
        return True
    except:
        pass

    if SCORE_OLS in steps and all_in_one:
        corr_form(all_results, root_folder=root_folder)
    return True


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    analyze_all(all_in_one=True)