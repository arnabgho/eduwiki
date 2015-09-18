__author__ = 'moonkey'

from quiz_score_analysis import *
from answer_irt_analysis import *

SCORE_OLS = 'score_ols'
SCORE_KDE = 'score_kde'
IRT_SIGMOID = 'irt_sigmoid'
ABILITY_OLS = 'ability_ols'


def analysis_pipeline(
        quiz,
        steps=list([SCORE_OLS, IRT_SIGMOID, ABILITY_OLS]),
        write_output=True):
    if write_output:
        filename = "./pics/" + quiz.set_topic + '_v' + str(quiz.version)
    else:
        filename = ''

    """
    Step : quiz_score_analysis (correlation analysis)
    """
    if SCORE_OLS or SCORE_KDE in steps:
        question_stat, expert_scores, eduwiki_scores = quiz_correct_rate(quiz)

        assert len(expert_scores) == len(eduwiki_scores)
        print "Number of answers:", len(expert_scores), len(eduwiki_scores)

        # record the context into a txt file, also in draw_scores()
        if write_output:
            with open(filename + "_info.txt", 'w') as corr_file:
                corr_file.write(
                    "Num of quiz answers:" + str(len(expert_scores)) + '\n')

        combined = combine_score_dicts_to_score_list(
            [expert_scores, eduwiki_scores])

    if SCORE_OLS in steps:
        corr = draw_scores(
            combined[0], combined[1], axis_range=(0, 1.05), overlap_weight=True,
            count_annotation=False, filename=filename)

    """
    Step : kde with 2 scores as the 2 dimensions
    """
    if SCORE_KDE:
        scores_gaussian(
            combined[0], combined[1],
            # fit_type=SINGLE_GAUSSIAN,
            fit_type=GAUSSIAN_KDE,
            filename=filename)

    """
    Step : IRT analysis and plot the sigmoid curves for questions
    """
    student_quiz_ans = read_student_answers_from_db(quiz)
    if IRT_SIGMOID in steps:
        compare_quizzes_with_expert_quiz(
            student_quiz_ans, expert_verison=-1.0, filename=filename)

    # # correlation analysis of student ability?
    if ABILITY_OLS in steps:
        compare_separate_student_ability(
            student_quiz_ans, expert_verison=-1.0, filename=filename)

    if SCORE_OLS in steps:
        return corr
    else:
        return True


def corr_form(all_corrs):
    fieldnames = [
        'Quiz',
        'Pearson Correlation', 'P-value',
        'Spearman Correlation', 'P-value',
        'Kendall\'s tau Correlation', 'P-value']
    with open("./pics/all_score_correlations.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for quiz in all_corrs:
            corr = all_corrs[quiz]
            writer.writerow([
                quiz,
                '%.4f' % corr[0][0], '%.4f' % corr[0][1],
                '%.4f' % corr[1][0], '%.4f' % corr[1][1],
                '%.4f' % corr[2][0], '%.4f' % corr[2][1],
            ])


def analyze_all(all_in_one=False):
    quiz_topic_list = [
        "Earthquake Quiz",
        # "Customer satisfaction",
        # "Developmental psychology",
        # "Earthquake",
        # "Market structure",
        # "Metaphysics",
        # "Vietnam War",
        # "Stroke",
        # "Waste management",
        # "Cell (biology)",
        # "Elasticity (physics)",
    ]

    all_corrs = {}
    for quiz_topic in quiz_topic_list:
        quiz = QuestionSet.objects(
            set_topic=quiz_topic, version=-1.0)[0]
        corr = analysis_pipeline(
            quiz,
            steps=[
                SCORE_OLS,
                IRT_SIGMOID,
                SCORE_KDE,
            ],
            write_output=True
        )
        all_corrs[quiz_topic] = corr

    if all_in_one:
        corr_form(all_corrs)
    return True


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    analyze_all()