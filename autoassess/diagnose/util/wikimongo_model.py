__author__ = 'moonkey'

from mongoengine import *


class WikipediaArticle(Document):
    """
    This matches what the wikipedia.page() returns [WikipediaPage object], and saves it
    But this is not the same object as the WikipediaPage in the 'wikipedia' package
    """
    # TODO:: how about just a dict field? Think about that.

    WikiArticleTypes = ["redirect", "page", "disambiguation"]

    ###### Redirect ######
    redirect = StringField()

    ###### Disambiguation ######
    pages = ListField(StringField())

    ###### Page ######
    # common
    title = StringField(unique=True)
    categories = ListField(StringField())

    # From JS parser
    type = StringField(choices=WikiArticleTypes)
    infobox = DictField()
    tables = ListField(StringField())
    text = DictField()

    # From wikipedia.page()
    images = ListField(StringField())
    content = StringField()
    links = ListField(StringField())
    original_title = StringField()
    # TODO:figure out what "original_title" actually means? May need to merge the titles, or just delte this field
    pageid = StringField()
    parent_id = IntField()
    references = ListField(URLField())
    revision_id = IntField()
    sections = ListField(StringField())
    summary = StringField()

    url = URLField()


class WikiKnowledgeNode(Document):
    """
    tree node of the knowledge tree
    """
    title = StringField()
    page = ReferenceField(WikipediaArticle)
    # question = ReferenceField(WikiQuestion)

    # to reference the same type as itself
    prerequisites = ListField(ReferenceField("self", reverse_delete_rule=NULLIFY))



#TODO:: change the collection name to 'wikipedia_article', also in the importing node.js code.
#TODO:: test the read of the WikipediaArticle.
