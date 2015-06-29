__author__ = 'moonkey'

import wikipedia
import str_util
import re
from nlp_util import NlpUtil
from wikimongo_model import WikipediaArticle


class WikipediaWrapper:
    def __init__(self):
        pass

    # TODO:: search local database first
    # summary: in "learn()", in the template a summary section is used
    # title
    # (wikitext?) in return_what_is?

    @staticmethod
    def search(query, results=1, suggestion=True):
        return wikipedia.search(query, results=results, suggestion=suggestion)

    @staticmethod
    def page(title=None, pageid=None, auto_suggest=True, redirect=True):
        """
        The search term from user may not directly corresponds to a wikipedia page,
        due to vagueness. There are 2 alternatives, "redirect" or "disambiguous".
        :param search_term:
        :param auto_suggest:let Wikipedia find a valid page title for the query
        :return:
        """
        try:
            page = WikipediaArticle.objects(title=title, pageid=str(pageid))
        except Exception as e:
            raise e

        page = wikipedia.page(title=title, pageid=pageid, auto_suggest=auto_suggest, redirect=redirect)
        # page = wikipedia.page(str_util.normal_str(title), pageid=pageid, auto_suggest=auto_suggest, redirect=redirect)
        if type(page) is wikipedia.WikipediaPage:
            pass  # TODO:: store page in
        else:  # local db load
            pass
        return page

    @staticmethod
    def sequential_linked_terms(wikipage):
        """
        :param num: the number of linked texts to return
        :return: list(strings), the first few texts that have a wikipedia hyper link
        """
        # TODO:: use the iwlinks to get the first few links!
        # internal_links = wikipage.internal_links
        w_text = wikipage.wikitext()
        wikilink_rx = re.compile(r'\[\[([^|\]]*\|)?([^\]]+)\]\]')
        # link_array = []
        for m in wikilink_rx.finditer(w_text):
            # if len(link_array) >= num:
            # break
            if m.group(1) is not None:
                if "Image" in m.group(1) or "Template" in m.group(1) or \
                                "File" in m.group(1):
                    continue
                link = m.group(1)[:-1]
                yield link
            else:
                if "Image" in m.group(2) or "Template" in m.group(2) or \
                                "File" in m.group(2):
                    continue
                link = m.group(2)
                yield link
                # return link_array

    @staticmethod
    def content_categories(wikipage, num):
        """
        request categories, and remove the hidden/tracking categories which are not content categories
        :param wikipage:
        :param num:
        :return:
        """
        # TODO:: http://www.mediawiki.org/wiki/API:Categorymembers
        categories = wikipage.content_categories
        print categories
        prereqs = []
        for cat in categories:
            if 'articles that' in cat.lower():
                continue
            yield cat

    @staticmethod
    def article_sentences(wikipage):
        if type(wikipage) is wikipedia.WikipediaPage:
            content = wikipage.content
            nlutil = NlpUtil()
            sentences = nlutil.punkt_tokenize(content)
        else:
            sentences = []  # TODO::
        return sentences