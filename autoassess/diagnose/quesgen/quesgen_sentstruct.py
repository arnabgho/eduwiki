# coding=utf-8
__author__ = 'moonkey'

from common import *

from autoassess.diagnose.quesgen.stem.question_stem_gen import *
from autoassess.diagnose.quesgen.distractor.distractor_prereq import *


def generate_question_sentstruct(prereq_tree):
    # wrong name: question_text should be question_stem or question_stem_text
    question_generated = generate_question_stem(prereq_tree['wikipage'])
    question_stem = question_generated['stem']
    correct_answer = question_generated['answer']
    stem_tenses = question_generated['tenses']

    distractors = generate_distractors_prereqs(prereq_tree, stem_tenses)
    question = {
        'topic': prereq_tree['wikipage'].title,
        'type': QUESTION_TYPE_WHAT_IS,
        'question_text': question_stem,
        'correct_answer': correct_answer,
        'distractors': distractors
    }

    return format_question(question)





