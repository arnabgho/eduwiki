__author__ = 'moonkey'

from botowrapper import *


def pay_hit(hit_id, sandbox=True):
    mtc = connect_mturk(sandbox=True)
    mtc.get_hit(hit_id=hit_id)
    mtc.get_assignments(hit_id=hit_id)