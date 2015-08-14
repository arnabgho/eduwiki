__author__ = 'moonkey'

from autoassess.diagnose.util.quesgen_util import *
from distractor_common import distractor_from_single_sentence
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from distractor_source import similar_page_titles_of_samecat
from autoassess.diagnose.util.NLPU.doc_sim import skip_thoughts_n_sim, \
    sort_docs_by_similarity


def generate_distractors_simcat(wikipage, tenses=[], max_num=3):
    distractors = []

    for p_title in similar_page_titles_of_samecat(wikipage):
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


def generate_distractors_simsent(wikipage, correct_ans="",
                                 tenses=[], max_num=3):
    pre_select_num = min(max_num * 3, 20)
    pre_select_distractors = generate_distractors_simcat(
        wikipage, tenses, pre_select_num)
    sorted_distractors = sort_docs_by_similarity(
        doc0=correct_ans,
        doc_list=pre_select_distractors,
        sim_func=skip_thoughts_n_sim,
        remove_sub=False)
    return sorted_distractors[:max_num]