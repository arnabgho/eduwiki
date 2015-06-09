from diagnose.prereq import find_direct_prereq
from diagnose.wikipedia import WikipediaPage
# Create your tests here.
topics = []


def test():
    csvfile = open("../../../random/new.csv", "rU")
    for c in csvfile.readlines():
        topic = c.split(",")[0]
        # print topic
        topics.append(topic)

    # edufile = open("../../../random/eduwiki.csv", "w")
    #
    # for t in topics:
    # wikipage = WikipediaPage(title=t)
    # pres = find_direct_prereq(wikipage, 3)
    #     line = t + ","
    #     for p in pres:
    #         line += p + ";"
    #     edufile.write(line + "\n")
    # edufile.close()

    linkfile = open("../../../random/link.csv", "w")
    for t in topics:
        a = t.replace(' ', '+')
        link = "https://eduwiki.ml/autoassess/quiz/?q=" + a
        linkfile.write(t + "," + link + "\n")
    linkfile.close()

    csvfile.close()


# TODO:: deal with the unicode issue, deal with the redirect, (inside the code)
# TODO:: # find the positions of the manually selected prereqs. (here)

if __name__ == '__main__':
    test()