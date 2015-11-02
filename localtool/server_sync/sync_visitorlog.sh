#!/usr/bin/env bash

# uncomment ceartin lines to perform corresponding actions
# TODO:: every time before excuting this script:
# 1. change the date into the current date


# remote questions and question sets are synced just in case,
# they will not be written into the database by default
ssh root@crowdtutor.info "mongodump --db eduwiki_db --collection visitor_log --out /opt/backup/eduwiki-20150922"
scp -r root@crowdtutor.info:/opt/backup/eduwiki-20150922/ ./export_results/logsOnly/

mongorestore --db eduwiki_db --collection visitor_log ./export_results/logsOnly/eduwiki-20150922/eduwiki_db/visitor_log.bson