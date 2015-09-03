__author__ = 'moonkey'

import requests
import codecs


def visit_eduwiki_link(version, local=True,
                       topic_max=200, start=0,
                       filename="../../../random/topics/topic.txt"):
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

    if local:
        dn = "http://localhost:8000"
    else:
        dn = "https://crowdtutor.info"

    for idx, t in enumerate(topics):
        if idx < start:
            continue
        print "visiting topic:" + t
        temp = t.replace(' ', '+')

        link = dn + "/autoassess/quiz/?q=" + temp + \
               "&v=" + str(version) \
               + "&pre=T"
               # + "&f=T"
        r = requests.get(link)
        if r:
            print idx, "good_link"
        else:
            print idx, "bad_link >>>>>>>>>>>>>>>>>>>>>>>>>"


def print_eduwiki_links(version, local=True,
                        topic_max=200, start=0,
                        filename="../../../random/topics/topic.txt"):
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

    if local:
        dn = "http://localhost:8000"
    else:
        dn = "https://crowdtutor.info"

    html = "<html><body>\n"
    for idx, t in enumerate(topics):
        if idx < start:
            continue
        print "visiting topic:" + t
        temp = t.replace(' ', '+')

        link = dn + "/autoassess/quiz/?q=" + temp + \
               "&v=" + str(version)
        lstr = '<a href="' + link + '" target="_blank">' + t + "</a><br>"
        html += lstr + '\n'

    html += "</body></html>"

    with open(filename + ".html", 'w') as page_file:
        page_file.write(html)


if __name__ == "__main__":
    # visit_eduwiki_link(version=0.2,
    # local=False, start=0, topic_max=200)

    # visit_topic_file = "../mturk_tool/experiment_data/IRT_topics.txt"
    visit_topic_file = "../mturk_tool/experiment_data/experiment_topics.txt"
    visit_eduwiki_link(
        version=0.24, local=True,
        start=0, topic_max=50,
        filename=visit_topic_file)
    # print_eduwiki_links(
    #     version=0.22, local=True,
    #     start=0, topic_max=50,
    #     filename=visit_topic_file)
