from __future__ import division
from gensim.models.doc2vec import Doc2Vec
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

__author__ = 'moonkey'


def load_doc2vec():
    print "loading doc2vec model (may take a few minutes) ..."
    model = Doc2Vec.load_word2vec_format(
        "/opt/word2vec/GoogleNews-vectors-negative300.bin.gz",
        binary=True)
    return model


DOC2VEC_MODEL = None  # load_doc2vec()


def bow_sim(sent0, sent_list):
    cv = CountVectorizer()
    if type(sent_list) in [str, unicode]:
        sent_list = [sent_list]
    bow_mtx = cv.fit_transform([sent0] + sent_list)
    sim_mtx = bow_mtx[1:] * bow_mtx[0].transpose()
    sim_mtx = sim_mtx.transpose()
    if not 1 in sim_mtx.get_shape():
        raise AttributeError(
            "The sim_mtx should has only one column or only one row.")
    sim_list = sim_mtx.toarray().tolist()[0]
    for idx, sim in enumerate(sim_list):
        sim_list[idx] = sim / (len(sent_list[idx]) * len(sent0))
    return sim_list


def doc2vec_sim(sent0, sent_list):
    DOC2VEC_MODEL = load_doc2vec()

    doc2vec_model = DOC2VEC_MODEL
    # if not (sent0 and sent_list):
    # return None

    # just in case the 2nd parameter is not a list as expected
    if type(sent_list) in [str, unicode]:
        sim = doc2vec_model.n_similarity(sent0.split(" "), sent_list.split(" "))
        return sim
    elif type(sent_list) is list:
        sim_list = []
        for sent in sent_list:
            sim = doc2vec_model.n_similarity(
                sent0.split(" "), sent.split(" ")
            )
            sim_list.append(sim)
        return sim_list


def high_rank_idx(li):
    idx_li = zip(range(0, len(li)), li)
    sorted_idx_li = sorted(idx_li, key=lambda k: k[1], reverse=True)
    return sorted_idx_li


def test():
    sent0 = 'Reinforcement learning'
    sentl = ['Markov decision process learning', 'machine learning']
    # doc2_vec_sim = doc2vec_sim(sent0, sentl)
    print bow_sim(sent0, sentl)
    # print doc2vec_sim(sent0, sentl)


if __name__ == '__main__':
    test()