__author__ = 'moonkey'

from autoassess.diagnose.quesgen import quesgen_sentstruct
from autoassess.diagnose.quesgen import quesgen_whatisregex

from autoassess.diagnose.verison_list import *


def generate_question(prereq_tree, version=None):
    if version == WHAT_IS_REGEX:
        return quesgen_whatisregex.generate_question_what_is(prereq_tree)
    if version == SENTENCE_STRUCTURE:
        return quesgen_sentstruct.generate_question_sentstruct(prereq_tree)
    if version == RANDOM_CATEGORICAL_DISTRACTOR:
        return quesgen_sentstruct.generate_question_samecat(prereq_tree)

    return None