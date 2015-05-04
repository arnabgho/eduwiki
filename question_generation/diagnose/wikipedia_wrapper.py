import os
import tempfile
import time
import hashlib
import wikipedia
import re
import json
import sys
import unicodedata
from WikiEducate import WikiEducate


def query(search_term, depth=1, num_children=3):
    """
    A recursive function that automatically generates multiple choice questions
    for the search_term and its prereqs

    :param depth: the depth of the tree, max: 6
    :param num_children: the depth of the tree, max: 6
    :return a tree (dict format) representing the term's article, with its prerequisites
    and quiz items as well as those of the prereqs, and of their prereqs, etc.
    """
    # set a max depth and branching factor as a fail-safe
    max_knowledge_tree_depth = 6
    max_num_children_per_node = 6
    depth = min(depth, max_knowledge_tree_depth)
    num_children = min(num_children, max_num_children_per_node)

    # get the topic and the names of its prereq links
    main_topic = WikiEducate(normal(search_term))
    prereq_names = main_topic.wiki_links(num_children)
    topic_name = main_topic.page.title

    # create a knowledge tree (dict) which will be recursively built
    knowledge_children = []


    # get topic text, descriptor, and distractors
    # note: I'm referring to the actual string of text as the distractor
    # distractor is generated from the definition of the first few linked items
    topic_text = main_topic.page.summary  # main_topic.plain_text_summary(1)
    description = main_topic.return_what_is()
    distractor_names = main_topic.wiki_links(num_children)
    distractors = []
    for i in range(0, 3):
        distractor_name = normal(distractor_names[i])
        distractor_obj = WikiEducate(distractor_name)
        distractor = distractor_obj.return_what_is()
        distractors.append(distractor)  # append dis tractor *vroom*

    # run for num_children if depth left
    if depth != 0:
        for j in range(0, num_children):
            json_child = query(prereq_names[j], depth=depth - 1, num_children=num_children)
            knowledge_children.append(json_child)

    # assemble the tree and return it
    knowledge_tree = {
        'title': topic_name, 'text': topic_text,
        'description': description, 'distractors': distractors,
        'children': knowledge_children}
    return knowledge_tree


def normal(text):
    """
    normalize unicode and return ascii text
    return "ascii" if there is an UnicodeEncodeError
    """
    return str(text)
    # try:
    # return unicodedata.normalize('NFKD', text).encode('ascii')
    # except UnicodeEncodeError as u:
    #     return "ascii" + str(u)


# def getpage(topic):
# return WikiEducate(topic)


# def getpage_exact(topic):
# return WikiEducate(topic, autosuggest=False)




