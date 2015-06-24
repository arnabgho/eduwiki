__author__ = 'moonkey'

from botowrapper import *
import requests


def create_hit_for_topic(topic, sandbox=True):
    return create_hit_question(
        question_url="https://crowdtutor.info/autoassess/single_question?q=" + str(topic),
        sandbox=sandbox
    )


def create_for_experiment(topic_file_name="experiment_topics.txt",
                          topic_max_idx=5, start_idx=0,
                          sandbox=True, visit_question_generation_link=True):
    topics = []
    with open(topic_file_name, "rU") as topic_file:
        topic_num = 0
        cat_line = False
        for t in topic_file.readlines():
            if topic_num >= topic_max_idx:
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

    output_file = open(topic_file_name + ".out.txt", "w")
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
            create_hit_result = create_hit_for_topic(t, sandbox=sandbox)
            creat_hit_info = t + " : " + str(create_hit_result.HITId)
            print creat_hit_info
            output_file.write(creat_hit_info + "\n")
        except Exception, e:
            print t + "failed to create."
            print e
            # raise e
    output_file.close()


if __name__ == "__main__":
    create_for_experiment(topic_max_idx=1, sandbox=True, visit_question_generation_link=False)