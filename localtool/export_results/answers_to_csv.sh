#!/bin/sh
mongoexport --db eduwiki_db --collection wiki_question_answer --csv --fieldFile answer_to_csv_fields.txt --out ./wiki_question_answer.csv