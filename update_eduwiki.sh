#!/usr/bin/env bash

cd /home/django/eduwiki
git pull
python manage.py collectstatic
service gunicorn restartgit p