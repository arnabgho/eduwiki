#!/bin/sh
mongoexport --db eduwiki_db --collection wiki_question_answer --csv --fieldFile fields.txt --out ./wiki_question_answer.csv