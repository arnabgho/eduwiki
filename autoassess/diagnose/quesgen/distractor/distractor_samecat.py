__author__ = 'moonkey'

from autoassess.diagnose.util.quesgen_util import *
from distractor_common import distractor_from_single_sentence
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper

from distractor_source import page_ids_of_same_category


def generate_distractors_samecat(wikipage, tenses=[], max_num=3):
    distractors = []

    for p_id in page_ids_of_same_category(wikipage, max_num=10):
        sim_page = WikipediaWrapper.page(pageid=p_id)
        sentences = topic_mentioning_sentence_generator(sim_page)
        distractor = None
        for sentence in sentences:
            distractor = distractor_from_single_sentence(
                sentence, sim_page.title, tenses,
                original_topic=wikipage.title)
            if distractor:
                break

        if distractor:
            distractors.append(distractor)
            if len(distractors) >= max_num:
                break

    return distractors