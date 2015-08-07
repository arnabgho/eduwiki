__author__ = 'moonkey'

from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
import sys
import re
from autoassess.diagnose.util.quesgen_util import topic_regex


def generate_item_question_stem(
        topic, topic_aliases, wikipage, verbose=True):
    # match to get the sentences
    question_sentences = item_sentence_generator(topic, topic_aliases, wikipage)

    # generate the questions:
    question_generated = None
    for question_sent in question_sentences:
        if verbose:
            print question_sent
        try:
            # TODO:: make the matching better
            answer = None
            if topic.lower() in question_sent.lower():
                start_pos = question_sent.lower().find(topic.lower())
                end_pos = start_pos + len(topic)
                answer = question_sent[start_pos:end_pos]
            else:
                for al in topic_aliases:
                    if al in question_sent.lower():
                        answer = al
            if answer:
                question_generated = {
                    'answer': answer,
                    'stem': question_sent.replace(answer, '________')
                }
                break
        except Exception as e:
            print >> sys.stderr, e
            continue

    if not question_generated:
        raise ValueError("No question generated.")
    return question_generated


def item_sentence_generator(topic, topics_aliases, wikipage):
    sentences = WikipediaWrapper.article_sentences(wikipage)
    quiz_topic_re = re.compile(topic_regex(wikipage.title))
    # topic_re = re.compile(topic_regex(topic))

    for s in sentences:
        if quiz_topic_re.search(s):
            continue
        # if topic_re.search(s):
        # yield s
        if topic.lower() in s.lower():
            yield s
        else:
            for al in topics_aliases:
                if al in s:
                    yield s
                    break