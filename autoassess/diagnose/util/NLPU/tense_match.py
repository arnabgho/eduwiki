__author__ = 'moonkey'

import pattern
from collections import Counter
import nltk


def find_sentence_tenses(sentence_tree, vp_pos):
    verbal_tree = sentence_tree[vp_pos]

    verb_node = find_verb_node_in_VP(verbal_tree=verbal_tree)
    tenses = None
    if verb_node and 'VB' in verb_node.label():
        sent_verb = verb_node[0]
        possible_tenses = pattern.en.tenses(sent_verb)
        # "was" can match both person 1 and 3
        if possible_tenses:
            tenses = heuristic_tenses(possible_tenses)
    return tenses


def heuristic_tenses(tenses_list):
    if len(tenses_list) == 1:
        return tenses_list[0]
    result = []
    for idx in range(0, len(tenses_list[0])):
        idx_elements = [t[idx] for t in tenses_list]
        count_list = Counter(idx_elements).most_common()
        max_count = count_list[0][1]
        max_elements = [c[0] for c in count_list if c[1] == max_count]
        if len(max_elements) == 1:
            heuristic_element = max_elements[0]
        else:
            heuristic_element = max(max_elements)
            if idx == 2:
                heuristic_element = 'plural'  # > 'singular'
        result.append(heuristic_element)

    # 'PRESENT'>'PAST'; 'person': 3>2>1>'None';
    return tuple(result)


def match_sentence_tense(verbal_tree, target_tenses):
    # TODO:: what if there are multiple verbs, connected by "and"/"or" etc.
    if not target_tenses:
        return verbal_tree
    if type(verbal_tree) == nltk.tree.Tree:
        verbal_tree = nltk.tree.ParentedTree.convert(verbal_tree)
    verb_node = find_verb_node_in_VP(verbal_tree=verbal_tree)
    if verb_node:
        original_verb = verb_node[0]
        conjugated_verb = pattern.en.conjugate(original_verb, target_tenses)
        if conjugated_verb != original_verb:
            verb_node[0] = conjugated_verb
            try:
                original_tenses = heuristic_tenses(
                    pattern.en.tenses(original_verb))
            except Exception as e:
                print e
                return verbal_tree
            target_sp_form = target_tenses[2]
            original_sp_form = original_tenses[2]
            if target_sp_form != original_sp_form \
                    and 'be' == pattern.en.lemma(original_verb):
                # find NPs in the same level
                parent_vp = verb_node.parent()
                if "VP" in parent_vp.label():
                    # skip the nodes before verb_node
                    verb_idx = len(parent_vp)
                    following_nps = []
                    for idx, child in enumerate(parent_vp):
                        if child == verb_node:
                            verb_idx = idx
                            continue
                        if idx < verb_idx:
                            continue
                        if "NP" in child.label():
                            following_nps.append(child)

                    # #####################################
                    def get_np_child(node):
                        if node is None or type(node) in [str, unicode]:
                            return None
                        for child in node:
                            if 'NP' or 'NN' in child.label():
                                return child
                        return None

                    def has_nn_child(node):
                        if node is None or type(node) in [str, unicode]:
                            return False
                        for child in node:
                            if 'NN' in child.label():
                                return True
                        return False

                    # #####################################

                    for np in following_nps:
                        major_np = np
                        while not has_nn_child(major_np):
                            major_np = get_np_child(major_np)
                            if major_np is None:
                                break
                        if major_np:
                            to_remove = []
                            np_changed = False
                            for child in reversed(major_np):
                                if 'DT' == child.label() \
                                        and child[0] is not 'the' \
                                        and target_sp_form == 'plural':
                                    to_remove.append(child)
                                if 'NN' in child.label() \
                                        or 'CD' in child.label():
                                    # TODO:: deal with the work
                                    # TODO:: add articles or determines?
                                    if not np_changed:
                                        if target_sp_form == 'plural':
                                            child[0] = pattern.en.pluralize(
                                                child[0])
                                        else:
                                            child[0] = pattern.en.singularize(
                                                child[0])
                                        # the last noun is replace, job done
                                        np_changed = True

                            for t in to_remove:
                                major_np.remove(t)

    return verbal_tree


def find_verb_node_in_VP(verbal_tree, priority='first'):
    """
    @:param priority: 'first' for Verb or MD whichever to be morphed,
    'exact_verb' for the exact Verb [Not implemented]
    @return: the VB or the MD, whichever to be morphed
    """

    if type(verbal_tree) is str:
        return None
    verb_node = verbal_tree

    while type(verb_node[0]) is not str and 'VP' in verb_node.label():
        # TODO:: this while loop is basically nonsense,
        # as basically only 'VB*' can be the 0th child of 'VP'
        verb_node = verb_node[0]

    # TODO:: may be write this in a for loop??
    if 'MD' in verb_node.label():
        return verb_node
        # TODO:: can/MD do/VB
    if 'VB' in verb_node.label():
        return verb_node
    else:
        return None


# def morphify(word, org_pos, target_pos):
# """
# morph a word based on rules
# http://stackoverflow.com/questions/27852969
# /how-to-list-all-the-forms-of-a-word-using-nltk-in-python