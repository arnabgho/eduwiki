__author__ = 'moonkey'

# from ...util.quesgen_util import *
from autoassess.diagnose.util.quesgen_util import *
from autoassess.diagnose.util.NLPU import tense_match


def distractor_from_single_sentence(
        sentence, topic, tenses=[], original_topic=None):
    distractors = distractors_from_single_sentence(sentence, topic, tenses)
    if distractors:
        for distractor in distractors:
            if is_heuristically_good_distractor(
                    distractor, original_topic=original_topic):
                return distractor
    return None


def distractors_from_single_sentence(sentence, topic, tenses=[]):
    """
    :param sentence:
    :param topic:
    :return: usually there is only one matched positions, thus one distractors,
            in rare cases, there might be multiple distractors
    """
    parsed_sentence, matched_positions = match_verbal_phrase(sentence, topic)
    if matched_positions:
        # distractors = []
        for matched_pos in matched_positions:
            # matched_pos = matched_positions[0]
            matched_vp = parsed_sentence[matched_pos]
            # match tenses here:
            if tenses:
                matched_vp = tense_match.match_sentence_tense(
                    matched_vp, tenses)

            distractor = ProcessUtil.untokenize(matched_vp.leaves())
            distractor = ProcessUtil.revert_penntreebank_symbols(distractor)

            yield distractor


def is_heuristically_good_distractor(distractor, original_topic=None):
    """
    Token numbers > 5,
    :param distractor: distractor phrase
    :return: bool
    """
    is_good_distractor = True
    tokens = nltk.word_tokenize(distractor)
    if len(tokens) < 5:
        is_good_distractor = False

    if original_topic:
        original_topic_re = re.compile(topic_regex(original_topic))
        if original_topic_re.search(distractor):
            is_good_distractor = False

    return is_good_distractor