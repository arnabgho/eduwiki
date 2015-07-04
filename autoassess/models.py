import random

from mongoengine import *

# Create your models here.

# TODO:: rewrite all the cached terms to database
# TODO:: use mongodb... things are so easy


class WikiQuestion(Document):
    """
    save generated questions,
    """
    WikiQuestionType = (
        "WHAT_IS",
        # No other type so far. no need to
    )
    type = StringField(choices=WikiQuestionType)

    topic = StringField(required=True)
    question_text = StringField(required=True)  # question_stem

    # We can make the options a EmbeddedDocument if needed as we may want to
    # know and store how the options are generated.
    choices = ListField(StringField(), required=True)
    # by deafult, the first option is the right answer
    correct_answer = IntField(required=True)

    # for question generation
    version = FloatField(required=True)

    def __unicode__(self):
        return str(self.topic) + ":" + str(self.question_text)


class Prereq(Document):
    """
    for linking question topics
    """
    topic = StringField(required=True)
    prereqs = ListField(StringField())

    version = FloatField()

    def __unicode__(self):
        return str(self.topic) + ":" + str(self.prereqs)


class WikiQuestionAnswer(Document):
    """
    to record mturk answers
    """
    # TODO:: write(/read)/test
    question = ReferenceField(WikiQuestion, required=True)
    topic = StringField()
    time = DateTimeField()

    answer = IntField(
        required=True)  # corresponds to choices indices in the WikiQuestion
    correctness = BooleanField()  # fast way to retrieve correctness, maybe not needed

    # user info
    # Later: generate random workerId for normal visitors? This is not needed for the mturk test. You are not going to
    # have a lot of users off mturk anyway
    workerId = StringField(required=True)
    assignmentId = StringField(required=True, unique=True)
    hitId = StringField()
    turkSubmitTo = StringField()

    # extra information
    topic_confidence = IntField(min_value=-1, max_value=5)
    question_confidence = IntField(min_value=-1, max_value=5)
    comment = StringField()
    comment_guess = StringField()

    is_reasonable_question = BooleanField()
    grammatical_errors = ListField(IntField())
    semantic_errors = ListField(IntField())

    # time delta in milliseconds
    topic_confidence_time_delta = IntField()
    submit_time_delta = IntField()

    def __unicode__(self):
        return str(self.topic) + ":" + str(self.workerId)
