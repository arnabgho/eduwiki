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

# using topic with similar embedded vectors
WORD2VEC_CATEGORICAL_DISTRACTOR = 0.22
SKIPTHOUGHT_SIM_DISTRACTOR = 0.23

IN_TEXT_QUESTIONS = 0.24

MANUALLY_ADDED = -1.0

########################################
#########      SET TYPE      ###########
########################################
SET_PREREQ = "Prereq"
SET_MENTIONED = "Mentioned"
# for manually composed question sets
SET_SELF_DEFINED = "Self-defined"

#########################################
#########################################
##########    SETTINGS     ##############
#########################################
#########################################
CURRENT_QUESTION_VERSION = SKIPTHOUGHT_SIM_DISTRACTOR
CURRENT_QUESTION_SET = SET_MENTIONED
WITH_PREREQ = True

#################
DIAGNOSE_QUESTION_VERSION = IN_TEXT_QUESTIONS
MTURK_QUESTION_VERSION = CURRENT_QUESTION_VERSION

print "Current Question Version:", CURRENT_QUESTION_VERSION
print "Current Set Type:", CURRENT_QUESTION_SET

