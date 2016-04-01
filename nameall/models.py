from mongoengine import *


class NameInfo(Document):
    name = StringField(required=True)
    gender = StringField()
    country = StringField()
    time = DateTimeField()
    ip = StringField()