# coding=utf-8
__author__ = 'moonkey'

import re
from util import wikipedia
import random
import util.nlp_util
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import normalize
import networkx as nx
import numpy
import nltk
import os
from util.nlp_util import NlpUtil

QUESTION_TYPE_WHAT_IS = 'WHAT_IS'
QUESTION_TYPE_WHY_IS = 'WHY_IS'


def generate_question(prereq_tree):
    # wrong name: question_text should be question_stem or question_stem_text
    question_generated = generate_question_stem(prereq_tree)
    question_stem = question_generated['stem']
    correct_answer = question_generated['answer']

    question = {
        'topic': prereq_tree['wikipage'].title,
        'type': QUESTION_TYPE_WHAT_IS,
        'question_text': question_stem,
        'correct_answer': correct_answer
    }

    distractors = generate_distractors(prereq_tree)
    question['distractors'] = distractors

    return format_question(question)


def generate_question_stem(prereq_tree):
    question_sentences = question_sentence_generator(prereq_tree['wikipage'])

    question_generated = None

    logged_sentences = []
    for question_sent in question_sentences:
        try:
            logged_sentences.append(question_sent)
            question_generated = question_from_single_sentence(
                question_sent, prereq_tree['wikipage'].title)
            if question_generated['stem'] and question_generated['answer']:
                break
        except Exception:
            continue

    if not question_generated:
        raise ValueError("No question generated")
    return question_generated


def generate_distractors(prereq_tree):
    distractors = []
    for child in prereq_tree['children']:
        sentences = topic_mentioning_sentence_generator(child['wikipage'])
        distractor = None
        for sentence in sentences:
            distractor = distractor_from_single_sentence(sentence, child['wikipage'].title)
            if distractor:
                break

        if distractor:
            distractors.append(distractor)
            # distractor = return_what_is(child['wikipage'])
    return distractors


def topic_mentioning_sentence_generator(wikipage):
    content = wikipage.content
    nlutil = NlpUtil()
    sentences = nlutil.punkt_tokenize(content)

    # TODO:: filter sentences with the key word (stemming matching here, not later?)
    # return {"filtered": " ", original_topic_form:" "}

    # sentences = [s for s in sentences if wikipage.title.lower() in s.lower()]
    topic_re = re.compile(topic_regex(wikipage.title))
    # sentences = [s for s in sentences if topic_re.search(s)]

    for s in sentences:
        # if wikipage.title.lower() in s.lower():
        if topic_re.search(s):
            if '\n' not in s.strip('\n'):  # TODO:: see below
                yield s

                # TODO:: only take sentences from certain parts, ignore "reference" "external links" etc.
                # fast hack for wrongly tokenized sentence,
                # for example with section information "=== Tree bagging ===" in it
                # this should not occur for the well organized offline sentences
                # Also we should not give them all up, but preprocess them better before sentence tokenization
                # only take sentences from certain parts, ignore "reference" "external links" etc.


def rank_sentences_textrank(sentences):
    """
    TODO:: this may not necessarily be separated from getting topic_mentioning sentences
    :param sentences:
    :return:
    """
    stemmed_pair = [util.nlp_util.ProcessedText(text=sent) for sent in sentences]
    stemmed_sentences = [NlpUtil.untokenize(s.stemmed_tokens) for s in stemmed_pair]
    if len(stemmed_sentences) < 1:
        return None
    if type(stemmed_sentences[0]) is list:  # tokens to text
        stemmed_sentences = [' '.join(s) for s in stemmed_sentences]

    vect = CountVectorizer()
    bow_count_mtx = vect.fit_transform(stemmed_sentences)
    bow_count_mtx = bow_count_mtx.astype(float)

    # normalize bow vector by total counts
    # normed_matrix = normalize(bow_count_mtx, axis=1, norm='l1')
    # bow_count_mtx = normed_matrix

    # maybe try tf-idf or other distance.
    # vect = TfidfVectorizer(min_df=1)
    # tfidf_mtx = vect.fit_transform(stemmed_sentences)

    cos_sim_mtx = (bow_count_mtx * bow_count_mtx.T).A

    # form an undirected graph
    cos_sim_threshold = 0.1  # parameter to tune.
    G = nx.Graph(cos_sim_mtx)

    # do a few PageRank iteration
    pr = nx.pagerank(G, alpha=0.9)
    sorted_pr = sorted(pr, key=pr.get, reverse=True)

    top_sentences = []
    for r in range(0, 10):
        top_sentences.append(stemmed_pair[sorted_pr[r]])

    return top_sentences


def question_sentence_generator(wikipage):
    sentences = topic_mentioning_sentence_generator(wikipage)
    # sentences = rank_sentences_textrank(sentences)
    return sentences


def question_from_single_sentence(sentence, topic):
    # TODO:: the topic might be too redundant to match any sentence,
    # like "Short (finance)", inspect on this a little more.
    # Maybe just remove "(*)".

    parsed_sentence, matched_positions = extract_verbal_phrase(sentence, topic)
    if matched_positions:
        matched_pos = matched_positions[0]
        matched_VP = parsed_sentence[matched_pos]

        answer = NlpUtil.untokenize(matched_VP.leaves())
        parsed_sentence[matched_pos] = nltk.tree.ParentedTree.fromstring("(VP ________)")
        stem = NlpUtil.untokenize(parsed_sentence.leaves())

        print stem
        # TODO:: is this the effect of the parser?
        answer = NlpUtil.revert_penntreebank_character(answer)
        stem = NlpUtil.revert_penntreebank_character(stem)
    else:
        answer = None
        stem = None

    question_stem = {
        'stem': stem,
        'answer': answer
    }

    return question_stem


def distractor_from_single_sentence(sentence, topic):
    distractors = distractors_from_single_sentence(sentence, topic)
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


def distractors_from_single_sentence(sentence, topic):
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
            distractor = NlpUtil.untokenize(matched_VP.leaves())
            distractor = NlpUtil.revert_penntreebank_character(distractor)
            yield distractor


def topic_cleaning(topic=""):
    if not topic:
        return None
    # Remove the string inside the brackets like in "Intersection (set theory)"
    topic = re.sub(r'\([^)]*\)', '', topic)
    topic.strip(" ")

    return topic


def topic_regex(topic=""):
    topic = topic_cleaning(topic)

    # Separate linked terms to tokens, like in "Karush–Kuhn–Tucker conditions"
    topic = re.sub(r"[-–_]+", ' ', topic, re.UNICODE)  # note '-' is ascii while '–' is not

    topic_tokens = nltk.word_tokenize(topic)
    try:
        processed_topic_tokens = util.nlp_util.ProcessedText(topic_tokens)
        stemmed_tokens = processed_topic_tokens.stemmed_tokens
    except UnicodeDecodeError:  # non-ascii characters like in "L'Hôpital's rule"
        stemmed_tokens = topic_tokens
        # TODO:: deal with the
        # if directly code them with unicode(t,'utf-8'), it will not match the original ascii-coded string

    topic_reg = '.*'.join(stemmed_tokens)
    topic_reg = '(?i)' + topic_reg
    return topic_reg


def extract_verbal_phrase(sentence, topic):
    nlutil = NlpUtil()

    parsed_sentence = nlutil.parsing(sentence)

    # matching  certain patterns that are suitable for question generation.
    topic = topic_cleaning(topic)
    topic_tokens = nltk.word_tokenize(topic)


    # or_tokens = [[t, t.lower()] if not t.islower() else [t] for t in topic_tokens]
    # Stemmed topic tokens added
    # TODO:: add initials like KKT(hard) or GDP(easy)
    or_tokens = []
    processed_topic_tokens = util.nlp_util.ProcessedText(topic_tokens)
    pt = processed_topic_tokens
    for idx in range(0, len(topic_tokens)):
        original_token = pt.original_tokens[idx]
        stemmed_token = pt.stemmed_tokens[idx]

        or_token = [stemmed_token + "*"]
        # TODO:: (test) the following seems to be the same as the above line
        # if stemmed_token == original_token:
        # or_token = [stemmed_token + "*"]
        # else:
        # or_token = [original_token, stemmed_token + "*"]

        # if not original_token.islower():
        #     or_token += [t.lower() for t in or_token]

        or_tokens.append(or_token)
    # topic_word_nodes = ['(* << /' + "|".join(s) + "/)" for s in or_tokens]

    # TODO:: (test) easier way to match while ignoring the case
    topic_word_nodes = ['(* << i@/' + "|".join(s) + "/)" for s in or_tokens]

    topic_words_sequence = '( ' + ' .. '.join(topic_word_nodes) + ' )'
    # for topic "A B C", "." would result in "A.B.C" which means A are directly followed by both B and C, which is false,
    # change into "..",

    # ###
    # only root sentence NP considered
    topic_NP = '/NP*/ << ' + topic_words_sequence + ' > (S > ROOT)'

    print topic_NP
    # for them to be sisters, should be better than "VP , NP"
    following_VP = 'VP $,, (' + topic_NP + ')'

    match_pattern = following_VP

    matched_positions = nlutil.tgrep_positions(parsed_sentence, match_pattern)

    return parsed_sentence, matched_positions


def format_question(question):
    possible_answers = [{'text': question['correct_answer'], 'correct': True}]

    for d in question['distractors']:
        possible_answers.append({'text': d, 'correct': False})

    random.shuffle(possible_answers)
    formated_question = {
        'topic': question['topic'],
        'question_text': question['question_text'],
        'choices': possible_answers,
        'type': question['type']
    }
    return formated_question