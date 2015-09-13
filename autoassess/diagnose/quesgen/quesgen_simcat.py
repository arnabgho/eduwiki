from common import *
from distractor.distractor_simcat import *
from stem.question_stem_gen import generate_question_stem
from ..version_list import *

__author__ = 'moonkey'


def generate_question_simcat(prereq_tree, distractor_num=3, version=None):
    # wrong name: question_text should be question_stem or question_stem_text
    question_generated = generate_question_stem(prereq_tree['wikipage'])
    question_stem = question_generated['stem']
    correct_answer = question_generated['answer']
    stem_tenses = question_generated['tenses']

    if not question_stem or not correct_answer:
        return None
    # [ADD VERSION] choose the right function to generate distractors
    if version == WORD2VEC_CATEGORICAL_DISTRACTOR:
        distractors = generate_distractors_simcat(
            prereq_tree['wikipage'], stem_tenses, max_num=3)
    elif version == SKIPTHOUGHT_SIM_DISTRACTOR or \
         version == IN_TEXT_QUESTIONS_WITH_MENTION_COUNT_CANDIDATE or \
         version == SKIPTHOUGHT_SIM_DISTRACTOR_WITH_TWO_WAY_MEASURED_CANDIDATE:
        distractors = generate_distractors_simsent(
            prereq_tree['wikipage'], correct_answer,
            stem_tenses, max_num=3)
    else:
        distractors = []

    if len(distractors) < distractor_num:
        raise ValueError("Only " + str(len(distractors)) + " generated.")

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