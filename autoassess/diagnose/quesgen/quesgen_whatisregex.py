__author__ = 'moonkey'

import re
from common import *



def generate_question_what_is(prereq_tree):
    # TODO

    question_text = "What is " + prereq_tree['wikipage'].title
    correct_answer = return_what_is(wikipage=prereq_tree['wikipage'])
    question = {
        'topic': prereq_tree['wikipage'].title,
        'type': QUESTION_TYPE_WHAT_IS,
        'question_text': question_text,
        'correct_answer': correct_answer
    }

    distractors = []
    for child in prereq_tree['children']:
        distractor = return_what_is(child['wikipage'])
        distractors.append(distractor)

    question['distractors'] = distractors

    return format_question(question)


def return_what_is(wikipage):
    """
    "<topic>\s[^\.](is|was)([^\.])+\." or None (if no matches)
    :return: first mention in article of the following regex
    """
    # Optimize over the regular expresson

    # TODO:: the number 5 might be hacked for a specific topic,

    topic = wikipage.title
    # figure out what the regex is doing and make it general
    regex_str1 = \
        '(' + topic[:5] + '(' + topic[5:] + ')?' + '|' + '(' + topic[:len(topic) - 5] + ')?' + topic[len(topic) - 5:] \
        + ')'
    regex_str2 = '(\s[^\.]*(is|was|can be regarded as)|[^,\.]{,15}?,)\s([^\.]+)\.(?=\s)'
    regex_str = regex_str1 + regex_str2
    # (abcde(fghijklmnopqrst)?|(abcdefghijklmno)?pqrst)
    # (\s[^\.]*(is|was|can be regarded as)|[^,\.]{,15}?,)\s([^\.]+)\.(?=\s)

    what_is_pattern = re.compile(regex_str, re.IGNORECASE)
    mentions = re.findall(what_is_pattern, wikipage.content)

    if not mentions:
        what_is = "can't find a good description"
    else:
        what_is = mentions[0][5]
        what_is = re.sub(r'.*\sis\s+(.*)$', r'\1', what_is)

    return what_is