__author__ = 'moonkey'

import wikipedia
import re
import search_wikipage

def find_direct_prereq(wikipage, num):
    """
    Based on the guess that the first few terms with wikipedia link
    will turn out to be background knowledge
    :param num:
    :return:
    """
    # TODO:: the heuristic actually needs to be changed
    return linked_wiki_terms(wikipage, num)


def linked_wiki_terms(wikipage, num):
    """
    :param num: the number of linked texts to return
    :return: list(strings), the first few texts that have a wikipedia hyper link
    """
    # TODO: use the page._links to match and find the first few links, maybe?
    w_text = wikipage.wikitext()
    wikilink_rx = re.compile(r'\[\[([^|\]]*\|)?([^\]]+)\]\]')
    link_array = []
    for m in wikilink_rx.finditer(w_text):
        if len(link_array) > num:
            break
        if m.group(1) is not None:
            if "Image" in m.group(1) or "Template" in m.group(1) or \
                            "File" in m.group(1):
                continue
            link_array.append(m.group(1)[:-1])
        else:
            if "Image" in m.group(2) or "Template" in m.group(2) or \
                            "File" in m.group(2):
                continue
            link_array.append(m.group(2))
    return link_array


def find_prereq_tree(topic, depth=1, num_prereq=3):
    # find exact page of the topic
    # This only happens at the root node, because all the rest are wiki links
    wikipage = search_wikipage.get_wikipage(topic)

    # set a max depth and branching factor as a fail-safe
    max_prereq_tree_depth = 6
    max_num_prereq_per_node = 6
    depth = min(depth, max_prereq_tree_depth)
    num_prereq = min(num_prereq, max_num_prereq_per_node)

    # get the topic and the names of its prereq links
    prereq_names = find_direct_prereq(wikipage, num_prereq)

    # create a knowledge tree (dict) which will be recursively built
    prereqs = []

    # run for num_children if depth left
    if depth != 0:
        for j in range(0, num_prereq):
            prereq_subtree = find_prereq_tree(prereq_names[j], depth=depth - 1, num_prereq=num_prereq)
            prereqs.append(prereq_subtree)

    # assemble the tree and return it
    prereq_tree = {
        'wikipage': wikipage,
        'children': prereqs}
    return prereq_tree