from autoassess.diagnose.quesgen.distractor.distractor_source \
    import similar_page_titles_of_samecat
from autoassess.diagnose.util.wikipedia_util import WikipediaWrapper
import codecs


def test_word2vec_model(start=0, topic_max=200, filename=""):
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

    sim_title_tuples = []
    for idx, t in enumerate(topics):
        if idx < start:
            continue
        print "visiting topic:" + t
        page_t = WikipediaWrapper.page(title=t)
        sim_titles = similar_page_titles_of_samecat(page_t)
        sim_title_tuples.append((page_t.title, sim_titles))
        # print t, sim_titles

    output_file = codecs.open("sim_titles.csv", 'w', encoding='utf-8')
    for t in sim_title_tuples:
        try:
            print t[0]
            print t[1]
            line = t[0] + u',' + u",".join(t[1]) + u"\n"
            output_file.write(line)
        except Exception as e:
            print e
            print "something went wrong"

    output_file.close()
    return sim_title_tuples


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    test_word2vec_model(
        start=0, topic_max=50,
        filename="../mturk_tool/experiment_data/experiment_topics.txt")
