__author__ = 'moonkey'

from xml.etree import ElementTree
from autoassess.models import *


def read_social_psych_quiz(quiz_xml):
    """
    A one-time function for adding some social psychology quizzes into the db
    :param quiz_xml:
    :return:
    """
    root = ElementTree.parse(quiz_xml).getroot()
    data_node = None
    for child in root:
        if child.tag == 'data':
            data_node = child
    for question_group in data_node[0]:
        preamble = question_group[0]
        if preamble._children:
            print 'preamble', preamble

        question_data_node = question_group[1][1]
        question_xml_id = question_group[1].attrib['id']
        print question_xml_id

        question_text_node = question_data_node[0]
        question_text = question_text_node.text.rstrip('\n')

        if question_text.endswith("<br> <br>"):
            question_text = question_text[
                            :len(question_text) - len("<br> <br>")]
        elif question_text.endswith('<br><br>'):
            question_text = question_text[:len(question_text) - len('<br><br>')]
        # else:
        # print question_text

        question_text = question_text.rstrip("\n")
        #############
        # question_explanation_node = question_node[1]
        question_option_groups_node = question_data_node[2]
        options_node = question_option_groups_node[0]

        option_texts = []
        correct_ans = -1
        for option_idx, option_node in enumerate(options_node):
            option_texts.append(option_node[0].text)
            if option_node.attrib['selected_score'] == '1':
                correct_ans = option_idx

        print question_text
        print option_texts, correct_ans

        question_obj = WikiQuestion(
            type='MANUAL',
            topic='SocialPsych' + question_xml_id,
            quiz_topic="Social psychology",
            question_text=question_text,
            choices=option_texts,
            correct_answer=correct_ans,
            version=-1.0,
        )
        # question_obj.save()


if __name__ == '__main__':
    from mongoengine import connect
    connect('eduwiki_db')
    read_social_psych_quiz(
        quiz_xml='../../../../other_materials/quiz/Social_psych_quiz.xml')