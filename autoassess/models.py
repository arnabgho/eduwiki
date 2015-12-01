import random
from mongoengine import *
import datetime
# Create your models here.


class WikiQuestion(Document):
    """
    save generated questions,
    """
    WikiQuestionType = (
        "WHAT_IS",
        "KEY_ITEM",

        "MANUAL",
        # No other type so far. no need to
    )
    type = StringField(choices=WikiQuestionType)

    topic = StringField(required=True)

    # for multiple questions inside one article
    quiz_topic = StringField()

    question_text = StringField(required=True)  # question_stem

    # We can make the options a EmbeddedDocument if needed as we may want to
    # know and store how the options are generated.
    choices = ListField(StringField(), required=True)
    # by deafult, the first option is the right answer
    correct_answer = IntField(required=True)

    # for question generation
    version = FloatField(required=True)

    # Added to cope with the case where the question has multiple right choices
    # i.e. multiple-choices rather than single-choice
    is_multiple_choice = BooleanField()  # by default is false (single-choice)
    multiple_correct_answers = ListField(IntField(required=True))

    def __str__(self):
        return unicode(self.topic) + ":" + unicode(self.question_text)

    def __unicode__(self):
        return unicode(self.__str__())


class Prereq(Document):
    """
    for linking question topics
    """
    topic = StringField(required=True)
    prereqs = ListField(StringField())

    version = FloatField()

    def __str__(self):
        return str(self.topic) + ":" + str(self.prereqs)

    def __unicode__(self):
        return unicode(self.__str__())


class WikiQuestionAnswer(Document):
    """
    to record mturk answers
    """
    # TODO:: write(/read)/test
    question = ReferenceField(WikiQuestion, required=True)
    topic = StringField()
    time = DateTimeField()

    answer = IntField(required=True)
    # corresponds to choices indices in the WikiQuestion
    correctness = BooleanField()
    # fast way to retrieve correctness, maybe not needed

    # user info
    # TODO:: to track the answers of the normal visitors?
    # Later: generate random workerId for normal visitors?
    # This is not needed for the mturk test. You are not going to
    # have a lot of users off mturk anyway
    workerId = StringField(required=True)
    assignmentId = StringField(required=True)
    # assignmentId: unique=True. does not hold for quizzes situation
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

    # track the choice orders in case they are randomly shuffled
    choice_order = ListField(IntField())

    def __str__(self):
        return str(self.topic) + ":" + str(self.workerId)

    def __unicode__(self):
        return unicode(self.__str__())


class QuestionSet(Document):
    set_topic = StringField(required=True)

    # for automatically generated question  sets
    related_topics = ListField(StringField())

    # for questions that are composed into one quiz
    questions = ListField(ReferenceField(WikiQuestion))

    version = FloatField()

    def __str__(self):
        return str(self.set_topic) + " version=" + str(self.version) + \
               ":" + str(self.related_topics)

    def __unicode__(self):
        return unicode(self.__str__())

    @property
    def note(self):
        quiz_note = ''
        if self.version == -1.0:
            quiz_note = 'Expert-Questimator Mixture'
        elif self.version == -1.1:
            quiz_note = 'Expert1 - Expert2 Mixture'
        elif self.version > 0:
            quiz_note = 'Questimator generated'
        return quiz_note


class QuizAnswers(Document):
    """
    Record a list of answers for a quiz (question set)
    """
    quiz = ReferenceField(QuestionSet, required=True)
    # in case the question order differs from person to person,
    # it will be recorded here
    question_order = ListField(ReferenceField(WikiQuestion))

    # user identification
    workerId = StringField(required=True)
    assignmentId = StringField(required=True, unique_with=['workerId'])

    # note this may contain multiple answers for each question
    # if the question answer has been modified
    quiz_answer_procedure = ListField(ReferenceField(WikiQuestionAnswer))
    quiz_final_answers = ListField(ReferenceField(WikiQuestionAnswer))

    quiz_submit_time = DateTimeField()
    # time delta in milliseconds
    quiz_time_delta = IntField()

    comment = StringField()  # For additional information

    def __str__(self):
        return str(self.quiz) + str(self.workerId)

    def __unicode__(self):
        return unicode(self.__str__())


class QuestionRequest(Document):
    search_term = StringField(required=True)
    request_time = StringField(required=True)
    request_email = EmailField()


class QuizRequest(Document):
    nickname = StringField(default='Anonymous')
    email = EmailField()
    request_topic = StringField(max_length=100)
    time = DateTimeField(default=datetime.datetime.now())
    status = StringField()


class QuestionLabel(Document):
    question_id = ObjectIdField(required=True)
    quiz_id = ObjectIdField(required=True)

    answer_qualities = ListField(BooleanField(required=True))

    typo = BooleanField(required=True)
    multi_answer = BooleanField(required=True)
    ambiguous_correct_answer = BooleanField(required=True)
    irrelevant_topic = BooleanField(required=True)
    too_easy = BooleanField(required=True)

    pedagogical_utility = IntField(required=True)
    comment = StringField()

    workerId = StringField(required=True)

    time = DateTimeField(default=datetime.datetime.now())