__author__ = 'moonkey'

from ...util.quesgen_util import *


def distractor_from_single_sentence(sentence, topic, tenses=[]):
    distractors = distractors_from_single_sentence(sentence, topic, tenses)
    if distractors:
        for distractor in distractors:
            if is_heuristically_good_distractor(distractor):
                return distractor
    return None


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


def is_heuristically_good_distractor(distractor):
    """
    Token numbers > 5,
    :param distractor: distractor phrase
    :return: bool
    """
    is_good_distractor = True
    tokens = nltk.word_tokenize(distractor)
    if len(tokens) < 5:
        is_good_distractor = False
    return is_good_distractor