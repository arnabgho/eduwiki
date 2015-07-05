# coding=utf-8
__author__ = 'moonkey'

from common import *

from autoassess.diagnose.quesgen.stem.question_stem_gen import *
from autoassess.diagnose.quesgen.distractor.distractor_prereq import *
from autoassess.diagnose.quesgen.distractor.distractor_samecat import *

QUESTION_TYPE_WHAT_IS = 'WHAT_IS'
QUESTION_TYPE_WHY_IS = 'WHY_IS'


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


def generate_question_samecat(prereq_tree, distractor_num=3):
    # wrong name: question_text should be question_stem or question_stem_text
    question_generated = generate_question_stem(prereq_tree['wikipage'])
    question_stem = question_generated['stem']
    correct_answer = question_generated['answer']
    stem_tenses = question_generated['tenses']

    # distractors = generate_distractors_prereqs(prereq_tree, stem_tenses)
    distractors = generate_distractors_samecat(
        prereq_tree['wikipage'], stem_tenses)

    if len(distractors) < distractor_num:
        raise ValueError("Only "+str(len(distractors))+" generated.")

    extracted = extract_same_part(question_stem, [correct_answer] + distractors)
    if extracted:
        question_stem = extracted[0]
        correct_answer = extracted[1][0]
        distractors = extracted[1][1:]

    question = {
        'topic': prereq_tree['wikipage'].title,
        'type': QUESTION_TYPE_WHAT_IS,
        'question_text': question_stem,
        'correct_answer': correct_answer,
        'distractors': distractors
    }
    return format_question(question)


