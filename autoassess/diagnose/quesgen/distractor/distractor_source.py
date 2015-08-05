__author__ = 'moonkey'

from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from autoassess.diagnose.util.wikipedia_util import page_titles_of_same_category
from autoassess.diagnose.util import  wikipedia_util
from collections import defaultdict
from autoassess.diagnose.util.NLPU import doc_sim
from sys import maxint


def page_ids_of_same_category(wikipage, max_num=maxint, cat_count=False):
    return wikipedia_util.page_ids_of_same_category(
        wikipage, max_num, cat_count)


def count_rank(xs):
    counts = defaultdict(int)
    for x in xs:
        counts[x] += 1
    sorted_xs = sorted(counts.items(), reverse=True, key=lambda tup: tup[1])
    return sorted_xs


def similar_page_titles_of_samecat(wikipage):
    """
    :param wikipage:
    :return: page titles of pages with shared category,
                ranked by title similarity
    """

    page_titles = page_titles_of_same_category(
        wikipage, cat_count=False)
    similar_pages = doc_sim.sort_docs_by_similarity(
        doc0=wikipage.title, doc_list=page_titles,
        sim_func=doc_sim.word2vec_n_sim)
    return similar_pages