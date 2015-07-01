# coding=utf-8
__author__ = 'moonkey'

import re
import random
import util.nlp_util
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import normalize
import networkx as nx
import numpy
import nltk
import os
from util.nlp_util import NlpUtil
import sys
from util.wikipedia_util import WikipediaWrapper
from question_stem_gen import *
from distractorgen import *

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

    distractors = generate_distractors_from_prereqs(prereq_tree, stem_tenses)
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