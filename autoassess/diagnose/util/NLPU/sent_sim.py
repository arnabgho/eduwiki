from __future__ import division
from gensim.models.doc2vec import Doc2Vec, Word2Vec
from sklearn.feature_extraction.text import CountVectorizer

import sys
import time
from sklearn.metrics.pairwise import cosine_similarity
from autoassess.diagnose.util.quesgen_util import topic_remove_bracket
from autoassess.diagnose.util.stvectors import skipthoughts

import numpy as np
import math

__author__ = 'moonkey'

WORD2VEC_MODEL = None
SKIP_THOUGHT_MODEL = None


def load_word2vec(
        model_filename="/opt/word2vec/GoogleNews-vectors-negative300.bin.gz",
        # compact_name="w2v_g100b"
):
    print >> sys.stderr, "loading word2vec model ", model_filename, \
        "(may take a few minutes) ..."
    start_time = time.time()
    model = Word2Vec.load_word2vec_format(model_filename, binary=True)
    # model.compact_name = compact_name
    elapsed = time.time() - start_time
    print >> sys.stderr, "word2vec model loading finished.", elapsed, "s"
    return model


# def load_doc2vec(
# model_filename="/opt/word2vec/GoogleNews-vectors-negative300.bin.gz"):
# print >> sys.stderr, "loading doc2vec model ", model_filename, \
# "(may take a few minutes) ..."
#     start_time = time.time()
#     model = Doc2Vec.load_word2vec_format(model_filename, binary=True)
#     elapsed = time.time() - start_time
#     print >> sys.stderr, "doc2vec model loading finished.", elapsed, "s"
#     return model

def load_skip_thoughts():
    print >> sys.stderr, "loading skip thoughts model ", \
        "(may take a few minutes) ..."
    start_time = time.time()
    # the model file path is set at the top of the skipthoughts.py file
    model = skipthoughts.load_model()
    elapsed = time.time() - start_time
    print >> sys.stderr, "skip thoughts model loading finished.", elapsed, "s"
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
    # sim_list = sim_mtx.toarray().tolist()[0]
    # for idx, sim in enumerate(sim_list):
    #     sim_list[idx] = sim / math.sqrt(len(doc_list[idx]) * len(doc0))
    #
    # if len(sim_list) == 1:
    #     return sim_list[0]

    sim_array = cosine_similarity(bow_mtx[0], bow_mtx[1:])
    sim_list = sim_array.tolist()[0]

    return sim_list


def cleaned_tokens(doc, model, doc_type="topic"):
    # global WORD2VEC_MODEL
    # if not WORD2VEC_MODEL:
    #     WORD2VEC_MODEL = load_word2vec()

    if doc_type.lower() == "topic":
        doc = topic_remove_bracket(doc)
    doc_tokens = doc.split(" ")
    to_remove = []
    for t in doc_tokens:
        if t not in model.vocab:
            to_remove.append(t)
    for tr in to_remove:
        doc_tokens.remove(tr)
    return doc_tokens


def word2vec_n_sim(doc0, doc_list, doc_type="topic"):
    if not (doc0 and doc_list):
        return None

    global WORD2VEC_MODEL
    if not WORD2VEC_MODEL:
        WORD2VEC_MODEL = load_word2vec()

    word2vec_model = WORD2VEC_MODEL

    doc0_tokens = cleaned_tokens(doc0, doc_type=doc_type, model=word2vec_model)
    # just in case the 2nd parameter is not a list as expected
    if type(doc_list) in [str, unicode]:
        sim = word2vec_model.n_similarity(
            doc0_tokens, cleaned_tokens(doc_list, word2vec_model))
        return sim
    elif type(doc_list) is list:
        sim_list = []
        for sent in doc_list:
            sent_tokens = cleaned_tokens(sent, word2vec_model)
            try:
                if not sent_tokens:
                    raise KeyError  # no word is in the vocabulary
                sim = word2vec_model.n_similarity(
                    doc0_tokens, sent_tokens)
            except KeyError as e:
                print "KeyError:", sent, sent_tokens
                sim = 0.0
            sim_list.append(sim)
        return sim_list


def doc2vec_n_sim(doc0, doc_list, doc_type="topic"):
    #TODO:: not working
    if not (doc0 and doc_list):
        return None
    global WORD2VEC_MODEL
    if not WORD2VEC_MODEL:
        WORD2VEC_MODEL = load_word2vec()

    doc2vec_model = WORD2VEC_MODEL

    doc0_tokens = cleaned_tokens(doc0, model=doc2vec_model,
                                 doc_type=doc_type)
    doc0_vec = doc2vec_model.infer_vector(doc_words=doc0_tokens)
    doc2vec_model.intersect_word2vec_format()
    print doc0_vec
    doc_vec_list = [
        doc2vec_model.infer_vector(
            cleaned_tokens(d, model=doc2vec_model, doc_type=doc_type)
        ) for d in doc_list]
    sim_array = cosine_similarity(doc0_vec, doc_vec_list)
    sim_list = sim_array.tolist()[0]
    return sim_list


def skip_thoughts_n_sim(doc0, doc_list, doc_type="topic"):
    """
    https://github.com/ryankiros/skip-thoughts
    :param doc0:
    :param doc_list:
    :param doc_type: "topic", "sentence", "paragraph"???
    :return: similarity list bewtween @doc0 and @doc_list
    """
    if not (doc0 and doc_list):
        return None
    global SKIP_THOUGHT_MODEL
    if not SKIP_THOUGHT_MODEL:
        SKIP_THOUGHT_MODEL = load_skip_thoughts()
    skip_thoughts_model = SKIP_THOUGHT_MODEL
    if type(doc_list) in [str, unicode]:
        doc_list = [doc_list]
    print "start encoding:"
    print doc0
    print doc_list
    st_vectors = skipthoughts.encode(skip_thoughts_model, [doc0] + doc_list)
    print st_vectors
    doc0_vector = st_vectors[0]
    doc_list_vector = st_vectors[1:]

    sim_array = cosine_similarity(doc0_vector, doc_list_vector)
    sim_list = sim_array.tolist()[0]
    return sim_list


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
    print bow_sim(sent0, sentl)
    # print word2vec_n_sim(sent0, sentl)
    # print doc2vec_n_sim(sent0, sentl)
    print skip_thoughts_n_sim(sent0, sentl)

if __name__ == '__main__':
    test()