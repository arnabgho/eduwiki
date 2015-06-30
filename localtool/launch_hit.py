__author__ = 'moonkey'

from botowrapper import *
import requests
import os.path


def create_hit_for_topic(topic, sandbox=True, max_assignments=2):
    return create_hit_question(
        question_url="https://crowdtutor.info/autoassess/single_question?q=" + str(topic),
        sandbox=sandbox,
        max_assignments=max_assignments
    )


def create_for_experiment(topic_file_name="experiment_topics.txt",
                          topic_max_num=5, start_idx=0,
                          sandbox=True, visit_question_generation_link=True,
                          max_assignments=2):
    topics = []
    with open(topic_file_name, "rU") as topic_file:
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
    if not os.path.exists(sandbox_prefix + topic_file_name + ".out.txt"):
        output_file = open(sandbox_prefix + topic_file_name + ".out.txt", "w")
    else:
        for idx in range(0, 100):
            if not os.path.exists(sandbox_prefix + topic_file_name + "_" + str(idx) + ".out.txt"):
                continue
            else:
                output_file = open(sandbox_prefix + topic_file_name + "_" + str(idx) + ".out.txt", "w")
                break

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
            create_hit_result = create_hit_for_topic(t, sandbox=sandbox, max_assignments=max_assignments)
            creat_hit_info = t + " : " + str(create_hit_result.HITId)
            print creat_hit_info
            output_file.write(creat_hit_info + "\n")
        except Exception, e:
            print t + "failed to create."
            print e
            # raise e
    output_file.close()


if __name__ == "__main__":
    create_for_experiment(topic_max_num=3, sandbox=True, visit_question_generation_link=False,
                          max_assignments=3)