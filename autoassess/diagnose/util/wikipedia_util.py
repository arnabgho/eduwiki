__author__ = 'moonkey'

import wikipedia
import str_util
import re
from nlp_util import NlpUtil
from wikimongo_model import WikipediaArticle, WikiLink, WikiCategorylinks
import wikitextparser as wtp
import time


class WikipediaWrapper:
    def __init__(self):
        pass

    # summary: in "learn()", in the template a summary section is used
    # title
    # (wikitext?) in return_what_is?

    @staticmethod
    def search(query, results=1, suggestion=True):
        return wikipedia.search(query, results=results, suggestion=suggestion)

    @staticmethod
    def page(title=None, pageid=None, auto_suggest=True, redirect=True):
        """
        The search term from user may not corresponds to a wikipedia page,
        due to vagueness. There are 2 alternatives, "redirect"/ "disambiguous".
        :param auto_suggest:let Wikipedia find a valid page title for the query
        :return:
        """
        if pageid is not None:
            pageid = int(pageid)
            page = WikipediaArticle.objects(pageid=pageid)
        else:
            page = WikipediaArticle.objects(title=title)
            if not page:
                results, suggestion = WikipediaWrapper.search(
                    title,
                    results=1,
                    suggestion=True)
                suggested_term = suggestion or results[0]
                page = WikipediaArticle.objects(title=suggested_term)

        if page:
            page = page[0]
        else:
            try:
                page = wikipedia.page(title=title,
                                      pageid=pageid,
                                      auto_suggest=auto_suggest,
                                      redirect=redirect)
            except UnicodeDecodeError:
                page = wikipedia.page(title=str_util.normal_str(title),
                                      pageid=pageid,
                                      auto_suggest=auto_suggest,
                                      redirect=redirect)
        if type(page) is wikipedia.WikipediaPage:
            page = WikipediaWrapper.save_page(page)
        return page

    @staticmethod
    def linked_terms(wikipage):
        """
        :param num: the number of linked texts to return
        :return: list(str), the first few texts that have a wikipedia link
        """

        if type(wikipage) is WikipediaArticle:
            for link in wikipage.wikilinks:
                yield link.target

        elif type(wikipage) is wikipedia.WikipediaPage:
            w_text = wikipage.wikitext
            wikilink_rx = re.compile(r'\[\[([^|\]]*\|)?([^\]]+)\]\]')

            for m in wikilink_rx.finditer(w_text):
                if m.group(1) is not None:
                    if "Image" in m.group(1) \
                            or "Template" in m.group(1) \
                            or "File" in m.group(1):
                        continue
                    link = m.group(1)[:-1]
                    yield link
                else:
                    if "Image" in m.group(2) \
                            or "Template" in m.group(2) \
                            or "File" in m.group(2):
                        continue
                    link = m.group(2)
                    yield link

    @staticmethod
    def save_page(wikipage):
        wt_parsed = wtp.parse(wikipage.wikitext)
        categories = []

        #### parse categories from wikilinks
        cat_link_started = False  # the category links may not be the last few
        for link in reversed(wt_parsed.wikilinks):
            if link.target.startswith("Category:"):
                cat_link_started = True
                categories.append(link.target.replace("Category:", ""))
            else:
                if cat_link_started:
                    break
        ####

        new_article = WikipediaArticle(
            title=wikipage.title,
            pageid=int(wikipage.pageid),

            wikitext=wikipage.wikitext,
            content=wikipage.content,
            summary=wikipage.summary,

            categories=categories,
            wikilinks=[WikiLink(target=l.target, text=l.text) for l in
                       wt_parsed.wikilinks],

            # sections=wt_parsed.sections,
        )
        new_article.save()
        return new_article

    @staticmethod
    def article_sentences(wikipage):
        sentences = []
        # if type(wikipage) is wikipedia.WikipediaPage:
        # content = wikipage.content
        nlutil = NlpUtil()
        # sentences = nlutil.sent_tokenize(content)
        if type(wikipage) is not WikipediaArticle:
            pass
        else:
            for section in wikipage.sections:
                if section.level == 0 or 2 \
                        and WikipediaWrapper.useful_section(section.title):
                    paragraphs = section.contents.split("\n")
                    for para in paragraphs:
                        para_sentences = nlutil.sent_tokenize(para)
                        sentences += para_sentences
                        for sent in para_sentences:
                            yield sent
                            # return sentences

    @staticmethod
    def useful_section(section_name):
        unuseful_sections = ["Reference", "External Link"]
        for un in unuseful_sections:
            if un.lower() in section_name.lower():
                return False
        return True

    @staticmethod
    def pages_from_category(category):
        category = category.replace(" ", "_")
        cat_links = WikiCategorylinks.objects(cl_to=category, cl_type='page')
        page_ids = [l.cl_from for l in cat_links]
        return page_ids


def test_wiki_util():
    page = WikipediaWrapper.page(title="Reinforcement learning")

    for cat in page.categories:
        print cat, WikipediaWrapper.pages_from_category(cat)


if __name__ == '__main__':
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    test_wiki_util()