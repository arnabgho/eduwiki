from util import wikipedia
import prereq
import quesgen
import unicodedata

def diagnose(search_term, depth=2, num_prereq=3):
    # find prereq tree
    prereq_tree = prereq.find_prereq_tree(search_term, depth=depth, num_prereq=num_prereq)

    # generate question
    topic_question = quesgen.generate_question(prereq_tree)

    prereq_questions = []
    for child in prereq_tree['children']:
        child_question = quesgen.generate_question(child)
        prereq_questions.append(child_question)
    questions = [topic_question] + prereq_questions

    # print questions
    return questions


# def query(search_term, depth=1, num_prereq=3):
#     """
#     A recursive function that automatically generates multiple choice questions
#     for the search_term and its prereqs
#
#     :param depth: the depth of the tree, max: 6
#     :param num_prereq: the depth of the tree, max: 6
#     :return a tree (dict format) representing the term's article, with its prerequisites
#     and quiz items as well as those of the prereqs, and of their prereqs, etc.
#     """
#     # set a max depth and branching factor as a fail-safe
#     max_prereq_tree_depth = 6
#     max_num_prereq_per_node = 6
#     depth = min(depth, max_prereq_tree_depth)
#     num_prereq = min(num_prereq, max_num_prereq_per_node)
#
#     # get the topic and the names of its prereq links
#     main_topic = WikiEducate(normal(search_term))
#     prereq_names = main_topic.linked_wiki_terms(num_prereq)
#     topic_name = main_topic.page.title
#
#     # create a knowledge tree (dict) which will be recursively built
#     knowledge_children = []
#
#     # get topic text, descriptor, and distractors
#     # note: I'm referring to the actual string of text as the distractor
#     # distractor is generated from the definition of the first few linked items
#     topic_text = main_topic.page.summary  # main_topic.plain_text_summary(1)
#     description = main_topic.return_what_is()
#     distractor_names = main_topic.linked_wiki_terms(num_prereq)
#     distractors = []
#     for i in range(0, 3):
#         distractor_name = normal(distractor_names[i])
#         distractor_obj = WikiEducate(distractor_name)
#         distractor = distractor_obj.return_what_is()
#         distractors.append(distractor)  # append dis tractor *vroom*
#
#     # run for num_children if depth left
#     if depth != 0:
#         for j in range(0, num_prereq):
#             knowledge_child = query(prereq_names[j], depth=depth - 1, num_prereq=num_prereq)
#             knowledge_children.append(knowledge_child)
#
#     # assemble the tree and return it
#     prereq_tree = {
#         'title': topic_name, 'text': topic_text,
#         'description': description, 'distractors': distractors,
#         'children': knowledge_children}
#     return prereq_tree
