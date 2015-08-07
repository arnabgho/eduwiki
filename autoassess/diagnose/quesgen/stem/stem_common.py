from sklearn.feature_extraction.text import CountVectorizer
import networkx as nx
from autoassess.diagnose.util.quesgen_util import *


def rank_sentences_textrank(sentences):
    """
    TODO:: this may not necessarily be separated from getting topic_mentioning sentences
    :param sentences:
    :return:
    """
    stemmed_pair = [ProcessedText(text=sent) for sent in sentences]
    stemmed_sentences = [ProcessUtil.untokenize(s.stemmed_tokens) for s in
                         stemmed_pair]
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