import os
import re
import sys
import traceback
import nltk_tgrep
import textblob
from textblob.np_extractors import FastNPExtractor, ConllExtractor
import nltk
import nltk.parse.stanford
import nltk.tag.stanford
import string
import itertools

__author__ = 'moonkey'


def load_stanford_parser():
    print >> sys.stderr, "loading stanford_parser"

    stanford_parser_path = '/opt/stanford-parser/stanford-parser.jar'
    env_stanford_parser = os.environ.get('STANFORD_PARSER', "")
    if stanford_parser_path not in env_stanford_parser:
        os.environ['STANFORD_PARSER'] = \
            stanford_parser_path  # + ";" + env_stanford_parser

    stanford_model_path = \
        '/opt/stanford-parser/stanford-parser-3.5.2-models.jar'
    env_stanford_model = os.environ.get('STANFORD_MODELS', "")
    if stanford_model_path not in env_stanford_model:
        os.environ['STANFORD_MODELS'] = \
            stanford_model_path  # + ";" + env_stanford_model

    parser = nltk.parse.stanford.StanfordParser(
        model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
    )
    return parser


def load_stanford_pos_tagger():
    print >> sys.stderr, "loading stanford pos tagger"
    try:
        path_to_model = \
            '/opt/stanford-postagger/models/english-bidirectional-distsim.tagger'
        path_to_jar = '/opt/stanford-postagger/stanford-postagger.jar'
        tagger = nltk.tag.stanford.POSTagger(
            path_to_model=path_to_model, path_to_jar=path_to_jar)
        return tagger
    except Exception as e:
        print >> sys.stderr, "FAILED: loading stanford pos tagger"
        print >> sys.stderr, e
        return None


def load_stanford_ner_tagger():
    print >> sys.stderr, "loading stanford NER tagger"
    try:
        path_to_model = \
            '/opt/stanford-ner/classifiers/all.3class.distsim.crf.ser.gz'
        path_to_jar = '/opt/stanford-ner/stanford-ner.jar'
        tagger = nltk.tag.stanford.NERTagger(
            path_to_model=path_to_model, path_to_jar=path_to_jar)
        return tagger
    except Exception as e:
        print >> sys.stderr, "FAILED: loading stanford NER tagger"
        print >> sys.stderr, e
        return None


def load_np_extractor():
    print >> sys.stderr, "loading noun phrase extractor"
    return ConllExtractor()


STANFORD_PARSER = load_stanford_parser()
NP_EXTRACTOR = load_np_extractor()
STANFORD_POS_TAGGER = load_stanford_pos_tagger()


class ProcessUtil:
    def __init__(self):
        self.parser = STANFORD_PARSER
        self.np_extractor = NP_EXTRACTOR
        self.pos_tagger = STANFORD_POS_TAGGER

    def _load_parser(self):
        if self.parser:
            return self.parser
        try:
            self.parser = load_stanford_parser()
            # os.environ['STANFORD_PARSER'] = os.path.join(
            # '/opt/stanford-parser/stanford-parser.jar')
            # os.environ['STANFORD_MODELS'] = os.path.join(
            # '/opt/stanford-parser/stanford-parser-3.5.2-models.jar')
            # self.parser = nltk.parse.stanford.StanfordParser(
            # model_path="edu/stanford/nlp/models"
            #                "/lexparser/englishPCFG.ser.gz")
            return self.parser
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
        sentences = nltk.sent_tokenize(text)
        return sentences

    def parsing(self, text, pre_chunk_nps=True, stanford_pos=False):
        """
        :param pre_chunk_nps: this will not "machine learning"
        """

        if not self.parser:
            self._load_parser()

        try:
            chunked_nps = {}
            if pre_chunk_nps:
                # chunk noun phrases to improve the performance of parsing
                blob = textblob.TextBlob(text, np_extractor=self.np_extractor)
                for np in blob.noun_phrases:
                    source = set(re.findall('(?i)' + np, text))
                    for s in source:
                        target = s.replace(" ", "_")
                        text = text.replace(np, target)
                        chunked_nps.update({target: s})

            tokens = nltk.word_tokenize(text)

            # actually parsing
            if stanford_pos and self.pos_tagger:
                tagged = self.pos_tagger.tag(tokens)
                if len(tagged) > 1:
                    print >> sys.stderr, "POS tagger found >1 sentences", tagged
                    tagged = list(itertools.chain(*tagged))
                else:
                    tagged = tagged[0]
                # "_" will be eliminated in the tagging process

                if pre_chunk_nps:
                    to_update = {}
                    for np in chunked_nps:
                        to_update.update(
                            {np.replace("_", ""): chunked_nps[np]})
                    chunked_nps.update(to_update)

                parsed = self.parser.tagged_parse(tagged).next()
            else:
                parsed = self.parser.parse(tokens).next()

            # get the original noun phrases back
            for leaf_idx in range(0, len(parsed.leaves())):
                leaf_position = parsed.leaf_treeposition(leaf_idx)
                parent_position = tuple(
                    list(leaf_position)[:len(leaf_position) - 1])

                new_node = parsed[leaf_position].replace("_", " ")
                parsed[parent_position][0] = new_node
                # more strict substitution rules
                if parsed[leaf_position] in chunked_nps:
                    parsed[parent_position][0] = chunked_nps[
                        parsed[leaf_position]]

                # (Deprecated) Trying to recover the parser tree structure
                # Problematic code:
                # "an o_d_e" will be (NP (DT an) (NP (JJ o) (JJ d) (NN e)))
                # which was supposed to be
                # (NP (DT an) (JJ o) (JJ d) (NN e))
                # if '_' in parsed[leaf_position]:
                # word_list = parsed[leaf_position].split("_")
                # if len(word_list) == 1:
                # new_node = Tree.fromstring("(NN " + word_list[0] + ")")
                # parsed[parent_position][0] = new_node
                # else:
                # node_str = "(NP "
                # for idx in range(0, len(word_list) - 1):
                # node_str += "(JJ " + word_list[idx] + ")"
                # node_str += "(" + parsed[parent_position].label() + \
                # " " + word_list[-1] + ")"
                #         node_str += ")"
                #         new_node = Tree.fromstring(node_str)
                #         parsed[parent_position] = new_node
                #         Tree.insert()

        except Exception, err:
            print >> sys.stderr, str(err)
            traceback.print_exc(file=sys.stderr)
            return None
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