#!/bin/sh
ssh root@crowdtutor.info "mongodump --db eduwiki_db --collection wiki_question --out /opt/backup/eduwiki-20150710"
ssh root@crowdtutor.info "mongodump --db eduwiki_db --collection wiki_question_answer --out /opt/backup/eduwiki-20150710"
scp -r root@crowdtutor.info:/opt/backup/eduwiki-20150710/ ./export_results/

#mongo eduwiki_db --eval "db.wiki_question.drop()"
#mongo eduwiki_db --eval "db.wiki_question_answer.drop()"
#mongorestore --db eduwiki_db --collection wiki_question ./export_results/eduwiki-20150710/eduwiki_db/wiki_question.bson
#mongorestore --db eduwiki_db --collection wiki_question_answer ./export_results/eduwiki-20150710/eduwiki_db/wiki_question_answer.bson
#mongoexport --db eduwiki_db --collection wiki_question_answer --csv --fieldFile ./export_results/answer_to_csv_fields.txt --out ./export_results/wiki_question_answer.csv