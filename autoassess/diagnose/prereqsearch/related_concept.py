from __future__ import division

__author__ = 'moonkey'

from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from autoassess.diagnose.util.wikipedia_util import page_titles_of_same_category
from autoassess.diagnose.util.wikipedia_util import filter_wikilink
from autoassess.diagnose.util.wikipedia_util import count_rank

from autoassess.diagnose.util.quesgen_util import topic_remove_bracket
from autoassess.diagnose.util.quesgen_util import topic_regex

import re
import sys
import operator
import networkx as nx
import matplotlib.pyplot as plt
import collections

from sklearn.feature_extraction.dict_vectorizer import DictVectorizer
from sklearn.cluster import DBSCAN, KMeans
import math

# [Future]TODO:: Factors to be included that are relevant to "good" subtopics
# categorical, mentioning (times, linkage),
# section title, emphasizing ''',

# Some way is needed for both signifying sharing similarity,
# and also RULING OUT too general concepts


def related_terms_in_article(wikipage):
    """

    :param wikipage:
    :return:
    """
    mm_links, aliases = most_mentioned_wikilinks(wikipage, with_count=False)
    related_terms = []
    for l in mm_links:
        if len(related_terms) > 5:
            break

        # to deal with "Markov", "Markov Model"

        # Supposedly remove more broad concept, and add more detailed ones
        related_terms = [x for x in related_terms if x not in l]
        to_add_l = True
        for already_added_link in related_terms:
            if l in already_added_link:
                to_add_l = False
                break
        if to_add_l:
            related_terms.append(l)

    return related_terms, aliases


# def find_related_terms(wikipage):
# # find overlapps in wikilinks and same category links
# wikilinks = [filter_wikilink(l.target) for l in wikipage.wikilinks]
# counted_wikilinks = count_rank(wikilinks)
# wikilinks = [c[0] for c in counted_wikilinks]
# same_cat_links = page_titles_of_same_category(wikipage)
#
# overlap_links = []
# for l in wikilinks:
# if l in same_cat_links:
# overlap_links.append(l)
#
# print overlap_links


def most_mentioned_wikilinks(wikipage, with_count=True):
    alias = {}

    main_topic = filter_wikilink(wikipage.title)
    wikilinks = wikipage.wikilinks
    for idx, l in enumerate(wikilinks):
        target = filter_wikilink(l.target, ignore_cat=True)

        # filter disambiguous links : 'Social psychology'
        # contains "Social Psychology (journal)"
        if target and topic_remove_bracket(
                target).lower() == topic_remove_bracket(main_topic).lower():
            target = None

        wikilinks[idx].target = target

    wikilinks = [l for l in wikilinks if l.target is not None]

    for l in wikilinks:
        if l.target not in alias:
            alias[l.target] = set()

        if l.text is not None:
            alias[l.target].add(l.text)

        title_contained_in_alias = False
        title_form_topic = topic_remove_bracket(l.target)
        for al in alias[l.target]:
            if title_form_topic in al:
                title_contained_in_alias = True
                break
        if not title_contained_in_alias:
            alias[l.target].add(title_form_topic)
        # "Software agent" will not be added, if "agent" is present,
        # as a short name covers all.

        # add abbreviations to alias
        # the abbreviations should appear in "(xxx)" following the link term
        # like "MDP", "GloVe"
        abbr_als = []
        for al in alias[l.target]:
            abbr_pattern = "" + re.escape(al) + " \(([\w-]+?)\)"  # K-K-T???

            abbr_matches = re.search(
                abbr_pattern, wikipage.content, re.IGNORECASE)
            if not abbr_matches:
                continue
            abbr_match = abbr_matches.group(1)
            if re.search('.*'.join(abbr_match), al, re.IGNORECASE):
                abbr_als.append(abbr_match)

        for al in abbr_als:
            alias[l.target].add(al)

    # get numbers of mention of each link target and their alias
    term_count = {}
    for l in alias:
        term_count[l] = 0
        for al in alias[l]:
            al_pattern = re.escape(al)
            if len(al) <= 2:
                al_pattern = '\b' + al_pattern + '\b'
            # + '\b'  # "s" for plurals may appear
            term_count[l] += len(re.findall(
                al_pattern, wikipage.content, re.IGNORECASE))

    # when "Markov", "Markov model"show up together
    # count(Markov) -= count(Markov model)
    try:
        for l in alias:
            for other_l in alias:
                if other_l == l:
                    continue
                if topic_remove_bracket(
                        other_l).lower() in topic_remove_bracket(l).lower():
                    term_count[other_l] -= term_count[l]
    except Exception as e:
        print >> sys.stderr, e
    # TODO:: when Markov, Markov model, Hidden Markov model show up together


    # get high number mention topics
    most_mentioned = sorted(
        term_count.items(), key=operator.itemgetter(1), reverse=True)

    if not with_count:
        most_mentioned = [m[0] for m in most_mentioned]

    return most_mentioned, alias


def list_overlapping(a, b):
    a_multiset = collections.Counter(a)
    b_multiset = collections.Counter(b)

    overlap = list((a_multiset & b_multiset).elements())
    # a_remainder = list((a_multiset - b_multiset).elements())
    # b_remainder = list((b_multiset - a_multiset).elements())
    # print overlap, a_remainder, b_remainder

    return overlap


def similarly_covered_topics(wikipage, with_count=False):
    link_to_main = WikipediaWrapper.page_ids_links_here(wikipage.title)

    mm_links, aliases = most_mentioned_wikilinks(wikipage, with_count=True)
    mm_link_titles = [m[0] for m in mm_links]

    links_here_dict = {}
    for title in mm_link_titles:
        try:
            link_to_title = WikipediaWrapper.page_ids_links_here(title)
            links_here_dict.update({title: link_to_title})
        except Exception as e:
            pass

    # calculate coverage overlap
    link_overlap = {}
    for title in links_here_dict:
        overlap_sim = len(list_overlapping(
            links_here_dict[title], link_to_main))
        overlap_sim /= math.exp(len(links_here_dict[title]) / len(link_to_main))

        link_overlap.update(
            {title: overlap_sim}
        )

    mostly_together_linked = sorted(
        link_overlap.items(), key=operator.itemgetter(1), reverse=True)

    if not with_count:
        mostly_together_linked = [m[0] for m in mostly_together_linked]

    return mostly_together_linked, aliases


def similar_concpet_by_clustering_bag_of_links_to_here(wikipage):
    link_to_main = WikipediaWrapper.page_ids_links_here(wikipage.title)
    mm_links, aliases = most_mentioned_wikilinks(wikipage, with_count=True)
    mm_link_titles = [m[0] for m in mm_links]

    links_here_dict = {}
    for title in mm_link_titles:
        try:
            link_to_title = WikipediaWrapper.page_ids_links_here(title)
            links_here_dict.update({title: link_to_title})
        except Exception as e:
            pass

    return cluster_bag_of_links_to_here(links_here_dict)


def cluster_bag_of_links_to_here(links_here_dict):
    # convert it to bags of links-to-here (B-O-L)
    #
    # for title in links_here_dict:
    title_list = []
    feature_dict_list = []
    for title in links_here_dict:
        title_list.append(title)
        links = links_here_dict[title]
        feature_dict = collections.Counter(links)  # {1435:1, 235345:1, ...}
        feature_dict_list.append(feature_dict)
    vec = DictVectorizer()
    bol_mtx = vec.fit_transform(feature_dict_list).toarray()
    print bol_mtx.shape

    # TODO::
    # DBSCAN might be the best for this
    # but it is good for data with similar density, which does not hold here
    # db = DBSCAN(eps=10, min_samples=3)
    # clusters = db.fit_predict(bol_mtx)

    kmeans = KMeans(
        init='k-means++',
        n_clusters=int(math.sqrt(len(title_list))),
        n_init=10)
    clusters = kmeans.fit_predict(bol_mtx)

    cluster_set = collections.Counter(clusters)
    print cluster_set
    clusters = [(title_list[idx], c) for idx, c in enumerate(clusters)]
    return clusters


def sparse_mention_spanning_graph(wikipage):
    """
    To get a graph for the mentions
    :return:
    """
    least_mention = 5
    mention_graph = nx.DiGraph()
    current_title = wikipage.title
    mention_graph.add_node(current_title)

    spanning_wikipages = [wikipage]
    next_depth_wikipages = []
    for depth in range(2, 0, -1):
        while True:
            if not spanning_wikipages:
                break

            # pop one page
            wikipage = spanning_wikipages.pop(0)

            current_title = wikipage.title
            print current_title
            # mention_graph.add_node(current_title)

            # mm for "most mentioned"
            mm_link_counts, alias = most_mentioned_wikilinks(wikipage)

            mm_links = [m[0] for m in mm_link_counts if m[1] > least_mention]
            # mm_counts = [m[1] for m in mm_link_counts]

            mention_graph.add_nodes_from(nodes=mm_links, depth=depth)

            mention_edges = [(current_title, m[0], m[1]) for m in
                             mm_link_counts]
            mention_graph.add_weighted_edges_from(mention_edges)

            # branch out from the key mentioned terms, and add them to the graph
            if depth > 1:
                key_mention_terms = [
                    m[0] for m in mm_link_counts if m[1] > least_mention]
                key_mention_terms = key_mention_terms[:5]
                print key_mention_terms
                next_depth_wikipages.extend(
                    [WikipediaWrapper.page(t) for t in key_mention_terms])

        spanning_wikipages = list(next_depth_wikipages)
        next_depth_wikipages = []

    low_d_nodes = [node for node, degree in mention_graph.degree().items() if
                   degree < 3]
    mention_graph.remove_nodes_from(low_d_nodes)
    print mention_graph.nodes()
    nx.draw_networkx(mention_graph, with_labels=True, prog='dot')
    plt.show()


def test(topic="Reinforcement learning"):
    page = WikipediaWrapper.page(topic)

    clusters = similar_concpet_by_clustering_bag_of_links_to_here(page)
    print clusters

    # referred_links, aliases = most_mentioned_wikilinks(page, with_count=True)
    # referring_links, aliases = similarly_covered_topics(page, with_count=True)
    # print referred_links
    # print referring_links



    # sparse_mention_spanning_graph(page)


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db')

    test()
    # test("Marketing Strategy")
