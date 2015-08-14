__author__ = 'moonkey'

from stem.item_question_stem_gen import generate_item_question_stem
from distractor.item_distractor_simcat import item_distractor_generator
from common import *
from autoassess.diagnose.util.quesgen_util import topic_regex
import re


def generate_item_question_simcat(
        term, aliases, wikipage, distractor_num=3,
        sentence_blacklist=list(), version=None):
    # Add syntax tree matching here.

    question_generated = generate_item_question_stem(
        term, aliases, wikipage, sentence_black_list=sentence_blacklist)
    question_stem = question_generated['stem']
    correct_answer = question_generated['answer']
    original_sentence = question_generated['original_sentence']
    distractors = []
    for distractor in item_distractor_generator(term, correct_answer):
        if not distractor:
            break
        if is_heuristically_good_item_distractor(distractor, original_sentence):
            distractors.append(distractor)
        if len(distractors) > distractor_num:
            break

    if len(distractors) < distractor_num:
        raise ValueError("Only " + str(len(distractors)) + " generated.")

    question = {
        'quiz_topic': wikipage.title,
        'topic': term,
        'type': QUESTION_TYPE_MENTIONED_ITEM,  # first of this type
        'question_text': question_stem,
        'correct_answer': correct_answer,
        'distractors': distractors,
        'original_sentence': original_sentence,
    }
    return format_question(question)


def is_heuristically_good_item_distractor(distractor, sentence):
    if re.search(topic_regex(distractor), sentence):
        return False
    else:
        return True