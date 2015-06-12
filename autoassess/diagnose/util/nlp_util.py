__author__ = 'moonkey'

import nltk
import string
import os
import nltk.parse.stanford
import nltk_tgrep


class NlpUtil:
    def __init__(self):
        self.tokenizer = None
        self.parser = None

    def _load_tokenizer(self):
        try:
            if not self.tokenizer:
                self.tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
                return True
        except:
            raise Exception

    def _load_parser(self):
        if self.parser:
            return True
        try:
            os.environ['STANFORD_PARSER'] = os.path.join(
                os.path.expanduser('~'), 'stanford-parser/stanford-parser.jar')
            os.environ['STANFORD_MODELS'] = os.path.join(
                os.path.expanduser('~'), 'stanford-parser/stanford-parser-3.5.2-models.jar')
            self.parser = nltk.parse.stanford.StanfordParser(
                model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
            return True
        except Exception:
            raise Exception

    def punkt_tokenize(self, text):
        """
        NLTK sentence tokenizer
        http://www.nltk.org/_modules/nltk/tokenize/punkt.html
        The algorithm for this tokenizer is described in::
            Kiss, Tibor and Strunk, Jan (2006): Unsupervised Multilingual Sentence
            Boundary Detection.  Computational Linguistics 32: 485-525.
        :param text:
        :return:
        """
        if not self.tokenizer:
            self._load_tokenizer()
        sentences = self.tokenizer.tokenize(text)
        return sentences

    def parsing(self, text):
        if not self.parser:
            self._load_parser()
        tokens = nltk.word_tokenize(text)
        # tagged = nltk.pos_tag(tokens)
        parsed = self.parser.parse(tokens).next()
        return parsed

    @staticmethod
    def tgrep_positions(sent_tree, pattern):
        if type(sent_tree) is not nltk.tree.ParentedTree:
            sent_tree = nltk.tree.ParentedTree.convert(sent_tree)
        matched_positions = nltk_tgrep.tgrep_positions(sent_tree, pattern)

        # TODO:: insepct other functions, is there a result like in regex where each parts are separated?
        return matched_positions

    @classmethod
    def tgrep(cls, sent_tree, pattern):
        return sent_tree[cls.tgrep_positions(sent_tree, pattern)]

    @staticmethod
    def untokenize(tokens):
        sentence = "".join(
            [" " + i if not i.startswith("'") and i not in string.punctuation else i for i in tokens]).strip()
        return sentence


class ProcessedText:
    """
    Maybe use nltk.stem.wordnet.WordNetLemmatizer instead of PorterStemmer.
    As stemmer semms just truncate the last parts, 'wolves' to 'wolv' not 'wolf'.
    But we will need to specify pos tag, like lemmatize('running'[,'n']) will be 'running'
     when lemmatize('running', 'v') will be 'run'. This is not what we want,
     like we want 'hypothesis test' to be matched with 'hypothesis testing'.
    """

    def __init__(self, text, stemmer=nltk.stem.PorterStemmer()):
        if type(text) is str:
            self.original_text = text
            self.original_tokens = nltk.word_tokenize(text)
        elif type(text) is list:
            self.original_tokens = text
            self.original_text = NlpUtil.untokenize(text)

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
        self.processed_tokens = [t.lower() for t in self.stemmed_tokens if t.lower() not in stopwords]


    def _stemming(self, stemmer=nltk.stem.PorterStemmer()):
        if not self.original_tokens:
            return None

        self.stemmed_tokens = [stemmer.stem(t) for t in self.original_tokens]

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
        if type(text) is str or unicode:
            original_tokens = nltk.word_tokenize(text)
        elif type(text) is list:  # tokens
            original_tokens = text
        else:
            original_tokens = None

        stemmed_tokens = [stemmer.stem(t.lower()) for t in original_tokens if t.lower() not in stopwords]

        if type(text) is str or unicode:
            stemmed_str = NlpUtil.untokenize(stemmed_tokens)
            return stemmed_str
        elif type(text) is list:
            return stemmed_tokens
        else:
            return None


def test():
    nlutil = NlpUtil()

    sentence = "At eight o'clock on Thursday morning Arthur didn't feel very good. I am good."
    tags = nlutil.pos_tag(sentence)
    print tags


if __name__ == '__main__':
    test()