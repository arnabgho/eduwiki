__author__ = 'moonkey'

from mongoengine import *
import traceback


class ErrorTopic(Document):
    topic = StringField(required=True)
    exception_msg = StringField(required=True)
    traceback_msg = StringField(required=True)


def save_error(topic, e):
    try:
        traceback_msg = traceback.format_exc()
        exception_msg = e.message
        et = ErrorTopic(
            topic=topic,
            exception_msg=exception_msg,
            traceback_msg=traceback_msg
        )
    except Exception:
        # should be a safe option without exception
        # do not want the main program to stall
        pass