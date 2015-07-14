__author__ = 'moonkey'

from autoassess.diagnose.util.quesgen_util import *
from distractor_common import distractor_from_single_sentence
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from collections import defaultdict
import random
from distractor_source import similar_pages_of_samecat


def generate_distractors_simcat(wikipage, tenses=[], max_num=3):
    distractors = []

    for p_title in similar_pages_of_samecat(wikipage):
        sim_page = WikipediaWrapper.page(title=p_title)
        sentences = topic_mentioning_sentence_generator(sim_page)
        distractor = None
        for sentence in sentences:
            distractor = distractor_from_single_sentence(
                sentence, sim_page.title, tenses, original_topic=wikipage.title)
            if distractor:
                break

        if distractor:
            distractors.append(distractor)
            if len(distractors) >= max_num:
                break

    return distractors
