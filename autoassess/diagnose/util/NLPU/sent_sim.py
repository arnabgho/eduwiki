from __future__ import division
from gensim.models.doc2vec import Doc2Vec
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import sys
import time
from sklearn.metrics.pairwise import cosine_similarity
from autoassess.diagnose.util.quesgen_util import topic_remove_bracket

__author__ = 'moonkey'

DOC2VEC_MODEL = None  # load_doc2vec()


def load_doc2vec(
        model_filename="/opt/word2vec/GoogleNews-vectors-negative300.bin.gz"):
    print >> sys.stderr, "loading doc2vec model ", model_filename, \
        "(may take a few minutes) ..."
    start_time = time.time()
    model = Doc2Vec.load_word2vec_format(
        model_filename,
        binary=True)
    elapsed = time.time() - start_time
    print >> sys.stderr, "doc2vec model loading finished ...", elapsed, "s"
    return model


def bow_sim(doc0, doc_list):
    cv = CountVectorizer()
    if type(doc_list) in [str, unicode]:
        doc_list = [doc_list]
    bow_mtx = cv.fit_transform([doc0] + doc_list)
    sim_mtx = bow_mtx[1:] * bow_mtx[0].transpose()
    sim_mtx = sim_mtx.transpose()
    if not 1 in sim_mtx.get_shape():
        raise AttributeError(
            "The sim_mtx should has only one column or only one row.")
    sim_list = sim_mtx.toarray().tolist()[0]
    for idx, sim in enumerate(sim_list):
        sim_list[idx] = sim / (len(doc_list[idx]) * len(doc0))

    if len(sim_list) == 1:
        return sim_list[0]
    return sim_list


def word2vec_n_sim(doc0, doc_list, doc_type="topic"):
    if not (doc0 and doc_list):
        return None

    global DOC2VEC_MODEL
    if not DOC2VEC_MODEL:
        DOC2VEC_MODEL = load_doc2vec()

    doc2vec_model = DOC2VEC_MODEL

    def cleaned_tokens(doc):
        if doc_type.lower() == "topic":
            doc = topic_remove_bracket(doc)
        doc_tokens = doc.split(" ")
        to_remove = []
        for t in doc_tokens:
            if t not in doc2vec_model.vocab:
                to_remove.append(t)
        for tr in to_remove:
            doc_tokens.remove(tr)
        return doc_tokens

    doc0_tokens = cleaned_tokens(doc0)
    # just in case the 2nd parameter is not a list as expected
    if type(doc_list) in [str, unicode]:
        sim = doc2vec_model.n_similarity(
            doc0_tokens, cleaned_tokens(doc_list))
        return sim
    elif type(doc_list) is list:
        sim_list = []
        for sent in doc_list:
            sent_tokens = cleaned_tokens(sent)
            try:
                if not sent_tokens:
                    raise KeyError  # no word is in the vocabulary
                sim = doc2vec_model.n_similarity(
                    doc0_tokens, sent_tokens)
            except KeyError as e:
                print "KeyError:", sent, sent_tokens
                sim = 0.0
            sim_list.append(sim)
        return sim_list


def doc2vec_n_sim(doc0, doc_list):
    if not (doc0 and doc_list):
        return None
    global DOC2VEC_MODEL
    if not DOC2VEC_MODEL:
        DOC2VEC_MODEL = load_doc2vec()

    doc2vec_model = DOC2VEC_MODEL

    doc2vec_model.infer_vector()
    # cosine_similarity()


def sort_docs_by_similarity(doc0, doc_list, sim_func=bow_sim,
                            remove_sub=True):
    doc_sims = sim_func(doc0, doc_list)
    sim_pairs = zip(doc_list, doc_sims)
    sorted_pairs = sorted(sim_pairs, key=lambda k: k[1], reverse=True)
    print "Sorted by similarity:", sorted_pairs
    sorted_docs = [d[0] for d in sorted_pairs]
    if remove_sub:
        sorted_docs = remove_subtopics(doc0, sorted_docs)
        print "After removing subtopics:", sorted_docs
    return sorted_docs


def remove_subtopics(master_topic, topic_list=list()):
    to_remove = []

    for t in topic_list:
        if is_subtopic(master_topic, t) or is_subtopic(t, master_topic):
            to_remove.append(t)
    for tr in to_remove:
        topic_list.remove(tr)
    return topic_list


def is_subtopic(topic0, susceptible_topic):
    topic0 = topic_remove_bracket(topic0.lower())
    topic0_tokens = topic0.split()

    susceptible_topic = susceptible_topic.lower()

    result = True
    for t in topic0_tokens:
        if t not in susceptible_topic:
            result = False
            break
    return result


def test():
    sent0 = 'Reinforcement learning'
    sentl = ['Markov decision process learning', 'machine learning']
    # doc2_vec_sim = word2vec_n_sim(sent0, sentl)
    print bow_sim(sent0, sentl)
    # print word2vec_n_sim(sent0, sentl)


if __name__ == '__main__':
    test()