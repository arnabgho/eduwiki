__author__ = 'moonkey'

import requests
import codecs
import time


def visit_eduwiki_link(version, local=True,
                       topic_max=200, start=0,
                       filename="../../../random/topics/topic.txt"):
    topics = []
    with open(filename, "rU") as topic_file:
        topic_num = 0
        cat_line = False
        for t in topic_file.readlines():
            if t.startswith("#"):
                print "Skip:", t
                continue
            if topic_num >= topic_max:
                break
            if cat_line:
                cat_line = False
                print "Cat:", t
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

    print "version:", version

    success_time = 0
    fail_time = 0
    success_count = 0
    fail_count = 0

    for idx, t in enumerate(topics):
        if idx < start:
            continue
        print "visiting topic:" + t
        temp = t.replace(' ', '+')

        link = dn + "/autoassess/quiz/?q=" + temp + \
               "&v=" + str(version) \
               + "&pre=T"
        # + "&f=T"
        start = time.time()
        r = requests.get(link)
        end = time.time()
        if r:
            print idx, "good_link", end - start
            success_count += 1
            success_time += end - start
        else:
            print idx, "bad_link >>>>>>>>>>>>>>>>>>>>>>>>>"
            fail_count += 1
            fail_time += end - start
        print success_count, fail_count, \
            success_time / success_count, fail_time / fail_count


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

    with open(filename + str(version) + "links.html", 'w') as page_file:
        page_file.write(html)


if __name__ == "__main__":
    # TODO:: (1)set correct topic file, (2) check correct link format in func

    # visit_topic_file = "../mturk_tool/experiment_data/experiment_topics.txt"
    # visit_topic_file = "../mturk_tool/experiment_data/quiz_topics.txt"
    # visit_topic_file = "../mturk_tool/experiment_data/done_topics.txt"
    # visit_topic_file = "./1000topics.txt"
    visit_topic_file = "./featured_articles.txt"

    visit_eduwiki_link(
        version=0.25, local=True,  # local always True if db synced
        start=400, topic_max=500,
        filename=visit_topic_file)
    #
    # print_eduwiki_links(
    # version=-1.0, local=False,
    #     start=0, topic_max=100,
    #     filename=visit_topic_file)

    # visit_eduwiki_link(
    #     version=0.24, local=True,  # local always True if db synced
    #     start=0, topic_max=100,
    #     filename=visit_topic_file)

    # print_eduwiki_links(
    #     version=0.24, local=True,
    #     start=0, topic_max=100,
    #     filename=visit_topic_file)
