__author__ = 'moonkey'


# ########################################
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


########################################
#########      SET TYPE      ###########
########################################
SET_PREREQ = "Prereq"
SET_MENTIONED = "Mentioned"


#########################################
#########################################
##########    SETTINGS     ##############
#########################################
#########################################
CURRENT_QUESTION_VERSION = SKIPTHOUGHT_SIM_DISTRACTOR
CURRENT_QUESTION_SET = SET_MENTIONED

#################
DIAGNOSE_QUESTION_VERSION = CURRENT_QUESTION_VERSION  # None
MTURK_QUESTION_VERSION = CURRENT_QUESTION_VERSION  # None

print "Current Question Version:", CURRENT_QUESTION_VERSION


