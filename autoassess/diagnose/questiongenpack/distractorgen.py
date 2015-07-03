from ..util.quesgen_util import *


def generate_distractors_from_prereqs(prereq_tree, tenses=[]):
    distractors = []
    for child in prereq_tree['children']:
        sentences = topic_mentioning_sentence_generator(child['wikipage'])
        distractor = None
        for sentence in sentences:
            distractor = distractor_from_single_sentence(sentence, child['wikipage'].title, tenses)
            if distractor:
                break

        if distractor:
            distractors.append(distractor)
            # distractor = return_what_is(child['wikipage'])
    return distractors


def generate_distractors_same_categories(wikipage):
    # TODO::
    # wikipage = wikipedia.page()
    # cats = wikipage.categories
    # wikipedia.page()
    pass


def distractor_from_single_sentence(sentence, topic, tenses=[]):
    distractors = distractors_from_single_sentence(sentence, topic, tenses)
    if distractors:
        for distractor in distractors:
            if is_heuristically_good_distractor(distractor):
                return distractor
    return None


def is_heuristically_good_distractor(distractor):
    """
    Token numbers > 5,
    :param distractor: distractor phrase
    :return: bool
    """
    is_good_distractor = None
    tokens = nltk.word_tokenize(distractor)
    if len(tokens) < 5:
        is_good_distractor = False
    else:
        is_good_distractor = True

    return is_good_distractor


def distractors_from_single_sentence(sentence, topic, tenses=[]):
    """
    :param sentence:
    :param topic:
    :return:
    """
    parsed_sentence, matched_positions = extract_verbal_phrase(sentence, topic)
    if matched_positions:
        # distractors = []
        for matched_pos in matched_positions:
            # matched_pos = matched_positions[0]
            matched_VP = parsed_sentence[matched_pos]
            # match tenses here:
            if tenses:
                matched_VP = NlpUtil.match_sentence_tense(matched_VP, tenses)

            distractor = NlpUtil.untokenize(matched_VP.leaves())
            distractor = NlpUtil.revert_penntreebank_symbols(distractor)

            yield distractor