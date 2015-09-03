__author__ = 'moonkey'

from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
from autoassess.diagnose.util.quesgen_util import topic_regex, \
    match_noun_phrase, topic_remove_bracket
from autoassess.diagnose.util.NLPU.preprocess import ProcessUtil

import nltk
import sys
import re


def generate_item_question_stem(
        topic, topic_aliases, wikipage,
        sentence_black_list=list(), verbose=True):
    """

    :param topic:
    :param topic_aliases:
    :param wikipage:
    :param sentence_black_list: sentence might have been used
    to generate question for another item, so they should not be reused.
    :param verbose:
    :return:
    """

    # match to get the sentences
    question_sentences = item_question_sentence_generator(
        topic, topic_aliases, wikipage)

    # generate the questions:
    question_generated = None
    for question_sent in question_sentences:
        if question_sent in sentence_black_list:
            continue
        try:
            question_generated = item_question_from_single_sentence(
                topic, topic_aliases, sentence=question_sent
            )
            if not question_generated['answer'] and question_generated['stem']:
                question_generated = item_question_from_single_sentence(
                    topic, topic_aliases, sentence=question_sent)

            if question_generated['answer'] and question_generated['stem']:
                break
        except Exception as e:
            if verbose:
                print >> sys.stderr, e
            continue

    if not question_generated:
        raise ValueError("No question generated.")
    return question_generated


def item_question_sentence_generator(topic, topics_aliases, wikipage):
    sentences = WikipediaWrapper.article_sentences(wikipage)

    quiz_topic_re = re.compile(topic_regex(wikipage.title))
    topic_re = re.compile(topic_regex(topic))

    for s in sentences:
        # if quiz_topic_re.search(s):
        #     continue
        if topic_re.search(s, re.IGNORECASE):
            yield s
        if topic.lower() in s.lower():
            yield s
        else:
            for al in topics_aliases:
                if al in s:
                    yield s
                    break


def item_question_from_single_sentence(topic, topic_aliases, sentence):
    parsed_sentence, matched_positions = match_noun_phrase(
        sentence, topic, topic_aliases=topic_aliases)

    if len(matched_positions) > 1:
        print matched_positions
    if matched_positions and len(matched_positions) >= 1:
        # TODO:: be careful, there might be multiple matched NPs

        matched_pos = matched_positions[-1]
        matched_np = parsed_sentence[matched_pos]

        answer = ProcessUtil.untokenize(matched_np.leaves())

        # copy.copy() is not need here
        # original_np = copy.copy(parsed_sentence[matched_pos])
        original_np = parsed_sentence[matched_pos]
        parsed_sentence[matched_pos] = nltk.tree.ParentedTree.fromstring(
            "(NP ________)")
        stem = ProcessUtil.untokenize(parsed_sentence.leaves())
        parsed_sentence[matched_pos] = original_np

        answer = ProcessUtil.revert_penntreebank_symbols(answer)
        stem = ProcessUtil.revert_penntreebank_symbols(stem)

        # tenses are not need here not like in descriptive questions
    else:
        answer = None
        stem = None

    question_stem = {
        'answer': answer,
        'stem': stem,
        'original_sentence': sentence
    }

    return question_stem

#
# def item_question_from_single_sentence_NPExtractor(topic, topic_aliases,
# sentence):
#     process_util = ProcessUtil()
#
#     answer = None
#
#     # [First] try matching non phrase
#     noun_phrases = process_util.np_trunking(sentence)
#     matching_np = None
#     matching_alias = None
#     for np in noun_phrases:
#         for al in topic_aliases:
#             if al in noun_phrases:
#                 matching_np = np
#                 matching_alias = al
#                 break
#
#     if matching_alias and matching_np:
#         answer = matching_np
#     else:
#         # [Second] try matching single nouns,
#         # if not contained as a (part of a) np
#         for al in topic_aliases:
#             if al.lower() in sentence.lower():
#                 start_pos = sentence.lower().find(al.lower())
#                 end_pos = start_pos + len(topic)
#                 for c_idx in range(end_pos, len(sentence)):
#                     if sentence[c_idx].isalnum():
#                         end_pos = c_idx
#                         answer = sentence[start_pos:end_pos]
#                         break
#                 break
#
#     # [Failed] if all does not work just return a None filled structure
#     if answer:
#         stem = sentence.replace(answer, '________')
#     else:
#         answer = None
#         stem = None
#
#     question_stem = {
#         'answer': answer,
#         'stem': stem,
#         'original_sentence': sentence
#     }
#
#     return question_stem
