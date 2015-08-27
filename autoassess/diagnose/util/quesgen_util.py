# coding=utf-8

__author__ = 'moonkey'

from autoassess.diagnose.util.NLPU.preprocess import ProcessUtil, ProcessedText
import re
import nltk
import sys
from wikipedia_util import WikipediaWrapper


def topic_remove_bracket(topic=""):
    if not topic:
        return None
    # Remove the string inside the brackets like in "Intersection (set theory)"
    topic = re.sub(r'\([^)]*\)', '', topic)
    topic = topic.strip(" ")
    return topic


def escape_slash(text):
    text = text.replace("/", "\/")
    # text = re.escape(text)
    return text


def topic_regex(topic=""):
    """
    only for topic mentioning sentence selection, as the syntax of
    tree matching is different.
    :param topic:
    :return:
    """
    topic = topic_remove_bracket(topic)

    # 1) Separate linked terms to tokens, like "Karush–Kuhn–Tucker conditions"
    # 2) remove symbols in the title
    topic = re.sub(r"[-–_!@#\$%\^&\*\?:;/\\]+", ' ', topic, re.UNICODE)
    # note '-' is ascii while '–' is not, though they look the same.



    topic_tokens = nltk.word_tokenize(topic)
    try:
        processed_topic_tokens = ProcessedText(topic_tokens)
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


def match_noun_phrase(sentence, topic, topic_aliases=None, verbose=True):
    #TODO:: add aliases
    return match_key_phrase(
        sentence, topic, phrase_type='NP', verbose=verbose)


def match_verbal_phrase(sentence, topic, verbose=False):
    return match_key_phrase(
        sentence, topic, phrase_type='VP', verbose=verbose)


def match_key_phrase(sentence, topic, phrase_type='VP', verbose=False):
    process_util = ProcessUtil()

    # print >> sys.stderr, "pre process_util.parsing()"
    parsed_sentence = process_util.parsing(sentence)
    if not parsed_sentence:
        if verbose:
            print >> sys.stderr, "no parsed tree returned for extracting VP."
        return None, None

    if verbose:
        print >> sys.stderr, "parsed_sentence" + str(parsed_sentence)

    # matching  certain patterns that are suitable for question generation.
    topic = topic_remove_bracket(topic)
    # 1) Separate linked terms to tokens, like "Karush–Kuhn–Tucker conditions"
    # 2) remove symbols in the title
    topic = re.sub(r"[-–_!@#\$%\^&\*\?:;/\\]+", ' ', topic, re.UNICODE)
    # note '-' is ascii while '–' is not, though they look the same.

    topic = escape_slash(topic)
    topic_tokens = nltk.word_tokenize(topic)

    # or_tokens = [[t, t.lower()] if not t.islower() else [t]
    # for t in topic_tokens]
    # TODO:: add initials like KKT(hard) or GDP(easy)

    # TODO:: add aliases here !!!!!!!!!!!

    # to match tokens or their stemmed version
    or_tokens = []
    processed_topic_tokens = ProcessedText(topic_tokens)
    pt = processed_topic_tokens
    # print >> sys.stderr, "processed_tokens:" + str(pt.stemmed_tokens)
    for idx in range(0, len(topic_tokens)):
        original_token = pt.original_tokens[idx]
        stemmed_token = pt.stemmed_tokens[idx]

        # or_token = [stemmed_token + "*"]
        # the following is not the same as the above line
        # not true if there are cases where stemming is not only truncating
        if stemmed_token in original_token:
            or_token = [stemmed_token + "*"]
        else:
            or_token = [original_token, stemmed_token + "*"]

        # TODO:: (test) seems to be not useful, as we are using i@ later
        # if not original_token.islower():
        # or_token += [t.lower() for t in or_token]

        or_tokens.append(or_token)

    # {DONE}:for topic "A B C", "." would result in "A.B.C" which means A
    # are directly followed by both B and C, which is false,
    # change into "..",

    # topic_word_nodes = ['(* << i@/' + "|".join(s) + "/)" for s in or_tokens]
    # topic_words_sequence = '( ' + ' .. '.join(topic_word_nodes) + ' )'
    # ###
    # only root sentence NP considered
    # topic_np = '/NP*/ << ' + topic_words_sequence + ' > (S > ROOT)'

    topic_word_nodes = ['<< i@/' + "|".join(s) + "/" for s in or_tokens]
    topic_words_sequence = ' '.join(topic_word_nodes)

    # ####################################################
    ######### Decide which node do we want here #########
    #####################################################

    topic_np = '/NP*/ ' + topic_words_sequence

    # only root sentence NP considered for VP extraction
    root_topic_np = topic_np + ' > (S > ROOT)'

    if verbose:
        print "Sentence:", sentence
    # for them to be sisters, should be better than "VP , NP"
    following_vp = 'VP $,, (' + root_topic_np + ')'

    if phrase_type == 'NP':
        match_pattern = topic_np
    elif phrase_type == 'VP':
        match_pattern = following_vp
    else:
        # default
        match_pattern = following_vp

    matched_positions = process_util.tgrep_positions(
        parsed_sentence,
        match_pattern)

    if verbose and not matched_positions:
        print >> sys.stderr, "No matched positions"
    return parsed_sentence, matched_positions


def topic_mentioning_sentence_generator(wikipage):
    sentences = WikipediaWrapper.article_sentences(wikipage)
    topic_re = re.compile(topic_regex(wikipage.title))
    # sentences = [s for s in sentences if topic_re.search(s)]

    for s in sentences:
        if topic_re.search(s):
            if '\n' not in s.strip('\n'):
                yield s