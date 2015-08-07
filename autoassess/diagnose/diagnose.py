from prereqsearch import prereq_early_terms
from prereqsearch.related_concept import most_mentioned_wikilinks
import quesgen_wrapper
from util.wikipedia_util import WikipediaWrapper
import sys


def diagnose(search_term, generate_prereq_question=False, num_prereq=3,
             version=None, set_type="Prereq"):
    if set_type == "Prereq":
        return diagnose_prereq_tree(
            search_term,
            generate_prereq_question=generate_prereq_question,
            num_prereq=num_prereq,
            version=version)
    elif set_type == "Mentioned":
        return diagnose_mentioned(
            search_term,
            generate_prereq_question=generate_prereq_question,
            num_prereq=num_prereq,
            version=version)


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
                       verbose=True):
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
    prereq_questions = []
    if generate_prereq_question:
        candidate_topics, alias = most_mentioned_wikilinks(
            main_article_wikipage, with_count=False)
        candidate_topics = candidate_topics[:5]

        if verbose:
            print "Candidates for", search_term, ":", candidate_topics

        for candidate in candidate_topics:
            try:
                child_question = quesgen_wrapper.generate_item_question(
                    candidate, alias[candidate],
                    main_article_wikipage)
                # child_question = quesgen_wrapper.generate_question(
                # {'wikipage': WikipediaWrapper.page(candidate)},
                # version=version)
                prereq_questions.append(child_question)
            except ValueError, ve:
                print >> sys.stderr, ve
                continue
    questions = [topic_question] + prereq_questions

    return questions