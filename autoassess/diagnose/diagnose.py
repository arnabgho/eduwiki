import prereq
import quesgen_wrapper
import unicodedata


def diagnose(search_term, generate_prereq_question=False, num_prereq=3,
             version=None):
    # find prereq tree
    depth = 1
    if generate_prereq_question:
        depth = 2
    prereq_tree = prereq.find_prereq_tree(search_term, depth=depth,
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

