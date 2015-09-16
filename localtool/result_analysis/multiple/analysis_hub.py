__author__ = 'moonkey'

from quiz_score_analysis import *
from answer_irt_analysis import *


def analysis_pipeline(quiz):
    filename = "./pics/" + quiz.set_topic + '_v' + str(quiz.version)

    """
    Step : quiz_score_analysis (correlation analysis)
    """
    question_stat, expert_scores, eduwiki_scores = quiz_correct_rate(quiz)

    assert len(expert_scores) == len(eduwiki_scores)
    print "Number of answers:", len(expert_scores), len(eduwiki_scores)

    # record the context into a txt file, also in draw_scores()
    with open(filename + "_info.txt", 'w') as corr_file:
        corr_file.write("Num of quiz answers:" + str(len(expert_scores)) + '\n')

    combined = combine_score_dicts_to_score_list(
        [expert_scores, eduwiki_scores])

    corr = draw_scores(
        combined[0], combined[1], axis_range=(0, 1.05), overlap_weight=True,
        filename=filename)

    """
    Step : kde with 2 scores as the 2 dimensions
    """
    scores_kde(combined[0], combined[1])

    """
    Step : IRT analysis and plot the sigmoid curves for questions
    """
    student_quiz_ans = read_student_answers_from_db(quiz)
    compare_quizzes_with_expert_quiz(
        student_quiz_ans, expert_verison=-1.0, filename=filename)

    # # correlation analysis of student ability?
    compare_separate_student_ability(
        student_quiz_ans, expert_verison=-1.0, filename=filename)

    return corr


def analyze_all():
    quiz_topic_list = [
        "Customer satisfaction",
        # "Developmental psychology",
        # "Earthquake",
        # "Market structure",
        # "Metaphysics",
        # "Vietnam War",
        # "Stroke",
        # "Waste management"
    ]
    all_corrs = {}
    for quiz_topic in quiz_topic_list:
        quiz = QuestionSet.objects(
            set_topic=quiz_topic, version=-1.0)[0]
        corr = analysis_pipeline(quiz)
        all_corrs[quiz_topic] = corr

    return True


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    analyze_all()