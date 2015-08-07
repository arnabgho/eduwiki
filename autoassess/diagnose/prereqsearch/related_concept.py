__author__ = 'moonkey'

from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from autoassess.diagnose.util.wikipedia_util import page_titles_of_same_category
from autoassess.diagnose.util.wikipedia_util import filter_wikilink
from autoassess.diagnose.util.wikipedia_util import count_rank
from autoassess.diagnose.util.quesgen_util import topic_remove_bracket
import re
import sys
import operator
import networkx as nx
import matplotlib.pyplot as plt


def related_term_generator(wikipage):
    return wikipage


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

    wikilinks = wikipage.wikilinks
    for idx, l in enumerate(wikilinks):
        wikilinks[idx].target = filter_wikilink(l.target, ignore_cat=True)

    wikilinks = [l for l in wikilinks if l.target is not None]

    for l in wikilinks:
        if l.target not in alias:
            alias[l.target] = set()

        # alias[l.target].add(l.target)
        alias[l.target].add(topic_remove_bracket(l.target))
        if l.text is not None:
            alias[l.target].add(l.text)

        # add abbreviations to alias
        # the abbreviations should appear in "(xxx)" following the link term
        to_add_als = []
        for al in alias[l.target]:
            abbr_pattern = "" + re.escape(al) + " \(([\w-]+?)\)"  # K-K-T???

            abbr_matches = re.search(
                abbr_pattern, wikipage.content, re.IGNORECASE)
            if not abbr_matches:
                continue
            abbr_match = abbr_matches.group(1)
            if re.search('.*'.join(abbr_match), al, re.IGNORECASE):
                to_add_als.append(abbr_match)
                # print >> sys.stderr, abbr_match, l.target
        for al in to_add_als:
            alias[l.target].add(al)

    # get numbers of mention of each link target and their alias
    term_count = {}
    for l in alias:
        term_count[l] = 0
        for al in alias[l]:
            al_pattern = '\W' + re.escape(al)
            # + '\W'  # "s" for plurals may appear
            term_count[l] += len(re.findall(
                al_pattern, wikipage.content, re.IGNORECASE))

    # TODO::
    # topics within quotes, meaning bold font, should be treated
    # as more important than others.
    # But they are not necessarily wikilinks
    # generate questions within the article?

    # get high number mention topics
    most_mentioned = sorted(
        term_count.items(), key=operator.itemgetter(1), reverse=True)

    if not with_count:
        most_mentioned = [m[0] for m in most_mentioned]

    return most_mentioned, alias


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
    sparse_mention_spanning_graph(page)


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db')

    test("Ellipse")