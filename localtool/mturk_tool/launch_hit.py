__author__ = 'moonkey'

import os.path
import requests
from localtool.mturk_tool.botowrapper import *


def create_hit_for_topic(topic, sandbox=True, max_assignments=2):
    return create_hit_question(
        question_url="https://crowdtutor.info/autoassess/single_question?q="
                     + str(topic),
        sandbox=sandbox,
        max_assignments=max_assignments
    )


def create_for_experiment(topic_filename,
                          topic_max_num=5, start_idx=0,
                          sandbox=True, visit_question_generation_link=True,
                          max_assignments=2):
    topics = []
    with open(topic_filename, "rU") as topic_file:
        topic_num = 0
        cat_line = False
        for t in topic_file.readlines():
            if topic_num >= topic_max_num:
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

    sandbox_prefix = 'sandbox_' if sandbox else ""
    output_file = None
    if not os.path.exists(sandbox_prefix + topic_filename + ".out.txt"):
        output_file = open(sandbox_prefix + topic_filename + ".out.txt", "w")
    else:
        for idx in range(0, 100):
            filename = sandbox_prefix + topic_filename \
                + "_" + str(idx) + ".out.txt"
            if not os.path.exists(filename):
                continue
            else:
                output_file = open(filename, "w")
                break
    if not output_file:
        print "No output file; Quitting..."
        return

    for idx, t in enumerate(topics):
        if idx < start_idx:
            continue
        if visit_question_generation_link:
            a = t.replace(' ', '+')
            print 'visiting: ' + t
            link = "https://crowdtutor.info/autoassess/quiz/?q=" + a + "&f=T"
            r = requests.get(link)
            if not r:
                print "bad_link"
                continue  # skip HIT creation for this question
        try:
            create_hit_result = create_hit_for_topic(
                t, sandbox=sandbox, max_assignments=max_assignments)
            creat_hit_info = t + " : " + str(create_hit_result.HITId)
            print creat_hit_info
            output_file.write(creat_hit_info + "\n")
        except Exception, e:
            print t + "failed to create."
            print e
            # raise e
    output_file.close()


if __name__ == "__main__":
    create_for_experiment(
        topic_filename="90_topics.txt",
        sandbox=True,
        topic_max_num=3, max_assignments=3,
        visit_question_generation_link=False
    )