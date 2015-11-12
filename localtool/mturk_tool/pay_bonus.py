__author__ = 'moonkey'

from botowrapper import connect_mturk
from autoassess.models import *

# TODO:: Test in sandbox first

# Read in data
mix_quizzes = QuestionSet.objects(version__lte=0.0)
mix_quizzes = list(mix_quizzes) # [q for q in mix_quizzes]


answers_for_quiz = {}
for quiz in mix_quizzes:
    answers_for_current_quiz = QuizAnswers.objects(
        quiz=quiz,
        workerId__exists=True, assignmentId__exists=True,
        final_answers_ne=[])
    answers_for_current_quiz = list(answers_for_current_quiz)
    for a in answers_for_current_quiz:
        pass #TODO::
    answers_for_quiz[id] = []

    pass

# Calculate money portion of each person

budget_with_amazon_fee = 10
budget = int(budget_with_amazon_fee / 1.4)


# TODO:: Test in sandbox first
sandbox = True
mtc = connect_mturk(sandbox=sandbox)
# get bonus already granted

# Actually pay them