__author__ = 'moonkey'

import os
import re
import sys
import traceback
import nltk_tgrep
import textblob
from textblob.np_extractors import FastNPExtractor, ConllExtractor
import nltk
import nltk.parse.stanford
import string
from nltk.tree import Tree


def load_punkt_tokenizer():
    print >> sys.stderr, "loading tokenizer"
    return nltk.data.load('tokenizers/punkt/english.pickle')


def load_stanford_parser():
    print >> sys.stderr, "loading stanford_parser"
    # os.environ['STANFORD_PARSER'] = os.path.join(
    # os.path.expanduser('~'), 'stanford-parser/stanford-parser.jar')
    # os.environ['STANFORD_MODELS'] = os.path.join(
    # os.path.expanduser('~'),
    # 'stanford-parser/stanford-parser-3.5.2-models.jar')
    os.environ['STANFORD_PARSER'] = os.path.join(
        '/opt/stanford-parser/stanford-parser.jar')
    os.environ['STANFORD_MODELS'] = os.path.join(
        '/opt/stanford-parser/stanford-parser-3.5.2-models.jar')
    parser = nltk.parse.stanford.StanfordParser(
        model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    return parser


def load_np_extractor():
    print >> sys.stderr, "loading noun phrase extractor"
    return ConllExtractor()


PUNKT_TOKENIZER = load_punkt_tokenizer()
STANFORD_PARSER = load_stanford_parser()
NP_EXTRACTOR = load_np_extractor()


class ProcessUtil:
    def __init__(self):
        self.tokenizer = PUNKT_TOKENIZER
        self.parser = STANFORD_PARSER
        self.np_extractor = NP_EXTRACTOR

    def _load_tokenizer(self):
        try:
            if not self.tokenizer:
                self.tokenizer = nltk.data.load(
                    'tokenizers/punkt/english.pickle')
                return True
        except:
            raise Exception

    def _load_parser(self):
        if self.parser:
            # print >> sys.stderr, 'parser already there'
            return True
        try:
            os.environ['STANFORD_PARSER'] = os.path.join(
                '/opt/stanford-parser/stanford-parser.jar')
            os.environ['STANFORD_MODELS'] = os.path.join(
                '/opt/stanford-parser/stanford-parser-3.5.2-models.jar')
            self.parser = nltk.parse.stanford.StanfordParser(
                model_path="edu/stanford/nlp/models"
                           "/lexparser/englishPCFG.ser.gz")
            return True
        except Exception:
            raise Exception

    @staticmethod
    def sent_tokenize(text):
        """
        NLTK sentence tokenizer
        http://www.nltk.org/_modules/nltk/tokenize/punkt.html
        The algorithm for this tokenizer is described in::
        Kiss, Tibor and Strunk, Jan (2006): Unsupervised Multilingual Sentence
        Boundary Detection.  Computational Linguistics 32: 485-525.
        :param text:
        :return:
        """
        # if not self.tokenizer:
        # self._load_tokenizer()
        # sentences = self.tokenizer.tokenize(text)
        sentences = nltk.sent_tokenize(text)
        return sentences

    def parsing(self, text):
        if not self.parser:
            self._load_parser()

        try:
            # chunk noun phrases to improve the performance of parsing
            blob = textblob.TextBlob(text, np_extractor=self.np_extractor)
            chunked_nps = {}
            print "Extracted NPs:", blob.noun_phrases
            for np in blob.noun_phrases:
                source = set(re.findall('(?i)' + np, text))
                for s in source:
                    target = s.replace(" ", "_")
                    text = text.replace(np, target)
                    chunked_nps.update({target: s})
            tokens = nltk.word_tokenize(text)
            # actually parsing
            parsed = self.parser.parse(tokens).next()

            # get the original noun phrases back
            for leaf_idx in range(0, len(parsed.leaves())):
                leaf_position = parsed.leaf_treeposition(leaf_idx)
                parent_position = tuple(
                    list(leaf_position)[:len(leaf_position) - 1])
                # grandparent_position = tuple(
                #     list(leaf_position)[:len(leaf_position) - 2])

                new_node = parsed[leaf_position].replace("_", " ")
                parsed[parent_position][0] = new_node
                # more strict substitution rules
                # if parsed[leaf_position] in chunked_nps:
                # parsed[parent_position][0] = chunked_nps[
                # parsed[leaf_position]]

                # if '_' in parsed[leaf_position]:
                # word_list = parsed[leaf_position].split("_")
                #     if len(word_list) == 1:
                #         new_node = Tree.fromstring("(NN " + word_list[0] + ")")
                #         parsed[parent_position][0] = new_node
                #     else:
                #         node_str = "(NP "
                #         for idx in range(0, len(word_list) - 1):
                #             node_str += "(JJ " + word_list[idx] + ")"
                #         node_str += "(" + parsed[parent_position].label() + \
                #                     " " + word_list[-1] + ")"
                #         node_str += ")"
                #         new_node = Tree.fromstring(node_str)
                #         parsed[parent_position] = new_node
                #         Tree.insert()
                # "an o_d_e" will be (NP (DT an) (NP (JJ o) (JJ d) (NN e)))
                # which was supposed to be
                # (NP (DT an) (JJ o) (JJ d) (NN e))

        except Exception, err:
            # print >> sys.stderr, "the sentence cannot be parsed"
            print >> sys.stderr, str(err)
            traceback.print_exc(file=sys.stderr)
            return None
        # print >> sys.stderr, "parsed_tree:" + str(parsed)
        return parsed

    @staticmethod
    def tgrep_positions(sent_tree, match_pattern):
        if type(sent_tree) is not nltk.tree.ParentedTree:
            sent_tree = nltk.tree.ParentedTree.convert(sent_tree)
        matched_positions = nltk_tgrep.tgrep_positions(sent_tree, match_pattern)

        # TODO:: insepct other functions, is there a result like
        # in regex where each parts are separated?
        return matched_positions

    @classmethod
    def tgrep(cls, sent_tree, pattern):
        return sent_tree[cls.tgrep_positions(sent_tree, pattern)]

    @staticmethod
    def untokenize(tokens):
        sentence = "".join(
            [" " + i
             if not i.startswith("'") and i not in string.punctuation
             else i for i in tokens]).strip()
        return sentence

    @staticmethod
    def revert_penntreebank_symbols(text):
        dic = {
            '-LRB- ': '(',
            ' -RRB-': ')',
            '-LSB- ': '[',
            ' -RSB-': ']',
            '-LCB- ': '{',
            ' -RCB-': '}'
        }
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text


class ProcessedText:
    """
    Maybe use nltk.stem.wordnet.WordNetLemmatizer instead of PorterStemmer.
    As stemmer semms just truncate the last parts,
    'wolves' to 'wolv' not 'wolf'.
    But we will need to specify pos tag, like lemmatize('running'[,'n']) will
     be 'running' when lemmatize('running', 'v') will be 'run'.
    This is not what we want, like we want 'hypothesis test'
     to be matched with 'hypothesis testing'.
    """

    def __init__(self, text):
        if type(text) is str:
            self.original_text = text
            self.original_tokens = nltk.word_tokenize(text)
        elif type(text) is list:
            self.original_tokens = text
            self.original_text = ProcessUtil.untokenize(text)

        self.stemmed_tokens = None
        self.processed_tokens = None

        self._processing()
        # self.stemmed = self.stemming(text=text, stemmer=stemmer)

    def _processing(self):
        stopwords = nltk.corpus.stopwords.words('english')
        stopwords += list(string.punctuation)

        if not self.stemmed_tokens:
            self._stemming()
        # to lower case and remove stop words
        self.processed_tokens = [
            t.lower() for t in self.stemmed_tokens
            if t.lower() not in stopwords]

    def _stemming(self, stemmer=nltk.stem.PorterStemmer()):
        if not self.original_tokens:
            return None
        try:
            self.stemmed_tokens = [stemmer.stem(t)
                                   for t in self.original_tokens]
        except UnicodeDecodeError as e:
            raise e
            # self.stemmed_tokens = \
            # [stemmer.stem(unicode(t, 'utf-8')) for t in self.original_tokens]

    @staticmethod
    def stemming(text, stemmer=nltk.stem.PorterStemmer()):
        """
            stemming/ to lower case
        :param text: list of tokens
        :param stemmer:
        :return: returned type is the same as input text.
        """
        stopwords = nltk.corpus.stopwords.words('english')
        stopwords += list(string.punctuation)

        if not text:
            return None
        if type(text) is str or type(text) is unicode:
            original_tokens = nltk.word_tokenize(text)
        elif type(text) is list:  # tokens
            original_tokens = text
        else:
            original_tokens = None

        stemmed_tokens = [
            stemmer.stem(t.lower()) for t in original_tokens
            if t.lower() not in stopwords]

        if type(text) is str or type(text) is unicode:
            stemmed_str = ProcessUtil.untokenize(stemmed_tokens)
            return stemmed_str
        elif type(text) is list:
            return stemmed_tokens
        else:
            return None


def test():
    nlutil = ProcessUtil()

    sentence = "At eight o'clock on Thursday morning " \
               "Arthur didn't feel very good. I am good."
    tags = nlutil.pos_tag(sentence)
    print tags


if __name__ == '__main__':
    test()