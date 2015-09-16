from prereqsearch import prereq_early_terms
from prereqsearch.related_concept import related_terms_in_article
from prereqsearch.related_concept import most_mentioned_wikilinks, \
    two_way_ranked_wiki_links, similarly_covered_topics
import quesgen_wrapper
from util.wikipedia_util import WikipediaWrapper
import sys
from version_list import *


def diagnose(search_term, generate_prereq_question=False, num_prereq=3,
             version=None, set_type="Prereq"):
    if set_type == "Prereq":
        return diagnose_prereq_tree(
            search_term,
            generate_prereq_question=generate_prereq_question,
            num_prereq=num_prereq,
            version=version)
    elif set_type == "Mentioned":
        extra_question_in_text = False

        # [ADD VERSION] if the question is to be generated in main article text
        # , add a condition branch here
        if version == IN_TEXT_QUESTIONS_WITH_MENTION_COUNT_CANDIDATE:
            extra_question_in_text = True
        return diagnose_mentioned(
            search_term,
            generate_prereq_question=generate_prereq_question,
            num_prereq=num_prereq,
            version=version,
            extra_question_in_text=extra_question_in_text)


def diagnose_prereq_tree(search_term, generate_prereq_question=False,
                         num_prereq=3, version=None):
    # find prereq tree
    depth = 1
    if generate_prereq_question:
        depth = 2
    prereq_tree = prereq_early_terms.find_prereq_tree(
        search_term, depth=depth,
        num_prereq=num_prereq)

    # generate question
    topic_question = quesgen_wrapper.generate_question(
        prereq_tree, version=version)

    prereq_questions = []
    if generate_prereq_question:
        for child in prereq_tree['children']:
            child_question = quesgen_wrapper.generate_question(
                child, version=version)
            prereq_questions.append(child_question)
    questions = [topic_question] + prereq_questions

    # print questions
    return questions


def diagnose_mentioned(search_term, generate_prereq_question=False,
                       num_prereq=3,
                       version=None,
                       verbose=True,
                       extra_question_in_text=False,
                       candidate_question_max_count=10):
    # depth = 1
    # if generate_prereq_question:
    # depth = 2

    prereq_tree = prereq_early_terms.find_prereq_tree(
        search_term, depth=1,  # depth,
        num_prereq=num_prereq)

    # generate question
    topic_question = quesgen_wrapper.generate_question(
        prereq_tree, version=version)

    main_article_wikipage = prereq_tree['wikipage']
    child_questions = []
    if generate_prereq_question:

        # Uncomment the following for fast debugging, remove after debugging
        # if search_term == "Reinforcement learning":
        # candidate_topics = [u'Software agent', u'Markov decision process',
        # u'Machine learning', u'Temporal difference',
        # u'Dynamic programming']
        #     alias = {}
        #     for c in candidate_topics:
        #         alias[c] = []
        # else:

        # [ADD VERSION] select the right candiate selection algorithm
        if version == SKIPTHOUGHT_SIM_DISTRACTOR_WITH_TWO_WAY_MEASURED_CANDIDATE:
            candidate_topics, alias = related_terms_in_article(
                main_article_wikipage, rank_method=two_way_ranked_wiki_links,
                max_count=candidate_question_max_count
            )
        else:
            candidate_topics, alias = related_terms_in_article(
                main_article_wikipage, rank_method=most_mentioned_wikilinks,
                max_count=candidate_question_max_count)

        # TODO:: make this a parameter
        candidate_question_count = 0

        if verbose:
            print "Candidates for", search_term, ":", \
                candidate_topics[:candidate_question_max_count]

        if extra_question_in_text:
            used_sentences = []
            for candidate in candidate_topics:
                try:
                    # [Future] TODO:: intelligently decide
                    # question type for subtopics
                    # as in some case item question is better, and vice versa.

                    # [ADD VERSION] TODO:: add a separate version for this.
                    child_question = quesgen_wrapper.generate_item_question(
                        candidate, alias[candidate],
                        main_article_wikipage, used_sentences)

                    # descriptive questions
                    # child_question = quesgen_wrapper.generate_question(
                    # {'wikipage': WikipediaWrapper.page(candidate)},
                    # version=version)
                    try:
                        used_sentences.append(
                            child_question['original_sentence'])
                        child_question.pop('original_sentence', None)
                    except KeyError:
                        used_sentences.append(
                            child_question['question_text'].repalce(
                                '________', child_question['correct_answer']))
                    if child_question:
                        child_questions.append(child_question)
                        candidate_question_count += 1

                    if candidate_question_count >= candidate_question_max_count:
                        break
                except ValueError, ve:
                    print >> sys.stderr, ve
                    continue
        else:
            for candidate in candidate_topics:
                try:
                    candidate_page = WikipediaWrapper.page(candidate)
                except Exception as e:
                    print "Cannot load page for question generation:", e
                    continue

                child_question = quesgen_wrapper.generate_question(
                    {'wikipage': candidate_page}, version=version)
                if child_question:
                    child_questions.append(child_question)
                    candidate_question_count += 1
                if candidate_question_count >= candidate_question_max_count:
                    break

    questions = [topic_question] + child_questions

    return questions