__author__ = 'moonkey'

import requests


def generate_eduwiki_link(local=True, topic_max=200, start=0):
    topics = []
    with open("../../../random/topics/topic.txt", "rU") as topic_file:
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

    if local:
        dn = "http://localhost:8000"
    else:
        dn = "https://crowdtutor.info"

    for idx, t in enumerate(topics):
        if idx < start:
            continue
        print "visiting topic:" + t
        a = t.replace(' ', '+')

        link = dn + "/autoassess/quiz/?q=" + a + "&f=T"
        r = requests.get(link)
        if r:
            print idx, "good_link"
        else:
            print idx, "bad_link"


if __name__ == "__main__":
    generate_eduwiki_link(local=False, start=0, topic_max=10)