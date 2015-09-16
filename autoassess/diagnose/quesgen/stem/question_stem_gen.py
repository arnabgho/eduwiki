__author__ = 'moonkey'

from autoassess.diagnose.util.quesgen_util import *
from autoassess.diagnose.util.NLPU import tense_match


def generate_question_stem(wikipage, verbose=False):
    question_sentences = question_sentence_generator(wikipage)

    question_generated = None

    # logged_sentences = []

    for question_sent in question_sentences:
        try:
            # logged_sentences.append(question_sent)
            # print >> sys.stderr, "question_sent:"+question_sent
            question_generated = question_from_single_sentence(
                question_sent, wikipage.title)
            if question_generated['stem'] and question_generated['answer']:
                break
        except Exception as e:
            if verbose:
                print >> sys.stderr, e
            continue

    if not question_generated:
        # raise ValueError("No question generated.")
        print >> sys.stderr, "No question generated."
        return None
    return question_generated


def question_sentence_generator(wikipage):
    sentences = topic_mentioning_sentence_generator(wikipage)
    # sentences = lex_pagerank(sentences)
    return sentences


def question_from_single_sentence(sentence, topic):
    # TODO:: the topic might be too redundant to match any sentence,
    # like "Short (finance)", inspect on this a little more.
    # Maybe just remove "(*)".

    parsed_sentence, matched_positions = match_verbal_phrase(sentence, topic)
    if matched_positions:
        matched_pos = matched_positions[0]
        matched_vp = parsed_sentence[matched_pos]

        answer = ProcessUtil.untokenize(matched_vp.leaves())

        original_vp = parsed_sentence[matched_pos]
        parsed_sentence[matched_pos] = nltk.tree.ParentedTree.fromstring(
            "(VP ________)")
        stem = ProcessUtil.untokenize(parsed_sentence.leaves())

        parsed_sentence[matched_pos] = original_vp

        answer = ProcessUtil.revert_penntreebank_symbols(answer)
        stem = ProcessUtil.revert_penntreebank_symbols(stem)

        # To match the tenses of the question stem and the distractors ########
        tenses = tense_match.find_sentence_tenses(parsed_sentence, matched_pos)
    else:
        answer = None
        stem = None
        tenses = None

    question_stem = {
        'stem': stem,
        'answer': answer,
        'tenses': tenses,
    }

    return question_stem