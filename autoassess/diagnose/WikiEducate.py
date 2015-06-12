import os
import tempfile
import time
import hashlib
from util import wikipedia
import re
import json
import sys
import unicodedata
import time


class WikiEducate:
    def __init__(self, topic, cache=True, autosuggest=True):
        self.topic = topic
        self.cache = cache  # means whether to save in the db or not
        # try:
        #     self.page = WikipediaArticle.objects.filter(title=topic)[0]
        # except Exception:
        #     self.page = wikipedia.page(self.topic, auto_suggest=autosuggest)
        # TODO: need to make self.page all WikipediaArticle, not wikipedia.page at all

        # page_obj_construction_start = time.time()
        self.page = wikipedia.page(self.topic, auto_suggest=autosuggest)
        # page_obj_construction_end = time.time()
        # if __debug__:
        #     print str(page_obj_construction_end-page_obj_construction_start) + ","

    def find_prerequisite(self, num):
        """
        Based on the guess that the first few terms with wikipedia link
        will turn out to be background knowledge
        :param num:
        :return:
        """
        # TODO:: the heuristic actually needs to be changed
        # self.page = wikipedia.page(self.topic, auto_suggest=True)
        return self.linked_wiki_terms(num)

    def linked_wiki_terms(self, num):
        """
        :param num: the number of linked texts to return
        :return: list(strings), the first few texts that have a wikipedia hyper link
        """
        # TODO: use the page._links to match and find the first few links, maybe?
        # self.page = wikipedia.page(self.topic, auto_suggest=True)
        wtext = self.page.wikitext()
        # print wtext
        wikilink_rx = re.compile(r'\[\[([^|\]]*\|)?([^\]]+)\]\]')
        link_array = []
        for m in wikilink_rx.finditer(wtext):
            if len(link_array) > num:
                break
            if m.group(1) is not None:
                if "Image" in m.group(1) or "Template" in m.group(1) or \
                                "File" in m.group(1):
                    continue
                link_array.append(m.group(1)[:-1])
            else:
                if "Image" in m.group(2) or "Template" in m.group(2) or \
                                "File" in m.group(2):
                    continue
                link_array.append(m.group(2))
        return link_array

    def return_what_is(self):
        """
        "<topic>\s[^\.](is|was)([^\.])+\." or None (if no matches)
        :return: first mention in article of the following regex
        """
        # self.page = wikipedia.page(self.topic)
        # self.page = wikipedia.page(self.topic, auto_suggest=True)
        # TODO:: the number 5 must be hacked for a specific topic,
        # figure out what the regex is doing and make it general
        regex_str = '(' + self.topic[:5] + '(' + self.topic[5:] + ')?' + '|' + '(' + self.topic[:len(
            self.topic) - 5] + ')?' + self.topic[len(
            self.topic) - 5:] + ')' + '(\s[^\.]*(is|was|can be regarded as)|[^,\.]{,15}?,)\s([^\.]+)\.(?=\s)'
        mentions = re.findall(regex_str, self.page.content, re.IGNORECASE)

        if not mentions:
            what_is = "can't find a good description"
        else:
            what_is = mentions[0][5]
            what_is = re.sub(r'.*\sis\s+(.*)$', r'\1', what_is)

        return what_is

    def plain_text_summary(self, n=2):
        """
        TODO:: why not directly return the summary by API?
        :param n: max paragraph number
        :return: (up to) first n paragraphs of given Wikipedia article.
        """
        # cached = self.cache and self.fetcher.fetch(self.topic + "-plainTextSummary")
        # if cached:
        #     page_content = cached
        # else:
        #     self.page = wikipedia.page(self.topic)
        #     page_content = self.page.content
        #     self.fetcher.cache(self.topic + "-plainTextSummary", page_content)
        # first_n_paragraphs = "\n".join(page_content.split("\n")[:n])
        # return first_n_paragraphs
        # self.page = wikipedia.page(self.topic, auto_suggest=True)
        return self.page.summary

    # def top_wiki_links(self, n=2):
    #     """
    #     Returns an array of words for wiki links within given wiki text.
    #     :param n:
    #     :return: self.page.links
    #     """
    #     cached = self.cache and self.fetcher.fetch(self.topic + "-links")
    #     if cached:
    #         links = json.loads(cached)
    #     else:
    #         self.page = wikipedia.page(self.topic)
    #         links = self.page.links
    #         self.fetcher.cache(self.topic + "-links", json.dumps(links))
    #     return links

    # def category_titles(self):
    #     """
    #     :return: an array of category titles (self.page.categories)
    #     """
    #     cached = self.cache and self.fetcher.fetch(self.topic + "-categories")
    #     if cached:
    #         categories = json.loads(cached)
    #     else:
    #         self.page = wikipedia.page(self.topic)
    #         categories = self.page.categories
    #         self.fetcher.cache(self.topic + "-categories",
    #                            json.dumps(categories))
    #     return categories

# class DiskCacheFetcher:
#     def __init__(self, cache_dir=None):
#         # If no cache directory specified, use system temp directory
#         if cache_dir is None:
#             cache_dir = tempfile.gettempdir()
#         self.cache_dir = cache_dir
#
#     def fetch(self, url, max_age=60000):
#         # Use MD5 hash of the URL as the filename
#         filename = hashlib.md5(url).hexdigest()
#         filepath = os.path.join(self.cache_dir, filename)
#         if __name__ != "__main__":
#             filepath = os.path.join('diagnose', filepath)
#             filepath = os.path.join('autoassess', filepath)
#
#         if os.path.exists(filepath):
#             if int(time.time()) - os.path.getmtime(filepath) < max_age:
#                 return open(filepath).read()
#
#         # if cache not found, simply return false
#         return False
#
#     def cache(self, url, data):
#         # Use MD5 hash of the URL as the filename
#         filename = hashlib.md5(url).hexdigest()
#         filepath = os.path.join(self.cache_dir, filename)
#         if __name__ != "__main__":
#             filepath = os.path.join('diagnose', filepath)
#             filepath = os.path.join('autoassess', filepath)
#
#         fd, temppath = tempfile.mkstemp()
#         fp = os.fdopen(fd, 'w')
#         fp.write(data.encode("ascii", "ignore"))
#         fp.close()
#         os.rename(temppath, filepath)
#         return data