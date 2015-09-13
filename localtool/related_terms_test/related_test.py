__author__ = 'moonkey'

from autoassess.diagnose.prereqsearch.related_concept import \
    most_mentioned_wikilinks, similarly_covered_topics
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
import codecs
import sys


def test(filename, topic_max=200, start=0, sim_method=most_mentioned_wikilinks):
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
        try:
            candidate_topics, alias = sim_method(wikipage, with_count=True)
            related_list.append((t, candidate_topics[:10]))
            print "Finding related topics for:", t, candidate_topics[:10]
        except Exception as e:
            print >> sys.stderr, e, t
    output_file = codecs.open("related_topics.csv", 'w', encoding='utf-8')
    for rc in related_list:
        try:
            print rc
            line = rc[0] + u',' + u",".join([r[0] for r in rc[1]]) + u"\n"
            # line = rc[0] + u',' + u",".join([r for r in rc[1]]) + u"\n"
            output_file.write(line)
        except Exception as e:
            print e
            print "something went wrong"

    output_file.close()


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    test("../mturk_tool/experiment_data/quiz_topics.txt",
         topic_max=200, start=0,
         sim_method=most_mentioned_wikilinks)
