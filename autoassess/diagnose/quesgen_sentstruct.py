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
    question_sentences = get_question_sentences(prereq_tree['wikipage'])

    question_generated = None

    for question_sent in question_sentences:
        try:
            question_generated = question_from_single_sentence(
                question_sent, prereq_tree['wikipage'].title)
            if question_generated['stem'] and question_generated['answer']:
                break
        except Exception:
            continue

    return question_generated


def generate_distractors(prereq_tree):
    distractors = []
    for child in prereq_tree['children']:
        sentences = get_topic_mentioning_sentences(child['wikipage'])
        distractor = None
        for sentence in sentences:
            distractor = distractor_from_single_sentence(sentence, child['wikipage'].title)
            if distractor:
                break

        if distractor:
            distractors.append(distractor)
            # distractor = return_what_is(child['wikipage'])
    return distractors


def get_topic_mentioning_sentences(wikipage):
    content = wikipage.content
    nlutil = NlpUtil()
    sentences = nlutil.punkt_tokenize(content)

    # TODO::move this part: (somewhere later)
    # filter sentences with the key word (stemming matching?)
    sentences = [s for s in sentences if wikipage.title.lower() in s.lower()]

    # fast hack for wrongly tokenized sentence, for example with section information "=== Tree bagging ===" in it
    # TODO::
    # this should not occur for the well organized offline sentences
    # Also we should not give them all up, but preprocess them better before sentence tokenization
    # only take sentences from certain parts, ignore "reference" "external links" etc.
    sentences = [s for s in sentences if '\n' not in s.strip('\n')]

    # for temporary testing
    sentences = sentences[1:3]
    return sentences


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


def get_question_sentences(wikipage):
    sentences = get_topic_mentioning_sentences(wikipage)
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
    # TODO::maybe using yield ???!!!
    parsed_sentence, matched_positions = extract_verbal_phrase(sentence, topic)
    if matched_positions:
        distractors = []
        for matched_pos in matched_positions:
            # matched_pos = matched_positions[0]
            matched_VP = parsed_sentence[matched_pos]
            distractor = NlpUtil.untokenize(matched_VP.leaves())
            distractors.append(distractor)
        return distractors
    else:
        return None


def extract_verbal_phrase(sentence, topic):
    nlutil = NlpUtil()

    parsed_sentence = nlutil.parsing(sentence)

    # matching  certain patterns that are suitable for question generation.
    topic_tokens = nltk.word_tokenize(topic)

    # ##### Examples (topic = "Reinforcement learning")
    # topic_words_sequence_simple = ' << Reinforcement|reinforcement << learning)'
    # the next line enforces the words to be continuous
    # topic_words_sequence = '((* << Reinforcement|reinforcement) . (* << learning))'
    # TODO:: maybe match stemmed text, for example "statistical hypothesis test"/"statistical hypothesis testing"


    # or_tokens = [[t, t.lower()] if not t.islower() else [t] for t in topic_tokens]
    # Stemmed topic tokens added
    # TODO:: add initials
    or_tokens = []
    processed_topic_tokens = util.nlp_util.ProcessedText(topic_tokens)
    pt = processed_topic_tokens
    for idx in range(0, len(topic_tokens)):
        original_token = pt.original_tokens[idx]
        stemmed_token = pt.stemmed_tokens[idx]
        if stemmed_token == original_token:
            or_token = [original_token + "*"]
        else:
            or_token = [original_token, stemmed_token + "*"]

        if not original_token.islower():
            or_token += [t.lower() for t in or_token]

        or_tokens.append(or_token)

    topic_word_nodes = ['(* << /' + "|".join(s) + "/)" for s in or_tokens]
    topic_words_sequence = '( ' + ' . '.join(topic_word_nodes) + ' )'

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


def test_sentence_parsing():
    sentence = "Reinforcement learning is an area of machine learning inspired by behaviorist psychology, concerned" \
               " with how software agents ought to take actions in an environment so as to maximize some notion of" \
               " cumulative reward. "
    question = question_from_single_sentence(sentence, 'Reinforcement learning')
    print "===========Generated Question============="
    print "Stem: " + str(question['stem'])
    print "Answer: " + str(question['answer'])


if __name__ == "__main__":
    test_sentence_parsing()