#!/usr/bin/env bash

cd /home/ubuntu/eduwiki
git pull
python manage.py collectstatic
service gunicorn restart