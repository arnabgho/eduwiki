__author__ = 'moonkey'

import nltk
import string

class NlUtil:
    def __init__(self):
        self.tokenizer = None

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
            self.tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sentences = self.tokenizer.tokenize(text)
        return sentences

    def pos_tag(self, text):
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        return tagged


class StemmedText:
    """
    Maybe use nltk.stem.wordnet.WordNetLemmatizer instead of PorterStemmer.
    As stemmer semms just truncate the last parts, 'wolves' to 'wolv' not 'wolf'.
    But we will need to specify pos tag, like lemmatize('running'[,'n']) will be 'running'
     when lemmatize('running', 'v') will be 'run'. This is not what we want,
     like we want 'hypothesis test' to be matched with 'hypothesis testing'.
    """

    def __init__(self, text, stemmer=nltk.stem.PorterStemmer()):
        self.original = text
        self.stemmed = self._stemming(text=text, stemmer=stemmer)

    @staticmethod
    def _stemming(text, stemmer=nltk.stem.PorterStemmer()):
        """
            stemming/ to lower case
        :param text: str or list of tokens
        :param stemmer:
        :return: returned type is the same as input text, str of list.
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
            stemmed_str = ' '.join(stemmed_tokens)
            return stemmed_str
        elif type(text) is list:
            return stemmed_tokens
        else:
            return None


def test():
    nlutil = NlUtil()
    # a = "In numerical analysis, isotonic regression (IR) involves finding a weighted " \
    # "least-squares fit to a vector with weights vector subject to a set of non-contradictory" \
    #     " constraints of kind . Such constraints define partial order or total order and can be " \
    #     "represented as a directed graph , where N is the set of variables involved, and E is the " \
    #     "set of pairs (i, j) for each constraint . Thus, the IR problem corresponds to the following" \
    #     " quadratic program (QP): In the case when is a total order, a simple iterative algorithm" \
    #     " for solving this QP is called the pool adjacent violators algorithm (PAVA). Best and " \
    #     "Chakravarti (1990) have studied the problem as an active set identification problem, and " \
    #     "have proposed a primal algorithm in O(n), the same complexity as the PAVA, which can be seen" \
    #     " as a dual algorithm. IR has applications in statistical inference, for example, to fit of an " \
    #     "isotonic curve to mean experimental results when an order is expected. A benefit of isotonic " \
    #     "regression is that it does not assume any form for the target function, such as linearity assumed" \
    #     " by linear regression. Another application is nonmetric multidimensional scaling, where a " \
    #     "low-dimensional embedding for data points is sought such that order of distances between points" \
    #     " in the embedding matches order of dissimilarity between points. Isotonic regression is used " \
    #     "iteratively to fit ideal distances to preserve relative dissimilarity order. Isotonic regression" \
    #     " is also sometimes referred to as monotonic regression. Correctly speaking, isotonic is used when" \
    #     " the direction of the trend is strictly increasing, while monotonic could imply a trend that is " \
    #     "either strictly increasing or strictly decreasing. Isotonic Regression under the for is defined as" \
    #     " follows:"
    #
    # sentences = util.punkt_tokenize(a)
    # stemmed = [StemmedText(s).stemmed for s in sentences]
    # print '\n-----\n'.join(sentences)
    # print '\n-----\n'.join(stemmed)

    sentence = "At eight o'clock on Thursday morning Arthur didn't feel very good. I am good."
    tags = nlutil.pos_tag(sentence)
    print tags


if __name__ == '__main__':
    test()