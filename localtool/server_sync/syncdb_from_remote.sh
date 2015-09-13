#!/bin/sh

# uncomment ceartin lines to perform corresponding actions
# TODO:: every time before excuting this script:
# 1. change the date into the current date


# remote questions and question sets are synced just in case,
# they will not be written into the database by default
ssh root@crowdtutor.info "mongodump --db eduwiki_db --collection wiki_question --out /opt/backup/eduwiki-20150912"
ssh root@crowdtutor.info "mongodump --db eduwiki_db --collection question_set --out /opt/backup/eduwiki-20150912"

ssh root@crowdtutor.info "mongodump --db eduwiki_db --collection wiki_question_answer --out /opt/backup/eduwiki-20150912"
ssh root@crowdtutor.info "mongodump --db eduwiki_db --collection quiz_answers --out /opt/backup/eduwiki-20150912"
scp -r root@crowdtutor.info:/opt/backup/eduwiki-20150912/ ./export_results/

#mongo eduwiki_db --eval "db.wiki_question.drop()"
#mongo eduwiki_db --eval "db.wiki_question_answer.drop()"
#mongorestore --db eduwiki_db --collection wiki_question ./export_results/eduwiki-20150912/eduwiki_db/wiki_question.bson
mongorestore --db eduwiki_db --collection wiki_question_answer ./export_results/eduwiki-20150912/eduwiki_db/wiki_question_answer.bson
mongorestore --db eduwiki_db --collection quiz_answers ./export_results/eduwiki-20150912/eduwiki_db/quiz_answers.bson
#mongoexport --db eduwiki_db --collection wiki_question_answer --csv --fieldFile ./export_results/answer_to_csv_fields.txt --out ./export_results/wiki_question_answer.csv