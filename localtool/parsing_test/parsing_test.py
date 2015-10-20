__author__ = 'moonkey'

from autoassess.diagnose.quesgen import quesgen_sentstruct
from autoassess.diagnose.util.NLPU.preprocess import ProcessUtil
import nltk
from autoassess.diagnose.util.wikimongo_model import WikipediaArticle
from autoassess.diagnose.util.wikipedia_util import *

import time

import jsonrpclib
import json
from nltk import Tree


def test_sentence_syntree():
    server = jsonrpclib.Server("http://localhost:8080")
    nlutil = ProcessUtil()
    pages = WikipediaArticle.objects()

    some_sentences = []
    count = 0
    max_count = 100
    for p in pages:
        sentences = WikipediaWrapper.article_sentences(p)
        for sentence in sentences:
            some_sentences.append(sentence)
            count += 1
            if count > max_count:
                break
        if count > max_count:
            break

    start_time = time.time()
    for idx, sentence in enumerate(some_sentences):
        # print idx
        # parsed_sentence = nlutil.parsing(sentence)
        parsed_result = json.loads(server.parse(sentence))
        # try:
        #     tree = Tree.fromstring(parsed_result['sentences'][0]['parsetree'])
        # except:
        #     print sentence
        #     print idx
        #     print parsed_result['sentences'][0]['parsetree']
        # print parsed_result
    elapsed_time = time.time() - start_time

    print float(elapsed_time) / float(max_count)
    # 100pages:1.62293873072
    # 500: 1.65
    # 0.386443588734
    # No tree rebuild: 0.372706110477

if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    test_sentence_syntree()