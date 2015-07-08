__author__ = 'moonkey'

from mongonaut.sites import MongoAdmin

# Import your custom models
from models import *


WikiQuestion.mongoadmin = MongoAdmin()
WikiQuestionAnswer.mongoadmin = MongoAdmin()
Prereq.mongoadmin = MongoAdmin()