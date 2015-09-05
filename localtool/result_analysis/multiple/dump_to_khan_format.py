__author__ = 'moonkey'

from autoassess.models import *
import csv


def dump_quiz(quiz_name, version, separate_questions_by_version=True):
    """
    Get the question answers into the Khan Academy format, so it can be
    analyzed directly through 'guacamole'

    These columns are name, exercise, time_taken, and correct.
    Reference: https://github.com/Khan/guacamole
    :param separate_questions_by_version: if True, then in one (MANUAL) quiz,
    the question generated (version>0) will be separated from expert questions
      (version<0)
    :return: the record list, the output will also be written to the file.
    """

    try:
        quiz = QuestionSet.objects(set_topic=quiz_name, version=version)[0]
        assert isinstance(quiz, QuestionSet)
    except Exception as e:
        print e
        print "No quiz retrieved for dumping"
        return False

    quiz_answers = QuizAnswers.objects(quiz=quiz)

    record_list = []
    if separate_questions_by_version:
        version_separate_record_lists = {}
    for quiz_ans in quiz_answers:
        assert isinstance(quiz_ans, QuizAnswers)

        # !!!NOTE!!!:: Only take quiz final answers, not directly retrieve
        # wiki_question_answer, which will contain intermediate answers
        final_answers = quiz_ans.quiz_final_answers
        for question_ans in final_answers:
            assert isinstance(question_ans, WikiQuestionAnswer)

            worker_id = question_ans.workerId
            exercise = question_ans.question.topic
            time_taken = question_ans.submit_time_delta
            correct = question_ans.correctness
            record = (worker_id, exercise, time_taken, correct)
            if separate_questions_by_version:
                qversion = question_ans.question.version
                if qversion not in version_separate_record_lists:
                    version_separate_record_lists[qversion] = []
                version_separate_record_lists[qversion].append(record)

            record_list.append(record)

    if not record_list:
        print "No record for", quiz_name, quiz.version
        return False

    with open('./response_data/' + quiz_name.replace(" ", "_") + '.response',
              'w') as outfile:
        csv_out = csv.writer(outfile)
        for row in record_list:
            csv_out.writerow(row)
        print "Finished dumping for", quiz_name, quiz.version

    if separate_questions_by_version:
        for qversion in version_separate_record_lists:
            with open('./response_data/' +
                      quiz_name.replace(" ", "_") +
                      "_v" + str(qversion) +
                      '.response', 'w') as outfile:
                csv_out = csv.writer(outfile)
                for row in version_separate_record_lists[qversion]:
                    csv_out.writerow(row)
                print "Finished dumping for", quiz_name, quiz.version, qversion

    return record_list


def dump_all():
    quizzes = QuestionSet.objects()
    for quiz in quizzes:
        assert isinstance(quiz, QuestionSet)
        dump_quiz(quiz_name=quiz.set_topic, version=quiz.version)


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db')
    dump_all()