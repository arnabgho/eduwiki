__author__ = 'moonkey'

import wikipedia_util

def remove_pages(filename, topic_max=200):
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

    for t in topics:
        print t
        print wikipedia_util.remove_article(t)


if __name__ == "__main__":
    from mongoengine import connect
    connect('eduwiki_db', host='localhost')

    remove_pages("./no_distractor_topics.txt")