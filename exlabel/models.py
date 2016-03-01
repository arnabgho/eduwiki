from mongoengine import *


class ExploreTrajectory(Document):
    image_name = StringField(required=True)
    # image_label = IntField(required=True)
    worker_label = IntField(required=True)

    # grid_size = IntField()  # M*N patches
    trajectory = StringField()  # ListField(ListField(IntField))
    actions = StringField()
    # use ast.literal_eval() to get back the lists when processing

    time = DateTimeField()
    workerId = StringField()
    assignmentId = StringField()
    hitId = StringField()
    turkSubmitTo = StringField()

    comment = StringField()