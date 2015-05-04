from mongoengine import *

# Create your models here.

# TODO:: rewrite all the cached terms to database
#TODO:: use mongodb... things are so easy

# Models include:
# Knowledge Tree Node


class WikiPage(Document):
    """
    This matches what the wikipedia.page() returns [WikipediaPage object], and saves it
    But this is not the same object as the WikipediaPage in the 'wikipedia' package
    """
    # TODO:: how about just a dict field? Think about that.
    categories = SortedListField(StringField)
    content = StringField()
    images = SortedListField(StringField)
    links = SortedListField(StringField)
    original_title = StringField()
    # TODO:figure out what "original_title" actually means? May need to merge the titles, or just delte this field
    pageid = StringField()
    parent_id = IntField()
    references = SortedListField(URLField)
    revision_id = IntField()
    sections = SortedListField(StringField)
    summary = StringField()
    title = StringField()
    url = URLField()


class WikiQuestion(Document):

    WikiQuestionType = (
        "WhatIs",
    )
    question_type = StringField(choices=WikiQuestionType)

    question_text = StringField()
    # We can make the options a EmbeddedDocument if needed as we may want to
    # know and store how the options are generated.
    question_options = SortedListField(StringField)
    question_answer = IntField()


class WikiKnowledgeNode(Document):
    """
    tree node of the knowledge tree
    """
    title = StringField()
    page = ReferenceField(WikiPage)
    question = ReferenceField(WikiQuestion)
    prerequisites = ListField(ReferenceField("self", reverse_delete_rule=NULLIFY))
