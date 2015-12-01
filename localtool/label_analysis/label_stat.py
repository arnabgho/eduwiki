from __future__ import division
from autoassess.models import QuestionLabel, QuestionSet, WikiQuestion
import collections


def read_all_labels():
    labels = [l for l in QuestionLabel.objects()]

    # find quizzes been labeled
    label_quiz_ids = [l.quiz_id for l in labels]
    label_quiz_ids = list(set(label_quiz_ids))
    print 'labeled quiz num:', len(label_quiz_ids)

    # eliminate duplicated labels (labeler may updated label)
    # label_question_ids = [l.question_id for l in labels]
    # duplicate_questions = [
    #     item for item, count in collections.Counter(label_quiz_ids).items()
    #     if count > 1]

    labels = sorted(labels, key=lambda k: k['time'], reverse=True)
    labels = list_of_seq_unique_by_key(labels, 'question_id')
    return labels


def stats(labels):
    num_labels = len(labels)
    print 'labeled question num:', num_labels
    quality_labels = [l.pedagogical_utility for l in labels]
    print 'quality_labels', quality_labels
    quality_count = {item: count for item, count in
                     collections.Counter(quality_labels).items()}
    quality_stats = {i: quality_count[i] / num_labels for i in quality_count}
    print 'question quality:', quality_stats

    bad_question_labels = [l for l in labels if l.pedagogical_utility == 0]
    bad_count_dict = error_type_stat(bad_question_labels)
    bad_stats = {i: bad_count_dict[i] / quality_count[0] for i in
                 bad_count_dict}
    print 'Not useful:', bad_stats

    # good_question_labels = [l for l in labels if l.pedagogical_utility]
    # good_count_dict = error_type_stat(good_question_labels)
    # print 'Good:', good_count_dict

    for l in labels:
        if not l.pedagogical_utility and not l.ambiguous_correct_answer and not l.irrelevant_topic and not l.multi_answer and not l.typo:
            if l.comment:
                print l.comment, l.id, l.question_id
            else:
                print "No comment", l.id, l.question_id
                # print l.comment


def error_type_stat(labels):
    typo_count = len([True for l in labels if l.typo])
    multi_ans_count = len([True for l in labels if l.multi_answer])
    ambiguous_count = len([True for l in labels if l.ambiguous_correct_answer])
    irrelevant_count = len([True for l in labels if l.irrelevant_topic])
    error_stat_dict = {
        'typo': typo_count,
        'multi_answer': multi_ans_count,
        'ambiguous_correct_answer': ambiguous_count,
        'irrelevant_topic': irrelevant_count,
    }

    return error_stat_dict


def list_of_seq_unique_by_key(seq, key):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x[key] not in seen and not seen_add(x[key])]


if __name__ == "__main__":
    from mongoengine import connect

    connect('eduwiki_db', host='localhost')
    all_labels = read_all_labels()
    stats(all_labels)