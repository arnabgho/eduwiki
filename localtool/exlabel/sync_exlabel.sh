#!/bin/sh

# uncomment ceartin lines to perform corresponding actions
# TODO:: every time before excuting this script:
# 1. change the date into the current date


# remote questions and question sets are synced just in case,
# they will not be written into the database by default
ssh ubuntu@crowdtutor.info "mongodump --db eduwiki_db --collection explore_trajectory --out /home/ubuntu/backup/exlabel-20160301"
scp -r ubuntu@crowdtutor.info:/home/ubuntu/backup/exlabel-20160301/ ./export_results/

#mongo eduwiki_db --eval "db.wiki_question_answer.drop()"
mongorestore --db eduwiki_db --collection explore_trajectory ./export_results/exlabel-20160301/eduwiki_db/explore_trajectory.bson