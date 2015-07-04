__author__ = 'moonkey'


#########################################
##########    LIST         ##############
#########################################
# regular expression matching to generation questions and distractors
WHAT_IS_REGEX = 0.0

# syntax tree
SENTENCE_STRUCTURE = 0.1

# using topic from same categories as distractors
RANDOM_CATEGORICAL_DISTRACTOR = 0.2


#########################################
##########    SETTINGS     ##############
#########################################
CURRENT_QUESTION_VERSION = RANDOM_CATEGORICAL_DISTRACTOR
DEFAULT_QUESTION_VERSION = CURRENT_QUESTION_VERSION # None