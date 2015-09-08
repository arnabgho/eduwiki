__author__ = 'moonkey'

from answer_io_util import *
from bayesian_irt import birt


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')

    quiz = QuestionSet.objects(
        set_topic="Customer satisfaction", version=-1.0)[0]
    student_ans = read_student_answers_from_db(quiz)
    ans_mtx, students, questions = answer_dict_to_arrays(student_ans)
    print len(questions), [q.topic for q in questions]
    print len(students), students
    a, b, theta = birt.bayesian_irt(ans_mtx)
    birt.plot_theta_trace(theta)