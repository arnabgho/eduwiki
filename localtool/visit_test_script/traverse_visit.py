__author__ = 'moonkey'

import requests
import codecs
import time
import logging
from autoassess.diagnose.util.wikimongo_model import WikiPageId


def traverse_eduwiki_link(version, local=True, topic_start=0):
    iter = 0
    logging.critical("Traversing all topics in database")

    logging.critical("Visiting local host?:" + str(local))
    if local:
        dn = "http://localhost:8000"
    else:
        dn = "https://crowdtutor.info"

    for art in WikiPageId.objects:
        iter += 1
        if iter < topic_start:
            continue
        art_id = art.id
        topic = art.page_title
        logging.info("Visiting" + str(art_id) + ' ' + topic)
        temp = topic.replace('_', '+')

        link = dn + "/autoassess/quiz_gen/?q=" + temp \
               + "&v=" + str(version) + "&pre=T"  # + "&f=T"
        start = time.time()
        try:
            r = requests.get(link)
            end = time.time()
            if r:
                logging.error(
                    str(art_id) + ",t" + str(end - start) + 's')
            else:
                logging.error(str(art_id) + ",f")
                # with codecs.open('./failures/' + topic + '.html',
                #                  'w', encoding='utf-8') as fail_html_file:
                #     fail_html_file.write(r.text)
        except requests.ConnectionError:
            logging.error(str(art_id) + "bad_link")


if __name__ == '__main__':
    from mongoengine import connect

    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s',
        filename='visit_all.log')

    connect('eduwiki_db', host='localhost')

    traverse_eduwiki_link(version=0.25, local=True)