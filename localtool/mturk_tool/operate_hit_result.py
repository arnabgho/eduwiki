__author__ = 'moonkey'

from botowrapper import *
import os


def approve_hit(hit_id, sandbox=True):
    mtc = connect_mturk(sandbox=sandbox)

    # Submitted, Approved, or Rejected
    submitted_assignments = mtc.get_assignments(
        hit_id=hit_id, status="Submitted")
    approved_assignments = mtc.get_assignments(
        hit_id=hit_id, status="Approved")
    print hit_id, len(submitted_assignments), len(approved_assignments)
    for assignment in submitted_assignments:
        mtc.approve_assignment(assignment.AssignmentId)


def expire_hit(hit_id, sandbox=True):
    mtc = connect_mturk(sandbox=sandbox)
    print "Expiring:", hit_id
    return mtc.expire_hit(hit_id)


def operate_experiment(filename, hit_op, sandbox=True):
    results = []
    with open(filename, 'rU') as topic_hits_file:
        for topic_hit in topic_hits_file:
            pair = topic_hit.split(':')
            topic = pair[0]
            hit_id = pair[1].lstrip(" ").rstrip("\n")
            operation_result = hit_op(hit_id, sandbox=sandbox)
            results.append(operation_result)
            print topic
    return results


def operate_all_experiments(topic_filename, hit_op, sandbox=True):
    sandbox_prefix = 'sandbox_' if sandbox else ""
    output_files = []
    if os.path.exists(sandbox_prefix + topic_filename + ".out.txt"):
        output_file = sandbox_prefix + topic_filename + ".out.txt"
        output_files.append(output_file)

    for idx in range(0, 100):
        filename = sandbox_prefix + topic_filename \
                        + "_" + str(idx) + ".out.txt"
        if os.path.exists(filename):
            output_file = filename
            output_files.append(output_file)
        else:
            break
    for filename in output_files:
        operate_experiment(filename, hit_op=hit_op, sandbox=sandbox)


if __name__ == "__main__":
    # operate_all_experiments(
    #     topic_filename="experiment_data/90_topics.txt",
    #     hit_op=approve_hit,
    #     sandbox=True)
    # for idx in range(0, 8):
    #     approve_hit(hit_id="3M0556243RJGIA3OPZJWY1DEWIKNFY", sandbox=False)
    # for idx in range(0, 8):
    #     approve_hit(hit_id="3GVPRXWRPGTBPGDRA08S514GBRII7B", sandbox=False)
    for idx in range(0, 8):
        approve_hit(hit_id="3NKW03WTLL63WT2BVGLD6JUJWY5QWY", sandbox=False)