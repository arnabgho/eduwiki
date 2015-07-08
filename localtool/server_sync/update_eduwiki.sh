#!/bin/sh

cd /home/django/eduwiki
git pull
python manage.py collectstatic
service gunicorn restart