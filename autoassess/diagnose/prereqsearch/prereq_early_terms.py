__author__ = 'moonkey'

from ..util.wikipedia_util import WikipediaWrapper
from ..util.wikipedia_util import filter_wikilink


def direct_prereq_generator(wikipage):
    """
    Based on the guess that the first few terms with wikipedia link
    will turn out to be background knowledge
    :return:
    """
    return WikipediaWrapper.linked_terms(wikipage)


def find_prereq_tree(topic, depth, num_prereq=3):
    # find the exact page of the topic
    # This only happens at the root node, because all the rest are wiki links

    topic = filter_wikilink(topic)
    if not topic:
        return None
    wikipage = WikipediaWrapper.page(topic)

    # set a max depth and branching factor as a fail-safe
    max_prereq_tree_depth = 6
    max_num_prereq_per_node = 6
    depth = min(depth, max_prereq_tree_depth)
    num_prereq = min(num_prereq, max_num_prereq_per_node)

    # ### create a knowledge tree (dict) which will be recursively built ###
    prereqs = []

    # run for num_children if depth left
    if depth != 0:
        # get the topic and the names of its prereq links
        prereq_names = direct_prereq_generator(wikipage)
        for pn in prereq_names:
            if len(prereqs) >= num_prereq:
                break
            try:
                prereq_subtree = find_prereq_tree(
                    pn,
                    depth=depth - 1,
                    num_prereq=num_prereq)
            except Exception:
                continue
            prereqs.append(prereq_subtree)

    # assemble the tree and return it
    prereq_tree = {
        'wikipage': wikipage,
        'children': prereqs
    }
    return prereq_tree


    # def prereq_stat(wikipage, terms):
    # """
    #     Get some stats of certain terms in a wikipage,
    #     to get sense of the prerequisites
    #     :param wikipage:
    #     :param terms:
    #     :return:
    #     """
    #     wikitext = wikipage.wikitext
    #     counts = {}
    #     star_pos = {}
    #
    #     suggested_terms = []
    #     for t in terms:
    #         results, suggestion = WikipediaWrapper.search(
    #               t, results=1, suggestion=True)
    #         suggested_term = suggestion or results[0]
    #         suggested_terms.append(suggested_term)
    #     terms = suggested_terms
    #
    #     for t in terms:
    #         star_pos[t] = wikitext.index(t)
    #     for t in enumerate(terms):
    #         if star_pos[t] == -1:
    #             continue
    #         counts[t] = wikitext.count(t)
    #
    #     stats = {
    #         'start_pos': star_pos,
    #         'counts': counts,
    #     }
    #
    #     return stats