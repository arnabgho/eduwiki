__author__ = 'moonkey'

from autoassess.diagnose.prereqsearch.related_concept import \
    most_mentioned_wikilinks
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
import codecs


def test(filename, topic_max=200, start=0):
    topics = []
    with open(filename, "rU") as topic_file:
        topic_num = 0
        cat_line = False
        for t in topic_file.readlines():
            if topic_num >= topic_max:
                break
            if cat_line:
                cat_line = False
                print "Cat:" + t
                continue

            t = t.strip('\n')
            if t.replace(" ", "") != "":
                topics.append(t)
                topic_num += 1
            else:
                cat_line = True
    related_list = []
    for idx, t in enumerate(topics):
        if idx < start:
            continue

        wikipage = WikipediaWrapper.page(t)
        candidate_topics, alias = most_mentioned_wikilinks(wikipage)
        related_list.append((t, candidate_topics[:5]))
        print "Finding related topics for:", t, candidate_topics[:5]
    output_file = codecs.open("related_topics.csv", 'w', encoding='utf-8')
    for rc in related_list:
        try:
            print rc
            line = rc[0] + u',' + u",".join([r[0] for r in rc[1]]) + u"\n"
            output_file.write(line)
        except Exception as e:
            print e
            print "something went wrong"

    output_file.close()


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    test("../mturk_tool/experiment_data/experiment_topics.txt")
