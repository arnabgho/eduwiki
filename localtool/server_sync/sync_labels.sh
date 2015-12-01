#!/usr/bin/env bash

# uncomment ceartin lines to perform corresponding actions
# TODO:: every time before excuting this script:
# 1. change the date into the current date


# remote questions and question sets are synced just in case,
# they will not be written into the database by default
ssh -i ~/.ssh/eduwiki.pem ubuntu@crowdtutor.info "mongodump --db eduwiki_db --collection question_label --out /home/ubuntu/backup/eduwiki-20151130"
scp -r -i ~/.ssh/eduwiki.pem ubuntu@crowdtutor.info:~/backup/eduwiki-20151130/ ./export_results/labels/

mongorestore  --host=127.0.0.1 --db eduwiki_db --collection question_label ./export_results/labels/eduwiki-20151130/eduwiki_db/question_label.bson