import os
import tempfile
import time
import hashlib
import wikipedia
import re
import json
import sys
import unicodedata


# takes a search term and, optionally, a depth and branch factor, and returns a
# JSON tree representing the term's article, with its prereqs and quiz items as
# well as those of the prereqs, and of their prereqs, etc.
def query(search_term, depth=1, children=3):
    # set a max depth and branching factor as a failsafe
    if depth > 6:
        depth = 6
    if children > 6:
        children = 6

    # get the topic and the names of its prereq links
    main_topic = WikiEducate(normal(search_term))
    prereqs = main_topic.wikilinks(children)
    topic_name = main_topic.page.title

    # create a JSON tree which will be recursively built
    json_children = []

    # get topic text, descriptor, and distractors
    # note: I'm referring to the actual string of text as the distractor
    topic_text = main_topic.plainTextSummary(1)
    description = main_topic.returnWhatIs()
    distractor_names = main_topic.wikilinks(children)
    distractors = []
    for i in range(0, 3):
        distractor_name = normal(distractor_names[i])
        distractor_obj = WikiEducate(distractor_name)
        distractor = distractor_obj.returnWhatIs()
        distractors.append(distractor)  # append dis tractor *vroom*

    # run for children if depth left
    if depth != 0:
        for j in range(0, children):
            json_child = query(prereqs[j], depth=depth - 1, children=children)
            json_children.append(json_child)

    # assemble the tree and return it
    json_tree = {'title': topic_name, 'text': topic_text,
                 'description': description, 'distractors': distractors,
                 'children': json_children}
    return json.dumps(json_tree)


def normal(text):
    try:
        return unicodedata.normalize('NFKD', text).encode('ascii')
    except UnicodeEncodeError as u:
        return "ascii"


def getpage(topic):
    return WikiEducate(topic)


def getpage_exact(topic):
    return WikiEducate(topic, autosuggest=False)


class WikiEducate:
    def __init__(self, topic, cache=True, autosuggest=True):
        self.topic = topic
        self.cache = cache
        self.fetcher = DiskCacheFetcher('url_cache')
        self.page = wikipedia.page(self.topic, auto_suggest=autosuggest)

    def wikitext(self):
        text = self.page.wikitext()
        return text

    def wikilinks(self, num):
        wtext = self.wikitext()
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

    # Returns (up to) first n paragraphs of given Wikipedia article.
    def plainTextSummary(self, n=2):
        cached = self.cache and \
            self.fetcher.fetch(self.topic+"-plainTextSummary")
        if cached:
            page_content = cached
        else:
            self.page = wikipedia.page(self.topic)
            page_content = self.page.content
            self.fetcher.cache(self.topic+"-plainTextSummary", page_content)
        first_n_paragraphs = "\n".join(page_content.split("\n")[:n])
        return first_n_paragraphs

    # Returns an array of article titles for wiki links within given wiki text.
    def topWikiLinks(self, n=2):
        cached = self.cache and self.fetcher.fetch(self.topic+"-links")
        if cached:
            links = json.loads(cached)
        else:
            self.page = wikipedia.page(self.topic)
            links = self.page.links
            self.fetcher.cache(self.topic+"-links", json.dumps(links))
        return links

    # Returns an array of category titles
    def categoryTitles(self):
        cached = self.cache and self.fetcher.fetch(self.topic+"-categories")
        if cached:
            categories = json.loads(cached)
        else:
            self.page = wikipedia.page(self.topic)
            categories = self.page.categories
            self.fetcher.cache(self.topic+"-categories",
                               json.dumps(categories))
        return categories

    # Returns first mention in article of the following regex
    # "<topic>\s[^\.](is|was)([^\.])+\." or None (if no matches)
    def returnWhatIs(self):
        cached = self.cache and self.fetcher.fetch(self.topic+"-whatis")
        if cached:
            whatis = cached
        else:
            self.page = wikipedia.page(self.topic)
            regex_str = '('+self.topic[:5]+'('+self.topic[5:]+')?'+'|'+'('+self.topic[:len(self.topic)-5]+')?'+self.topic[len(self.topic)-5:] + ')' + '(\s[^\.]*(is|was|can be regarded as)|[^,\.]{,15}?,)\s([^\.]+)\.(?=\s)'
            mentions = re.findall(regex_str, self.page.content, re.IGNORECASE)

            whatis = mentions[0][5]
            whatis = re.sub(r'.*\sis\s+(.*)$', r'\1', whatis)
            if not mentions:
                whatis = "can't find a good description"
            self.fetcher.cache(self.topic+"-whatis", whatis)
        return whatis


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
            filepath = os.path.join('eduprototype', filepath)

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
            filepath = os.path.join('eduprototype', filepath)

        fd, temppath = tempfile.mkstemp()
        fp = os.fdopen(fd, 'w')
        fp.write(data.encode("ascii", "ignore"))
        fp.close()
        os.rename(temppath, filepath)
        return data
