__author__ = 'moonkey'

from autoassess.diagnose.util.quesgen_util import *
from distractor_common import distractor_from_single_sentence
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from collections import defaultdict
import random


def generate_distractors_samecat(wikipage, tenses=[], max_num=3):
    distractors = []

    for p_id in page_ids_of_samecategory(wikipage):
        page = WikipediaWrapper.page(pageid=p_id)
        sentences = topic_mentioning_sentence_generator(page)
        distractor = None
        for sentence in sentences:
            distractor = distractor_from_single_sentence(
                sentence, page.title, tenses)
            if distractor:
                break

        if distractor:
            distractors.append(distractor)
            if len(distractors) >= max_num:
                break
    return distractors


def page_ids_of_samecategory(wikipage, max_num=7):
    cat_page_lists = []
    for cat in wikipage.categories:
        cat_page_list = WikipediaWrapper.pages_from_category(cat)
        if wikipage.pageid in cat_page_list:
            cat_page_list.remove(wikipage.pageid)
        cat_page_lists.append(cat_page_list)

    # merge lists
    page_list = [item for sublist in cat_page_lists for item in sublist]
    counted_pages = count_rank(page_list)

    print counted_pages[:10]  # for debug

    if len(counted_pages) <= max_num:
        return [p[0] for p in counted_pages]

    # first pick out pages with more shared categories
    result = []
    for p_c in counted_pages:
        page = p_c[0]
        count = p_c[1]
        if count > 1:
            result.append(page)
        else:
            break

        if len(result) >= max_num:
            break

    one_count_pages = counted_pages[len(result):]
    random_one_count_pages = random.sample(one_count_pages,
                                           max_num - len(result))
    result += [p[0] for p in random_one_count_pages]

    return result


def count_rank(xs):
    counts = defaultdict(int)
    for x in xs:
        counts[x] += 1
    sorted_xs = sorted(counts.items(), reverse=True, key=lambda tup: tup[1])
    return sorted_xs