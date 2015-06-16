__author__ = 'moonkey'

from util import wikipedia
import re
import search_wikipage


def direct_prereq_generator(wikipage, num):
    """
    Based on the guess that the first few terms with wikipedia link
    will turn out to be background knowledge
    :param num:
    :return:
    """
    # TODO:: the heuristic actually needs to be changed
    # for example, we can measure the similarity (BOW)
    # return content_categories(wikipage, num)
    return linked_wiki_term_generator(wikipage, num)


def content_categories(wikipage, num):
    """
    request categories, and remove the hidden/tracking categories which are not content categories
    :param wikipage:
    :param num:
    :return:
    """
    # TODO:: http://www.mediawiki.org/wiki/API:Categorymembers
    categories = wikipage.content_categories
    print categories
    prereqs = []
    for cat in categories:
        if 'articles that' in cat.lower():
            continue
        prereqs.append(cat)
    return prereqs


def linked_wiki_term_generator(wikipage, num):
    """
    :param num: the number of linked texts to return
    :return: list(strings), the first few texts that have a wikipedia hyper link
    """
    # TODO:: use the iwlinks to get the first few links!
    # internal_links = wikipage.internal_links
    w_text = wikipage.wikitext()
    wikilink_rx = re.compile(r'\[\[([^|\]]*\|)?([^\]]+)\]\]')
    # link_array = []
    for m in wikilink_rx.finditer(w_text):
        # if len(link_array) >= num:
        #     break
        if m.group(1) is not None:
            if "Image" in m.group(1) or "Template" in m.group(1) or \
                            "File" in m.group(1):
                continue
            link = m.group(1)[:-1]
            yield link
        else:
            if "Image" in m.group(2) or "Template" in m.group(2) or \
                            "File" in m.group(2):
                continue
            link = m.group(2)
            yield link
    # return link_array


def find_prereq_tree(topic, depth=1, num_prereq=3):
    # find the exact page of the topic
    # This only happens at the root node, because all the rest are wiki links
    if topic.startswith("wikt") or topic.startswith("wikitionary"):
        raise ValueError("wikitionary terms not supported")
    elif '#' in topic:
        # for links containing section like "Euclidean group#Direct_and_indirect_isometries"
        topic = topic[0:topic.find('#')]


    wikipage = search_wikipage.get_wikipage(topic)

    # set a max depth and branching factor as a fail-safe
    max_prereq_tree_depth = 6
    max_num_prereq_per_node = 6
    depth = min(depth, max_prereq_tree_depth)
    num_prereq = min(num_prereq, max_num_prereq_per_node)

    # get the topic and the names of its prereq links
    prereq_names = direct_prereq_generator(wikipage, num_prereq)

    # create a knowledge tree (dict) which will be recursively built
    prereqs = []

    # run for num_children if depth left
    if depth != 0:
        for pn in prereq_names:
            if len(prereqs) >= num_prereq:
                break
            try:
                prereq_subtree = find_prereq_tree(pn, depth=depth - 1, num_prereq=num_prereq)
            except Exception:
                continue
            prereqs.append(prereq_subtree)

    # assemble the tree and return it
    prereq_tree = {
        'wikipage': wikipage,
        'children': prereqs
    }
    return prereq_tree


def prereq_stat(wikipage, terms):
    """
    Get some stats of certain terms in a wikipage,
    to get sense of the prerequisites
    :param wikipage:
    :param terms:
    :return:
    """
    wikitext = wikipage.wikitext()
    counts = {}
    star_pos = {}

    suggested_terms = []
    for t in terms:
        results, suggestion = wikipedia.search(t, results=1, suggestion=True)
        suggested_term = suggestion or results[0]
        suggested_terms.append(suggested_term)
    terms = suggested_terms

    for t in terms:
        star_pos[t] = wikitext.index(t)
    for t in enumerate(terms):
        if star_pos[t] == -1:
            continue
        counts[t] = wikitext.count(t)

    stats = {
        'start_pos': star_pos,
        'counts': counts,
    }

    return stats