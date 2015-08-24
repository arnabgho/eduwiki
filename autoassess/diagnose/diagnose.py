from prereqsearch import prereq_early_terms
from prereqsearch.related_concept import related_terms_in_article
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
                       verbose=True,
                       extra_question_in_text=False):
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
        candidate_topics, alias = related_terms_in_article(
            main_article_wikipage)
        candidate_topics = candidate_topics[:5]

        if verbose:
            print "Candidates for", search_term, ":", candidate_topics

        if extra_question_in_text:
            used_sentences = []
            for candidate in candidate_topics:
                try:
                    # TODO:: decide question type for subtopics

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
                    child_questions.append(child_question)

                except ValueError, ve:
                    print >> sys.stderr, ve
                    continue
        else:
            for candidate in candidate_topics:
                candidate_page = WikipediaWrapper.page(candidate)
                child_question = quesgen_wrapper.generate_question(
                    {'wikipage': candidate_page}, version=version)
                child_questions.append(child_question)
    questions = [topic_question] + child_questions

    return questions