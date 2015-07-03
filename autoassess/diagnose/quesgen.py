from autoassess.diagnose.questiongenpack import quesgen_sentstruct

__author__ = 'moonkey'

QUESTION_TYPE_WHAT_IS = 'WHAT_IS'
QUESTION_TYPE_WHY_IS = 'WHY_IS'


def generate_question(prereq_tree):
    return quesgen_sentstruct.generate_question(prereq_tree)
    # return quesgen_whatisregex.generate_question_what_is(prereq_tree)