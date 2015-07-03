from ...util.quesgen_util import *

from distractor_common import distractor_from_single_sentence


def generate_distractors_prereqs(prereq_tree, tenses=[], max_num=3):
    distractors = []
    for child in prereq_tree['children']:
        sentences = topic_mentioning_sentence_generator(child['wikipage'])
        distractor = None
        for sentence in sentences:
            distractor = distractor_from_single_sentence(sentence, child['wikipage'].title, tenses)
            if distractor:
                break

        if distractor:
            distractors.append(distractor)
            if len(distractors) >= max_num:
                break
    return distractors

