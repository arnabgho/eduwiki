__author__ = 'moonkey'

import re
import wikipedia
import random
import util.nlp_util
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import normalize
import networkx as nx
import numpy


QUESTION_TYPE_WHAT_IS = 'WHAT_IS'
QUESTION_TYPE_WHY_IS = 'WHY_IS'


def generate_question(prereq_tree):
    # wrong name: question_text should be question_stem or question_stem_text
    question_text, correct_answer = question_stem(prereq_tree)
    question = {
        'topic': prereq_tree['wikipage'].title,
        'type': QUESTION_TYPE_WHAT_IS,
        'question_text': question_text,
        'correct_answer': correct_answer
    }

    distractors = []
    for child in prereq_tree['children']:
        distractor = return_what_is(child['wikipage'])
        distractors.append(distractor)

    question['distractors'] = distractors

    return format_question(question)


def get_question_sentence(wikipage):
    content = wikipage.content
    nlutil = util.nlp_util.NlUtil()
    sentences = nlutil.punkt_tokenize(content)

    # TODO:: (somewhere later) filter sentences with the key word (stemming matching?)
    sentences = [s for s in sentences if wikipage.title.lower() in s.lower()]

    stemmed_pair = [util.nlp_util.StemmedText(text=sent) for sent in sentences]
    stemmed_sentences = [s.stemmed for s in stemmed_pair]
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


def question_from_single_sentence(sentence):
    nlutil = util.nlp_util.NlUtil()
    tagged = nlutil.pos_tag(sentence)

    # TODO:: to be continued here
    # TODO:: to be continued here
    # TODO:: to be continued here

    question_stem = {
        'stem': sentence,
        'answer': None
    }
    return question_stem


def question_stem(prereq_tree):
    question_sentences = get_question_sentence(prereq_tree['wikipage'])

    # TODO:: to be continued here
    # TODO:: to be continued here
    # TODO:: to be continued here
    question_stems = []
    for question_sent in question_sentences:
        question_stem = question_from_single_sentence(question_sent)
        if question_stem:
            question_stems.append(question_stem)

    question_text = "What is " + prereq_tree['wikipage'].title
    correct_answer = return_what_is(wikipage=prereq_tree['wikipage'])
    return question_text, correct_answer


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


def return_what_is(wikipage):
    """
    "<topic>\s[^\.](is|was)([^\.])+\." or None (if no matches)
    :return: first mention in article of the following regex
    """
    # Optimize over the regular expresson


    # TODO:: the number 5 might be hacked for a specific topic,

    topic = wikipage.title
    # figure out what the regex is doing and make it general
    regex_str1 = \
        '(' + topic[:5] + '(' + topic[5:] + ')?' + '|' + '(' + topic[:len(topic) - 5] + ')?' + topic[len(topic) - 5:] \
        + ')'
    regex_str2 = '(\s[^\.]*(is|was|can be regarded as)|[^,\.]{,15}?,)\s([^\.]+)\.(?=\s)'
    regex_str = regex_str1 + regex_str2
    # (abcde(fghijklmnopqrst)?|(abcdefghijklmno)?pqrst)
    # (\s[^\.]*(is|was|can be regarded as)|[^,\.]{,15}?,)\s([^\.]+)\.(?=\s)

    what_is_pattern = re.compile(regex_str, re.IGNORECASE)
    mentions = re.findall(what_is_pattern, wikipage.content)

    if not mentions:
        what_is = "can't find a good description"
    else:
        what_is = mentions[0][5]
        what_is = re.sub(r'.*\sis\s+(.*)$', r'\1', what_is)

    return what_is