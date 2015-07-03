from autoassess.diagnose.quesgen import quesgen_sentstruct

__author__ = 'moonkey'


QUESTION_VERISON = None


def generate_question(prereq_tree):
    return quesgen_sentstruct.generate_question(prereq_tree)
    # return quesgen_whatisregex.generate_question_what_is(prereq_tree)
