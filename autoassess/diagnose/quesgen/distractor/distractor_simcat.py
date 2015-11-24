__author__ = 'moonkey'

from autoassess.diagnose.util.quesgen_util import *
from distractor_common import distractor_from_single_sentence
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from distractor_source import similar_page_titles_of_samecat
from autoassess.diagnose.util.NLPU.doc_sim import skip_thoughts_n_sim, \
    sort_docs_by_similarity
import time


def generate_distractors_simcat(wikipage, tenses=[], max_num=3, try_max_num=10):
    """
    :param wikipage:
    :param tenses:
    :param max_num:
    :param try_max_num: Try (try_max_num) article sentences to generate
            a distractor, if fail, then discard the article, to save time
    :return:
    """
    distractors = []

    for p_title in similar_page_titles_of_samecat(wikipage):
        try:
            dist_start = time.time()
            sim_page = WikipediaWrapper.page(title=p_title)
            page_ret_done = time.time()
            print 'page:', page_ret_done - dist_start
            sentences = topic_mentioning_sentence_generator(sim_page)
            sentence_done = time.time()
            print 'sentence:', sentence_done - page_ret_done
            distractor = None
            try_num = 0
            for sentence in sentences:
                try_num += 1
                if try_num > try_max_num:
                    break  # give up this page
                distractor = distractor_from_single_sentence(
                    sentence, sim_page.title, tenses,
                    original_topic=wikipage.title)
                if distractor:
                    break
            distractor_done = time.time()
            print 'sentence:', distractor_done - sentence_done
            if distractor:
                distractors.append(distractor)
                if len(distractors) >= max_num:
                    break
        except Exception:
            # There might be page error,
            # or a distractor cannot be generated from the page.
            # TODO::logging
            continue
    return distractors


def generate_distractors_simsent(wikipage, correct_ans="",
                                 tenses=[], max_num=3):
    dis_start = time.time()
    pre_select_num = min(max_num * 3, 10)
    pre_select_distractors = generate_distractors_simcat(
        wikipage, tenses, pre_select_num)
    pre_select_time = time.time()
    print 'pre_select', pre_select_time - dis_start
    sorted_distractors = sort_docs_by_similarity(
        doc0=correct_ans,
        doc_list=pre_select_distractors,
        sim_func=skip_thoughts_n_sim,
        remove_sub=False)
    print 'rank', time.time() - pre_select_time
    print 'generate_distractors_simsent', time.time() - dis_start
    return sorted_distractors[:max_num]