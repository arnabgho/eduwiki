__author__ = 'moonkey'

from mongoengine import *
import wikitextparser as wtp


class WikiLink(EmbeddedDocument):
    target = StringField(required=True)
    text = StringField()

    def __str__(self):
        return str(self.target)

    def __unicode__(self):
        return unicode(self.__str__())


# class WikipediaSection(EmbeddedDocument):
#     # sections = ListField(
#     #     EmbeddedDocumentField("self"))
#     title = StringField()
#     level = IntField()
#     contents = StringField()
#     wikilinks = ListField(EmbeddedDocumentField(WikiLink))
#
#     def __str__(self):
#         return str(self.title)
#
#     def __unicode__(self):
#         return unicode(self.__str__())


class WikipediaArticle(Document):
    """
    This matches what the wikipedia.page() returns [WikipediaPage object],
    and saves it. But this is not the same object as the WikipediaPage
    in the 'wikipedia' package
    """
    # ##### Page ######
    # common
    pageid = IntField()
    title = StringField(unique=True)


    wikitext = StringField()  # with links etc.
    content = StringField()
    summary = StringField()

    wikilinks = ListField(EmbeddedDocumentField(WikiLink))
    categories = ListField(StringField())

    # sections = ListField(EmbeddedDocumentField(WikipediaSection))
    # sections = ListField(StringField())
    @property
    def sections(self):

        try:
            if not hasattr(self, '_sections'):
                wp_parsed = wtp.parse(self.content)
                self._sections = wp_parsed.sections
                for sect in self._sections:
                    sect.title = sect.title.strip(" ")
            return self._sections
        except Exception as e:
            raise e

    def __str__(self):
        return str(self.title)

    def __unicode__(self):
        return unicode(self.__str__())
    # ########################################################
    # # Deprecated fields that are not used, only reserved  ##
    # ########################################################
    # WikiArticleTypes = ["redirect", "page", "disambiguation"]
    # # ##### Redirect ######
    # redirect = StringField()
    # # ##### Disambiguation ######
    # pages = ListField(StringField())
    # infobox = DictField()
    # tables = ListField(StringField())
    # images = ListField(StringField())
    # original_title = StringField()
    # type = StringField(choices=WikiArticleTypes)
    # references = ListField(URLField())
    # revision_id = IntField()
    # text = DictField()
    # url = URLField()
    # parent_id = IntField()


class WikiCategorylinks(Document):
    cl_from = IntField()  # page_id
    cl_to = StringField()  # category str
    cl_type = StringField()

    def __str__(self):
        return str(self.cl_from)+'>'+str(self.cl_to)

    def __unicode__(self):
        return unicode(self.__str__())

# class WikiPageId(Document):
#     page_title = StringField()

# class WikiKnowledgeNode(Document):
# """
#     tree node of the knowledge tree
#     """
#     title = StringField()
#     page = ReferenceField(WikipediaArticle)
#     # question = ReferenceField(WikiQuestion)
#
#     # to reference the same type as itself
#     prerequisites = ListField(
#         ReferenceField("self", reverse_delete_rule=NULLIFY))
