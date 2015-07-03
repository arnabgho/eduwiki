# coding=utf-8
__author__ = 'moonkey'

import re
import random
import nlp_util
import nltk
from nlp_util import NlpUtil
import sys
from wikipedia_util import WikipediaWrapper


def topic_cleaning(topic=""):
    if not topic:
        return None
    # Remove the string inside the brackets like in "Intersection (set theory)"
    topic = re.sub(r'\([^)]*\)', '', topic)
    topic.strip(" ")

    return topic


def topic_regex(topic=""):
    """
    only for topic mentioning sentence selection, as the syntax of
    tree matching is different.
    :param topic:
    :return:
    """
    topic = topic_cleaning(topic)

    # Separate linked terms to tokens, like in "Karush–Kuhn–Tucker conditions"
    topic = re.sub(r"[-–_]+", ' ', topic, re.UNICODE)
    # note '-' is ascii while '–' is not

    topic_tokens = nltk.word_tokenize(topic)
    try:
        processed_topic_tokens = nlp_util.ProcessedText(topic_tokens)
        stemmed_tokens = processed_topic_tokens.stemmed_tokens
        or_tokens = []
        for idx in range(0, len(stemmed_tokens)):
            or_token = \
                '(' + processed_topic_tokens.stemmed_tokens[idx] + '|' \
                + processed_topic_tokens.original_tokens[idx] + ')'
            or_tokens.append(or_token)
    except UnicodeDecodeError:  # non-ascii characters in "L'Hôpital's rule"
        or_tokens = topic_tokens
        # TODO:: deal with the
        # if directly code them with unicode(t,'utf-8'),
        # it will not match the original ascii-coded string

    topic_reg = '.*'.join(or_tokens)
    topic_reg = '(?i)' + topic_reg
    return topic_reg


def extract_verbal_phrase(sentence, topic):
    nlutil = NlpUtil()

    # print >> sys.stderr, "pre nlutil.parsing()"
    parsed_sentence = nlutil.parsing(sentence)
    if not parsed_sentence:
        # print >> sys.stderr, "no parsed tree returned for extracting VP."
        return None, None

    # print >> sys.stderr, "parsed_sentence" + str(parsed_sentence)
    # matching  certain patterns that are suitable for question generation.
    topic = topic_cleaning(topic)
    topic_tokens = nltk.word_tokenize(topic)


    # or_tokens = [[t, t.lower()] if not t.islower() else [t]
    # for t in topic_tokens]
    # Stemmed topic tokens added
    # TODO:: add initials like KKT(hard) or GDP(easy)
    or_tokens = []
    processed_topic_tokens = nlp_util.ProcessedText(topic_tokens)
    pt = processed_topic_tokens
    # print >> sys.stderr, "processed_tokens:" + str(pt.stemmed_tokens)
    for idx in range(0, len(topic_tokens)):
        original_token = pt.original_tokens[idx]
        stemmed_token = pt.stemmed_tokens[idx]

        or_token = [stemmed_token + "*"]
        # TODO:: (test) the following seems to be the same as the above line
        if stemmed_token in original_token:
            or_token = [stemmed_token + "*"]
        else:
            or_token = [original_token, stemmed_token + "*"]

        if not original_token.islower():
            or_token += [t.lower() for t in or_token]

        or_tokens.append(or_token)
    # topic_word_nodes = ['(* << /' + "|".join(s) + "/)" for s in or_tokens]

    # TODO:: (test) easier way to match while ignoring the case
    topic_word_nodes = ['(* << i@/' + "|".join(s) + "/)" for s in or_tokens]

    topic_words_sequence = '( ' + ' .. '.join(topic_word_nodes) + ' )'
    # for topic "A B C", "." would result in "A.B.C" which means A
    # are directly followed by both B and C, which is false,
    # change into "..",

    # ###
    # only root sentence NP considered
    topic_NP = '/NP*/ << ' + topic_words_sequence + ' > (S > ROOT)'

    print >> sys.stderr, topic_NP
    # for them to be sisters, should be better than "VP , NP"
    following_VP = 'VP $,, (' + topic_NP + ')'

    match_pattern = following_VP

    matched_positions = nlutil.tgrep_positions(parsed_sentence, match_pattern)

    return parsed_sentence, matched_positions


def topic_mentioning_sentence_generator(wikipage):
    sentences = WikipediaWrapper.article_sentences(wikipage)
    topic_re = re.compile(topic_regex(wikipage.title))
    # sentences = [s for s in sentences if topic_re.search(s)]

    for s in sentences:
        if topic_re.search(s):
            if '\n' not in s.strip('\n'):
                yield s