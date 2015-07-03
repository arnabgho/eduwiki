__author__ = 'moonkey'

from ..util import nlp_util
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import normalize
import networkx as nx

from ..util.nlp_util import NlpUtil
from ..util.quesgen_util import *


def generate_question_stem(wikipage):
    question_sentences = question_sentence_generator(wikipage)

    question_generated = None

    # logged_sentences = []
    for question_sent in question_sentences:
        try:
            # logged_sentences.append(question_sent)
            # print >> sys.stderr, "question_sent:"+question_sent
            question_generated = question_from_single_sentence(
                question_sent, wikipage.title)
            if question_generated['stem'] and question_generated['answer']:
                break
        except Exception:
            continue

    if not question_generated:
        raise ValueError("No question generated")
    return question_generated


def lex_pagerank(sentences):
    """
    TODO:: this may not necessarily be separated from getting topic_mentioning sentences
    :param sentences:
    :return:
    """
    stemmed_pair = [nlp_util.ProcessedText(text=sent) for sent in sentences]
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
    # sentences = lex_pagerank(sentences)
    return sentences


def question_from_single_sentence(sentence, topic):
    # TODO:: the topic might be too redundant to match any sentence,
    # like "Short (finance)", inspect on this a little more.
    # Maybe just remove "(*)".

    parsed_sentence, matched_positions = extract_verbal_phrase(sentence, topic)
    # print >> sys.stderr, matched_positions
    if matched_positions:
        matched_pos = matched_positions[0]
        matched_VP = parsed_sentence[matched_pos]

        answer = NlpUtil.untokenize(matched_VP.leaves())

        orginal_verbal_phrase = parsed_sentence[matched_pos]
        parsed_sentence[matched_pos] = nltk.tree.ParentedTree.fromstring("(VP ________)")
        stem = NlpUtil.untokenize(parsed_sentence.leaves())

        parsed_sentence[matched_pos] = orginal_verbal_phrase

        answer = NlpUtil.revert_penntreebank_symbols(answer)
        stem = NlpUtil.revert_penntreebank_symbols(stem)

        # ######## To match the tenses of the question stem and the distractors
        tenses = NlpUtil.find_sentence_tenses(parsed_sentence, matched_pos)
    else:
        answer = None
        stem = None
        tenses = None

    question_stem = {
        'stem': stem,
        'answer': answer,
        'tenses': tenses,
    }

    return question_stem