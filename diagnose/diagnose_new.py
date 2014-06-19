import md5, os, tempfile, time
import wikipedia
import re
import json
import sys
import array
import unicodedata

class EduTopic:
    def __init__(self, name, distractors, description):
        self.name = name
        self.distractors = distractors
        self.description = description
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class WikiEducate:
    def __init__(self, topic, cache=True):
        self.topic = topic
        self.cache = cache
        self.fetcher = DiskCacheFetcher('url_cache')

    def wikitext(self):
        self.page = wikipedia.page(self.topic)
        wiki_content = self.page.wikitext()
        return wiki_content

    def wikilinks(self):
        wtext = self.wikitext()
        #print wtext
        wikilink_rx = re.compile(r'\[\[([^|\]]*\|)?([^\]]+)\]\]')
        link_array = []
        for m in wikilink_rx.finditer(wtext):
            #print '%02d-%02d: %s' % (m.start(), m.end(), m.group(2))
            link_array.append(m.group(2))

        return link_array


    # Returns (up to) first n paragraphs of given Wikipedia article.
    def plainTextSummary(self, n=2):
        cached = self.cache and self.fetcher.fetch(self.topic+"-plainTextSummary")
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
            self.fetcher.cache(self.topic+"-categories", json.dumps(categories))
        return categories

    # Returns first mention in article of the following regex
    # "<topic>\s[^\.](is|was)([^\.])+\." or None (if no matches)
    def returnWhatIs(self):
        cached = self.cache and self.fetcher.fetch(self.topic+"-whatis")
        if cached:
            whatis = cached
        else:
            self.page = wikipedia.page(self.topic)
            print self.topic + "||" + self.topic[:7] + "||" + self.page.content[:200] + "\n"
            regex_str = '('+self.topic[:5]+'('+self.topic[5:]+')?'+'|'+'('+self.topic[:len(self.topic)-5]+')?'+self.topic[len(self.topic)-5:] + ')' + '(\s[^\.]*(is|was|can be regarded as)|[^,\.]{,15}?,)\s([^\.]+)\.(?=\s)'
            print regex_str + "\n"
            mentions = re.findall(regex_str, self.page.content, re.IGNORECASE)

            if len(mentions) > 0:
                whatis = mentions[0][5]
                whatis = re.sub(r'.*\sis\s+(.*)$', r'\1', whatis)
            else:
                whatis = None
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
        filename = md5.new(url).hexdigest()
        filepath = os.path.join(self.cache_dir, filename)
        if os.path.exists(filepath):
            if int(time.time()) - os.path.getmtime(filepath) < max_age:
                return open(filepath).read()

        #if cache not found, simply return false
        return False
        
    def cache(self, url, data):
        # Use MD5 hash of the URL as the filename
        filename = md5.new(url).hexdigest()
        filepath = os.path.join(self.cache_dir, filename)

        fd, temppath = tempfile.mkstemp()
        fp = os.fdopen(fd, 'w')
        fp.write(data.encode("ascii", "ignore"))
        fp.close()
        os.rename(temppath, filepath)
        return data

#  An example query.
main_topic = WikiEducate(sys.argv[1], True)
prereqs = main_topic.wikilinks()

my_json = []

for i in range(0, 4):
    print "Investigating " + prereqs[i] + "\n"
    topic_name = unicodedata.normalize('NFKD', prereqs[i]).encode('ascii', 'ignore')
    topic = WikiEducate(topic_name, True)
    description = topic.returnWhatIs()
    distractors = topic.wikilinks()
    distractor_defs = []
    for j in range(0,3):
        distractor_name = unicodedata.normalize('NFKD', distractors[j]).encode('ascii', 'ignore')
        distractor = WikiEducate(distractor_name, True)
        distractor_description = distractor.returnWhatIs()
        distractor_defs.append(distractor_description)
        print "D: " + distractor_name + "=" + distractor_description + "\n"
    print prereqs[i] + ": " + description + "\n"
    topic_text = topic.plainTextSummary(1)
    print "TOPIC TEXT" + topic_text + "\n\n";
    print "\n"
    #topic_learner = EduTopic(topic_name, distractor_defs, topic_text)
    #my_json.append(topic_learner)
    my_json.append({'name': topic_name, 'def': description,'distractors': distractor_defs, 'text': topic_text})

print json.dumps(my_json)

#print wikitext

#summary = wikieducate.plainTextSummary()
#links = wikieducate.topWikiLinks()
#categories = wikieducate.categoryTitles()
#first_mention = wikieducate.returnWhatIs()

#print "Summary:", summary
#print
#print "Links:", links
#print
#print "Categories:", categories
#print
#print "First Mention:", first_mention
