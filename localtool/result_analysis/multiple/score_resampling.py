from __future__ import division

__author__ = 'moonkey'

import sklearn.utils
from autoassess.models import *
import csv
import numpy as np


def bootstrap_resample(X, n=None):
    """ Bootstrap resample an array_like
    Parameters
    ----------
    X : array_like
      data to resample
    n : int, optional
      length of resampled array, equal to len(X) if n==None
    Results
    -------
    returns X_resamples
    """
    if type(X) is not np.ndarray:
        X = np.array(X)
    if n is None:
        n = len(X)

    resample_i = np.floor(np.random.rand(n) * len(X)).astype(int)
    X_resample = X[resample_i]
    return X_resample.tolist()


def resample_students(student_ans, n_samples=100):
    # student_ans = {
    # "workerId": [...]
    # }
    student_list = [s for s in student_ans]

    print "student_list", student_list
    # sampled_students = sklearn.utils.resample(
    # student_list, replace=True, n_samples=n_samples)
    sampled_students = bootstrap_resample(student_list, n=n_samples)
    new_student_dict = {}
    for idx, stu in enumerate(sampled_students):
        sampled_stu_new_name = str(idx) + "_" + stu
        new_student_dict[sampled_stu_new_name] = student_ans[stu]

    return new_student_dict


def read_student_answers_from_db(quiz):
    quiz_answers = QuizAnswers.objects(quiz=quiz)


    # ###########
    # ### stat for each student
    # ###########
    student_ans = {}

    for quiz_ans in quiz_answers:
        final_answers = quiz_ans.quiz_final_answers
        workerId = quiz_ans.workerId

        for final_ans in final_answers:
            if workerId not in student_ans:
                student_ans[workerId] = []
            student_ans[workerId].append(final_ans)
    return student_ans


def separate_student_answers_by_version(student_ans):
    student_ans_of_version = {}
    for workerId in student_ans:
        for sq_ans in student_ans[workerId]:
            version = sq_ans.question.version

            if version not in student_ans_of_version:
                student_ans_of_version[version] = {}

            if workerId not in student_ans_of_version[version]:
                student_ans_of_version[version][workerId] = []

            student_ans_of_version[version][workerId].append(sq_ans)

    return student_ans_of_version


def student_ans_dict_to_record(student_ans):
    record_list = []
    for workerId in student_ans:
        for sq_ans in student_ans[workerId]:
            # Note workerId does not match the sq_ans.workerId
            # if this is from bootstrap sampling with changed names
            exercise = sq_ans.question.topic
            time_taken = sq_ans.submit_time_delta
            correct = sq_ans.correctness

            record = (workerId, exercise, time_taken, correct)

            record_list.append(record)

    if not record_list:
        print "No record !!!"
        return False
    return record_list


def write_record_list_to_file(record_list, quiz_name, quiz_version=None):
    record_file_name = './response_data/' + quiz_name.replace(" ", "_")
    if quiz_version:
        record_file_name += "_v" + str(quiz_version)

    record_file_name += '.response'
    with open(record_file_name, 'w') as outfile:
        csv_out = csv.writer(outfile)
        for row in record_list:
            csv_out.writerow(row)
        print "Finished dumping for", quiz_name, quiz_version


def dump_quiz(quiz_name, version, bootstrap_amount=100):
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

    if len(student_ans) < bootstrap_amount:
        student_ans = resample_students(student_ans, n_samples=bootstrap_amount)
    record_list = student_ans_dict_to_record(student_ans)
    write_record_list_to_file(record_list, quiz.set_topic, quiz_version=None)

    student_ans_of_v = separate_student_answers_by_version(student_ans)
    for v in student_ans_of_v:
        record_list_v = student_ans_dict_to_record(student_ans_of_v[v])
        write_record_list_to_file(record_list_v, quiz.set_topic, quiz_version=v)

    return record_list


def dump_all(only_manual=True):
    if only_manual:
        quizzes = QuestionSet.objects(version=-1.0)
    # quizzes = QuestionSet.objects()
    for quiz in quizzes:
        assert isinstance(quiz, QuestionSet)
        dump_quiz(quiz_name=quiz.set_topic, version=quiz.version)


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    dump_all()
    # stats = db_quiz_stats()
    # for stat in stats:
    # for p in stat:
    # print p

    # quiz = QuestionSet.objects(
    # set_topic="Customer satisfaction", version=-1.0)[0]
    # student_ans = read_student_answers_from_db(quiz)
    # student_ans_of_v = separate_student_answers_by_version(student_ans)
    # for v in student_ans_of_v:
    # print "Version ", v
    # student_ans = student_ans_of_v[v]
    # for s in student_ans:
    #         print s, student_ans[s]

