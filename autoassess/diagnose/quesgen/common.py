__author__ = 'moonkey'

import random

# Note: keep coherent with '''WikiQuestion.WikiQuestionType'''
QUESTION_TYPE_WHAT_IS = 'WHAT_IS'
QUESTION_TYPE_MENTIONED_ITEM = "KEY_ITEM"


def format_question(question):
    possible_answers = [{'text': question['correct_answer'], 'correct': True}]

    for d in question['distractors']:
        possible_answers.append({'text': d, 'correct': False})

    random.shuffle(possible_answers)
    question['choices'] = possible_answers

    question.pop('distractors', None)

    return question

    # formatted_question = {
    # 'topic': question['topic'],
    # 'question_text': question['question_text'],
    #     'choices': possible_answers,
    #     'type': question['type']
    # }
    # return formatted_question


def extract_same_part(stem, answers):
    first_words = [ans.split(' ')[0] for ans in answers]
    if len(set(first_words)) != 1:
        return stem, answers
    else:
        first_word = first_words[0]
        insert_pos = stem.rfind(' ')
        stem = stem[:insert_pos] + ' ' + first_word + stem[insert_pos:]
        answers = [ans[len(first_word):].lstrip('') for ans in answers]
        return stem, answers