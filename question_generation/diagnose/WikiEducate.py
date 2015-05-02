import os
import tempfile
import time
import hashlib
import wikipedia
import re
import json
import sys
import unicodedata


class WikiEducate:
    def __init__(self, topic, cache=True, autosuggest=True):
        self.topic = topic
        self.cache = cache
        self.fetcher = DiskCacheFetcher('url_cache')
        self.page = wikipedia.page(self.topic, auto_suggest=autosuggest)

    # def wikitext(self):
    # text = self.page.wikitext()
    # return text

    def wiki_links(self, num):
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

    def plain_text_summary(self, n=2):
        """
        :param n: max paragraph number
        :return: (up to) first n paragraphs of given Wikipedia article.
        """
        cached = self.cache and self.fetcher.fetch(self.topic + "-plainTextSummary")
        if cached:
            page_content = cached
        else:
            self.page = wikipedia.page(self.topic)
            page_content = self.page.content
            self.fetcher.cache(self.topic + "-plainTextSummary", page_content)
        first_n_paragraphs = "\n".join(page_content.split("\n")[:n])
        return first_n_paragraphs


    def top_wiki_links(self, n=2):
        """
        Returns an array of article titles for wiki links within given wiki text.
        :param n:
        :return:
        """
        cached = self.cache and self.fetcher.fetch(self.topic + "-links")
        if cached:
            links = json.loads(cached)
        else:
            self.page = wikipedia.page(self.topic)
            links = self.page.links
            self.fetcher.cache(self.topic + "-links", json.dumps(links))
        return links

    # Returns an array of category titles
    def category_titles(self):
        cached = self.cache and self.fetcher.fetch(self.topic + "-categories")
        if cached:
            categories = json.loads(cached)
        else:
            self.page = wikipedia.page(self.topic)
            categories = self.page.categories
            self.fetcher.cache(self.topic + "-categories",
                               json.dumps(categories))
        return categories

    def return_what_is(self):
        """
        "<topic>\s[^\.](is|was)([^\.])+\." or None (if no matches)
        :return: first mention in article of the following regex
        """
        cached = self.cache and self.fetcher.fetch(self.topic + "-whatis")
        if cached:
            what_is = cached
        else:
            self.page = wikipedia.page(self.topic)
            regex_str = '(' + self.topic[:5] + '(' + self.topic[5:] + ')?' + '|' + '(' + self.topic[:len(
                self.topic) - 5] + ')?' + self.topic[len(
                self.topic) - 5:] + ')' + '(\s[^\.]*(is|was|can be regarded as)|[^,\.]{,15}?,)\s([^\.]+)\.(?=\s)'
            mentions = re.findall(regex_str, self.page.content, re.IGNORECASE)

            what_is = mentions[0][5]
            what_is = re.sub(r'.*\sis\s+(.*)$', r'\1', what_is)
            if not mentions:
                what_is = "can't find a good description"
            self.fetcher.cache(self.topic + "-whatis", what_is)
        return what_is


class DiskCacheFetcher:
    def __init__(self, cache_dir=None):
        # If no cache directory specified, use system temp directory
        if cache_dir is None:
            cache_dir = tempfile.gettempdir()
        self.cache_dir = cache_dir

    def fetch(self, url, max_age=60000):
        # Use MD5 hash of the URL as the filename
        filename = hashlib.md5(url).hexdigest()
        filepath = os.path.join(self.cache_dir, filename)
        if __name__ != "__main__":
            filepath = os.path.join('diagnose', filepath)
            filepath = os.path.join('question_generation', filepath)

        if os.path.exists(filepath):
            if int(time.time()) - os.path.getmtime(filepath) < max_age:
                return open(filepath).read()

        # if cache not found, simply return false
        return False

    def cache(self, url, data):
        # Use MD5 hash of the URL as the filename
        filename = hashlib.md5(url).hexdigest()
        filepath = os.path.join(self.cache_dir, filename)
        if __name__ != "__main__":
            filepath = os.path.join('diagnose', filepath)
            filepath = os.path.join('question_generation', filepath)

        fd, temppath = tempfile.mkstemp()
        fp = os.fdopen(fd, 'w')
        fp.write(data.encode("ascii", "ignore"))
        fp.close()
        os.rename(temppath, filepath)
        return data