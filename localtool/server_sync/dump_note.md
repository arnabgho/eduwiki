# DB Note

## Sync Protocol
### localhost to server
* question_set
* wiki_question

### server to localhost
* wiki_question answer
* quiz_answers
* question_set [Optional, not restored into local db]
* wiki_question [Optional, not restored into local db]

####!!!So please make sure the question with a specific ID is not changed


## Sync Record
### eduwiki-20150707
Content: single question answers for 50(?) questions
Answer per q: 5(?)
Version: 0.2X (?)

### eduwiki-20150823
Content: ANN quiz answers
Workers: 5(?)
Version: 0.23/-1.0

### eduwiki-20150824
+above
Content: with additional 4 workers for ANN quiz
mysteriously got 10 workers

### eduwiki_20150831
+above
Content: Customer centricity quiz anwers
Workers: 10

### eduwiki_20150901
+above
Content: Customer centricity quiz anwers
Workers: 21