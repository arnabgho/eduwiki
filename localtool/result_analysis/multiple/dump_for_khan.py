__author__ = 'moonkey'

from answer_io_util import *


def write_khan_record_list_to_file(
        record_list, quiz_name, quiz_version=None, n_samples=None):
    record_file_name = './response_data/' + quiz_name.replace(" ", "_")
    if quiz_version:
        record_file_name += "_v" + str(quiz_version)

    if n_samples:
        record_file_name += "_sample" + str(n_samples)

    record_file_name += '.response'
    with open(record_file_name, 'w') as outfile:
        csv_out = csv.writer(outfile)
        for row in record_list:
            csv_out.writerow(row)
        print "Finished dumping for", quiz_name, quiz_version


def dump_quiz_khan_format(quiz_name, version, n_samples=100):
    try:
        quiz = QuestionSet.objects(set_topic=quiz_name, version=version)[0]
        assert isinstance(quiz, QuestionSet)
    except Exception as e:
        print e
        print "No quiz retrieved for dumping"
        return False

    student_ans = read_student_answers_from_db(quiz)

    if not student_ans:
        print "No answers retrieved for", quiz.set_topic
        return []

    if len(student_ans) < n_samples:
        print 'Resampling with replacement:', n_samples
        student_ans = resample_students(student_ans, n_samples=n_samples)
    else:
        n_samples = None
    record_list = student_ans_dict_to_khan_record(student_ans)
    write_khan_record_list_to_file(record_list, quiz.set_topic,
                                   quiz_version=None,
                                   n_samples=n_samples)

    student_ans_of_v = separate_student_answers_by_version(student_ans)
    for v in student_ans_of_v:
        record_list_v = student_ans_dict_to_khan_record(student_ans_of_v[v])
        write_khan_record_list_to_file(record_list_v, quiz.set_topic,
                                       quiz_version=v,
                                       n_samples=n_samples)

    return record_list


def dump_all_khan_format(only_manual=True, n_samples=100):
    if only_manual:
        quizzes = QuestionSet.objects(version=-1.0)
    # quizzes = QuestionSet.objects()
    for quiz in quizzes:
        assert isinstance(quiz, QuestionSet)
        dump_quiz_khan_format(quiz_name=quiz.set_topic, version=quiz.version,
                              n_samples=n_samples)


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')

    quiz = QuestionSet.objects(
        set_topic="Customer satisfaction", version=-1.0)[0]
    student_ans = read_student_answers_from_db(quiz)
    # student_mtx = answer_dict_to_arrays(student_ans)
    # student_ans_of_v = separate_student_answers_by_version(student_ans)
    # for v in student_ans_of_v:
    # print "Version ", v
    # student_ans = student_ans_of_v[v]
    # for s in student_ans:
    # print s, student_ans[s]


    # The following code was written before the current code, and worked smoothly
    # for dumping into khan format
    # Uncomment if the current code does not work.

    #
    # def dump_quiz_khan_format(quiz_name, version, separate_questions_by_version=True):
    # """
    # Get the question answers into the Khan Academy format, so it can be
    # analyzed directly through 'guacamole'
    #
    # These columns are name, exercise, time_taken, and correct.
    # Reference: https://github.com/Khan/guacamole
    #     :param separate_questions_by_version: if True, then in one (MANUAL) quiz,
    #     the question generated (version>0) will be separated from expert questions
    #       (version<0)
    #     :return: the record list, the output will also be written to the file.
    #     """
    #
    #     try:
    #         quiz = QuestionSet.objects(set_topic=quiz_name, version=version)[0]
    #         assert isinstance(quiz, QuestionSet)
    #     except Exception as e:
    #         print e
    #         print "No quiz retrieved for dumping"
    #         return False
    #
    #     quiz_answers = QuizAnswers.objects(quiz=quiz)
    #
    #     record_list = []
    #     if separate_questions_by_version:
    #         version_separate_record_lists = {}
    #     for quiz_ans in quiz_answers:
    #         assert isinstance(quiz_ans, QuizAnswers)
    #
    #         # !!!NOTE!!!:: Only take quiz final answers, not directly retrieve
    #         # wiki_question_answer, which will contain intermediate answers
    #         final_answers = quiz_ans.quiz_final_answers
    #         for question_ans in final_answers:
    #             assert isinstance(question_ans, WikiQuestionAnswer)
    #
    #             worker_id = question_ans.workerId
    #             exercise = question_ans.question.topic
    #             time_taken = question_ans.submit_time_delta
    #             correct = question_ans.correctness
    #             record = (worker_id, exercise, time_taken, correct)
    #             if separate_questions_by_version:
    #                 qversion = question_ans.question.version
    #                 if qversion not in version_separate_record_lists:
    #                     version_separate_record_lists[qversion] = []
    #                 version_separate_record_lists[qversion].append(record)
    #
    #             record_list.append(record)
    #
    #     if not record_list:
    #         print "No record for", quiz_name, quiz.version
    #         return False
    #
    #     with open('./response_data/' + quiz_name.replace(" ", "_") + '.response',
    #               'w') as outfile:
    #         csv_out = csv.writer(outfile)
    #         for row in record_list:
    #             csv_out.writerow(row)
    #         print "Finished dumping for", quiz_name, quiz.version
    #
    #     if separate_questions_by_version:
    #         for qversion in version_separate_record_lists:
    #             with open('./response_data/' +
    #                       quiz_name.replace(" ", "_") +
    #                       "_v" + str(qversion) +
    #                       '.response', 'w') as outfile:
    #                 csv_out = csv.writer(outfile)
    #                 for row in version_separate_record_lists[qversion]:
    #                     csv_out.writerow(row)
    #                 print "Finished dumping for", quiz_name, quiz.version, qversion
    #
    #     return record_list
    #
    #
    # def dump_all_khan_format():
    #     quizzes = QuestionSet.objects()
    #     for quiz in quizzes:
    #         assert isinstance(quiz, QuestionSet)
    #         dump_quiz_khan_format(quiz_name=quiz.set_topic, version=quiz.version)