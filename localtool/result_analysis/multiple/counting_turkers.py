from __future__ import division
from quiz_score_analysis import *


def read_submit_time_from_db_by_student(quiz):
    quiz_answers = QuizAnswers.objects(quiz=quiz)

    student_time = {}

    for quiz_ans in quiz_answers:
        # Filter quiz answers that are not complete
        final_answers = quiz_ans.quiz_final_answers
        if len(final_answers) != len(quiz_ans.quiz.questions):
            continue
        workerId = quiz_ans.workerId

        for final_ans in final_answers:
            question = final_ans.question

            if workerId not in student_time:
                student_time[workerId] = {}
            student_time[workerId][question.topic] = final_ans.submit_time_delta

    return student_time


def read_text_length_from_db_by_student(quiz):
    quiz_answers = QuizAnswers.objects(quiz=quiz)

    student_text_length = {}

    for quiz_ans in quiz_answers:
        # Filter quiz answers that are not complete
        final_answers = quiz_ans.quiz_final_answers
        if len(final_answers) != len(quiz_ans.quiz.questions):
            continue
        workerId = quiz_ans.workerId
        for final_ans in final_answers:
            question = final_ans.question

            if workerId not in student_text_length:
                student_text_length[workerId] = {}
            assert len(final_ans.comment) >= 15
            if len(final_ans.comment) > 100:
                print final_ans.comment
            student_text_length[workerId][question.topic] = len(
                final_ans.comment)

    return student_text_length


def count_turks():
    all_turkers = []
    all_times = []
    all_text_lengths = []
    quiz_topic_list = [
        "Earthquake Quiz",
        "Vietnam War Quiz",
        "Customer satisfaction",
        "Developmental psychology",
        "Earthquake",
        "Market structure",
        "Metaphysics",
        "Vietnam War",
        "Stroke",
        "Waste management",
        "Cell (biology)",
        "Elasticity (physics)",
    ]

    # root_folder = './analysis_result/'
    # all_corrs = {}
    for quiz_topic in quiz_topic_list:
        quiz = QuestionSet.objects(
            set_topic=quiz_topic, version=-1.0)[0]
        student_times = \
            read_submit_time_from_db_by_student(quiz)
        # print student_times.keys()
        quiz_times = []
        for s in student_times:
            assert len(student_times[s].values()) == 20
            s_sum = sum(student_times[s].values())
            quiz_times.append(s_sum)
        # print quiz_times
        all_turkers += student_times.keys()
        all_times += quiz_times

        student_text_lengths = \
            read_text_length_from_db_by_student(quiz)

        quiz_text_lengths = []
        for s in student_text_lengths:
            assert len(student_text_lengths[s].values()) == 20
            print student_text_lengths[s].values()
            s_sum = sum(student_text_lengths[s].values())
            quiz_text_lengths.append(s_sum)
        all_text_lengths += quiz_text_lengths

    print 'Answers received:', len(all_turkers)
    print 'Workers involved:', len(set(all_turkers))
    print 'len(all_times)', len(all_times)
    avg_milliseconds = (sum(all_times) / (20 * len(all_times)))
    avg_seconds = avg_milliseconds / 1000
    print 'Times spent on each question (avg)', avg_seconds
    print 'len(all_text_lengths)', len(all_text_lengths)
    avg_text_length = sum(all_text_lengths) / (20 * len(all_text_lengths))
    print 'Text length on each question (avg)', avg_text_length


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    count_turks()