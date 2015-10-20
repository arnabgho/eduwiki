__author__ = 'moonkey'

from bs4 import BeautifulSoup
import requests
import codecs


def parse_featured():
    featured_url = "https://en.wikipedia.org/wiki/Wikipedia:Featured_articles"
    featured_html = requests.get(featured_url).text
    soup = BeautifulSoup(featured_html, 'html.parser')

    links = soup.body.find_all('a')
    pre_links_end = False
    # post_links_start = False
    featured_titles = []
    for l in links:
        href = l.attrs.get('href', None)
        if href and href.startswith("#Warfare_biographies"):
            pre_links_end = True
            continue
        if pre_links_end:
            if href and not href.startswith('/wiki'):
                # post_links_start = True
                break
            # if not href.startswith('/wiki'):
            # print l.attrs['title'], href
            featured_titles.append(l.attrs['title'])
    print len(featured_titles)

    with codecs.open('featured_articles.txt', 'w', 'utf-8') as fa_file:
        for t in featured_titles:
            fa_file.write(t + '\n')


if __name__ == "__main__":
    parse_featured()