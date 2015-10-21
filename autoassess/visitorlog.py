__author__ = 'moonkey'

from ipware.ip import get_real_ip, get_ip
from mongoengine import *


class VisitorLog(Document):
    ip = StringField(required=True)
    ip_real = BooleanField(required=True)
    path = StringField(required=True)
    time = DateTimeField(required=True, default=datetime.datetime.now())


def log_visitor_ip(request):
    try:
        ip = get_real_ip(request)
        ip_real = True
        if not ip:
            ip = get_ip(request)
            ip_real = False

        if not ip or ip == '127.0.0.1':
            return

        path = request.path
        vl = VisitorLog(
            ip=ip, ip_real=ip_real, path=path, time=datetime.datetime.now())
        vl.save()
        return True
    except Exception:
        # It does not matter if this code fails
        return False