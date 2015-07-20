__author__ = 'moonkey'

from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from collections import defaultdict
import random
from sys import maxint
from autoassess.diagnose.util.NLPU import sent_sim


def page_ids_of_same_category(wikipage, max_num=maxint, cat_count=False):
    cat_page_lists = []
    for cat in wikipage.categories:
        cat_page_list = WikipediaWrapper.pages_from_category(cat)

        # remove the wikipage itself
        if wikipage.pageid in cat_page_list:
            cat_page_list.remove(wikipage.pageid)
        cat_page_lists.append(cat_page_list)

    # merge lists
    page_list = [item for sublist in cat_page_lists for item in sublist]
    counted_pages = count_rank(page_list)

    if len(counted_pages) <= max_num:
        if cat_count:
            return [p for p in counted_pages]
        else:
            return [p[0] for p in counted_pages]

    # first pick out pages with more shared categories
    result = []
    for p_c in counted_pages:
        page = p_c[0]
        count = p_c[1]
        if count > 1:
            if cat_count:
                result.append(p_c)
            else:
                result.append(page)
        else:
            break

        if len(result) >= max_num:
            return result

    one_count_pages = counted_pages[len(result):]
    rest_len = min(max_num - len(result), len(one_count_pages))
    random_one_count_pages = random.sample(one_count_pages, rest_len)
    if cat_count:
        result += random_one_count_pages
    else:
        result += [p[0] for p in random_one_count_pages]

    return result


def count_rank(xs):
    counts = defaultdict(int)
    for x in xs:
        counts[x] += 1
    sorted_xs = sorted(counts.items(), reverse=True, key=lambda tup: tup[1])
    return sorted_xs


def similar_pages_of_samecat(wikipage):
    """

    :param wikipage:
    :return: page titles of pages with shared category,
                ranked by title similarity
    """
    page_ids = page_ids_of_same_category(wikipage=wikipage, cat_count=False)
    page_titles = [WikipediaWrapper.page_title_from_id(pid) for pid in page_ids]

    page_titles = [p for p in page_titles if p is not None]
    # in case the page title is not successfully retrieved, like the pageid is
    # no longer there.
    similar_pages = sent_sim.sort_docs_by_similarity(
        doc0=wikipage.title, doc_list=page_titles,
        sim_func=sent_sim.word2vec_n_sim)
    return similar_pages