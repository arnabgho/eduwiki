import md5, os, tempfile, time
import urllib
import urllib2
import json
from BeautifulSoup import BeautifulSoup


class WikiEducate:
    cache_refresh = 100000
    base_url = "http://en.wikipedia.org/w/api.php"

    def __init__(self, topic):
    	self.fetcher = DiskCacheFetcher('url_cache')
    	self.topic = topic

    # Returns (up to) first n paragraphs of given Wikipedia article.
    def plainTextSummary(self, n=2):
        topic_quoted = urllib.quote(self.topic)

        # This illustrates how to use the code we alerady have, but it
        # isn't the desired functionality.
        fetcher = DiskCacheFetcher('url_cache')
        url = self.createURL("json", "query", topic_quoted, "extracts")
        data = fetcher.fetch(url, self.cache_refresh)
        print data
        json_obj = json.loads(data)


        return

    # Returns an array of article titles for wiki links within given wiki text.
    def topWikiLinks(self):
        return

    # Returns an array of category titles
    def categoryTitles(self):
    	return

    # Returns first mention in article of the following regex
    # "<topic>\s[^\.](is|was)([^\.])+\." or None (if no matches)
    def returnWhatIs(self):
    	return


    def createURL(self, format="", action="", titles="", prop=""):
        return self.base_url + "?format=" + format + "&action=" + action + "&titles=" + titles + "&prop=" + prop


class DiskCacheFetcher:
    def __init__(self, cache_dir=None):

        # If no cache directory specified, use system temp directory
        if cache_dir is None:
            cache_dir = tempfile.gettempdir()
        self.cache_dir = cache_dir
    def fetch(self, url, max_age=0):
        # Use MD5 hash of the URL as the filename
        filename = md5.new(url).hexdigest()
        filepath = os.path.join(self.cache_dir, filename)
        if os.path.exists(filepath):
            if int(time.time()) - os.path.getmtime(filepath) < max_age:
                return open(filepath).read()

        # Retrieve over HTTP and cache, using rename to avoid collisions
        data = urllib.urlopen(url).read()

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this

        resource = opener.open(url)
        data = resource.read()
        resource.close()

        fd, temppath = tempfile.mkstemp()
        fp = os.fdopen(fd, 'w')
        fp.write(data)
        fp.close()
        os.rename(temppath, filepath)
        return data


#  An example query.
wikieducate = WikiEducate("Albert Einstein")
data = wikieducate.plainTextSummary()

print data