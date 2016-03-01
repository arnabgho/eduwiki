from xml.etree import ElementTree
from boto.mturk.connection import MTurkConnection
from boto.mturk.price import Price
from boto.mturk.question import ExternalQuestion
from boto.mturk.connection import BaseAutoResultElement
from django.template.loader import render_to_string
from datetime import datetime, timedelta


def connect_mturk(sandbox=True):
    configure_file = ElementTree.parse('mturk_config.xml')
    configure_root = configure_file.getroot()

    ACCESS_ID = configure_root.find('Mturk').find('Access_Key_ID').text
    SECRET_KEY = configure_root.find('Mturk').find('Secret_Access_Key').text

    if sandbox:
        HOST = 'mechanicalturk.sandbox.amazonaws.com'
    else:
        HOST = 'mechanicalturk.amazonaws.com'

    mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                          aws_secret_access_key=SECRET_KEY,
                          host=HOST)
    return mtc


def create_hit_question(question_url, sandbox=True, max_assignments=2,
                        reward=0.1):
    mtc = connect_mturk(sandbox=sandbox)

    # --------------- META INFO -------------------
    external_question = ExternalQuestion(external_url=question_url,
                                         frame_height=900)

    title = 'Answer multiple-choice questions'
    description = 'Answer the multiple-choice questions of various topics, ' \
                  'and give explanations. ' \
                  'You do not need to know a lot about the question topics. ' \
                  '[Please use the newest version Chrome on your computer to ' \
                  'take this HIT. Other environments may cause error.]'

    # title = 'Inspect multiple-choice question qualities'
    # description = 'Answer the multiple-choice questions of various topics, ' \
    # 'and inspect the qualities of them. ' \
    # 'You do not need to know about the question topics.'


    keywords = 'multiple-choice question, learning, quality inspection'

    # --------------- CREATE THE HIT -------------------
    hit_create_result = mtc.create_hit(question=external_question,
                                       max_assignments=max_assignments,
                                       title=title,
                                       description=description,
                                       keywords=keywords,
                                       duration=timedelta(minutes=60),
                                       # larger than 30 secs
                                       lifetime=timedelta(days=3),
                                       reward=reward)  # in USD
    result = hit_create_result[0] \
        if hit_create_result[0].IsValid == 'True' else None
    if not result:
        raise ValueError("ERROR: Failed to create HIT.")
    return result


class BonusPayment(BaseAutoResultElement):
    # def __init__(self, connection):
    #     self.amount = -1
    #     self.currency_code = 'USD'
    #     self.formatted_price = ''
    #     self.woker_id = ''
    #     self.assignment_id = ''

    def endElement(self, name, value, connection):
        if name == 'Amount':
            self.amount = float(value)
        elif name == 'CurrencyCode':
            self.currency_code = value
        elif name == 'FormattedPrice':
            self.formatted_price = value
        elif name == 'AssignmentId':
            self.assignment_id = value
        elif name == 'WorkerId':
            self.woker_id = value
        else:
            setattr(self, name, value)


def get_bonus_payments(mtc=connect_mturk(), assignment_id=None, hit_id=None):
    if not assignment_id and not hit_id:
        return -1
    if assignment_id:
        params = {'AssignmentId': assignment_id}
    else:
        params = {'HITId': hit_id}
    params['Operation'] = 'GetBonusPayments'
    http_request = mtc.build_base_http_request(
        'POST', '/', None, params, {}, '', mtc.host)
    http_request.params['Version'] = '2014-08-15'
    response = mtc._mexe(http_request)
    return mtc._process_response(
        response, marker_elems=[('BonusPayment', BonusPayment)])


def expire_hit(question_hit_id, sandbox=True):
    mtc = connect_mturk(sandbox=sandbox)
    return mtc.expire_hit(hit_id=question_hit_id)


def test():
    result = create_hit_question(
        question_url="https://crowdtutor.info/autoassess"
                     + "/single_question?q=Reinforcement+learning",
        sandbox=True)
    print result


if __name__ == "__main__":
    test()