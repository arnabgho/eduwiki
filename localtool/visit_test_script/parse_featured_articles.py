__author__ = 'moonkey'

from bs4 import BeautifulSoup
import requests


def parse_featured():
    featured_url = "https://en.wikipedia.org/wiki/Wikipedia:Featured_articles"
    featured_html = requests.get(featured_url).text
    soup = BeautifulSoup(featured_html, 'html.parser')

    links = soup.body.find_all('a')
    for l in links:
        print l


if __name__ == "__main__":
    parse_featured()