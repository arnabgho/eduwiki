__author__ = 'moonkey'

from autoassess.diagnose.version_list import *
from autoassess.diagnose.quesgen import quesgen_whatisregex
from autoassess.diagnose.quesgen import quesgen_sentstruct
from autoassess.diagnose.quesgen import quesgen_samcat
from autoassess.diagnose.quesgen import quesgen_simcat
from autoassess.diagnose.quesgen import item_quesgen_simcat


def generate_question(prereq_tree, version=None):
    if version == WHAT_IS_REGEX:
        return quesgen_whatisregex.generate_question_what_is(prereq_tree)
    if version == SENTENCE_STRUCTURE:
        return quesgen_sentstruct.generate_question_sentstruct(prereq_tree)
    if version == RANDOM_CATEGORICAL_DISTRACTOR:
        return quesgen_samcat.generate_question_samecat(prereq_tree)
    if version == WORD2VEC_CATEGORICAL_DISTRACTOR:
        return quesgen_simcat.generate_question_simcat(
            prereq_tree, version=version)
    if version == SKIPTHOUGHT_SIM_DISTRACTOR:
        return quesgen_simcat.generate_question_simcat(
            prereq_tree, version=version)
    return None


def generate_item_question(
        term, aliases, wikipage, sentence_blacklist=list(), version=None):
    return item_quesgen_simcat.generate_item_question_simcat(
        term, aliases, wikipage, sentence_blacklist=sentence_blacklist
    )