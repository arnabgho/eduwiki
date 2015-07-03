# coding=utf-8
__author__ = 'moonkey'

import random

from autoassess.diagnose.quesgen.stem.question_stem_gen import *
from autoassess.diagnose.quesgen.distractor.distractor_prereq import *
from autoassess.diagnose.quesgen.distractor.distractor_samecat import *

QUESTION_TYPE_WHAT_IS = 'WHAT_IS'
QUESTION_TYPE_WHY_IS = 'WHY_IS'


def generate_question(prereq_tree):
    # wrong name: question_text should be question_stem or question_stem_text
    question_generated = generate_question_stem(prereq_tree['wikipage'])
    question_stem = question_generated['stem']
    correct_answer = question_generated['answer']
    stem_tenses = question_generated['tenses']

    question = {
        'topic': prereq_tree['wikipage'].title,
        'type': QUESTION_TYPE_WHAT_IS,
        'question_text': question_stem,
        'correct_answer': correct_answer
    }

    # distractors = generate_distractors_prereqs(prereq_tree, stem_tenses)
    distractors = generate_distractors_same_categories(
        prereq_tree['wikipage'], stem_tenses)
    question['distractors'] = distractors

    return format_question(question)


def format_question(question):
    possible_answers = [{'text': question['correct_answer'], 'correct': True}]

    for d in question['distractors']:
        possible_answers.append({'text': d, 'correct': False})

    random.shuffle(possible_answers)
    formated_question = {
        'topic': question['topic'],
        'question_text': question['question_text'],
        'choices': possible_answers,
        'type': question['type']
    }
    return formated_question