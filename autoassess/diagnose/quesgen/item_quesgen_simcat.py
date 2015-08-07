__author__ = 'moonkey'

from stem.item_question_stem_gen import generate_item_question_stem
from distractor.item_distractor_simcat import generate_item_distractors
from common import *


def generate_item_question_simcat(
        term, aliases, wikipage, distractor_num=3, version=None):
    question_generated = generate_item_question_stem(term, aliases, wikipage)
    question_stem = question_generated['stem']
    correct_answer = question_generated['answer']

    noun_form = None
    # TODO::
    # get the noun form of the correct_answer

    distractors = generate_item_distractors(
        term, noun_form=noun_form, max_num=distractor_num)

    if len(distractors) < distractor_num:
        raise ValueError("Only " + str(len(distractors)) + " generated.")

    question = {
        'quiz_topic': wikipage.title,
        'topic': term,
        'type': QUESTION_TYPE_MENTIONED_ITEM,  # first of this type
        'question_text': question_stem,
        'correct_answer': correct_answer,
        'distractors': distractors
    }
    return format_question(question)