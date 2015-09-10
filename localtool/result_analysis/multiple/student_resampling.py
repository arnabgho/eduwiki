from __future__ import division

__author__ = 'moonkey'

import sklearn.utils
from autoassess.models import *
import csv
import numpy as np


def bootstrap_resample(samples, n=None):
    """ Bootstrap resample an array_like
    Parameters
    ----------
    X : array_like
      data to resample
    n : int, optional
      length of resampled array, equal to len(X) if n==None
    Results
    -------
    returns X_resamples
    """
    if type(samples) is not np.ndarray:
        samples = np.array(samples)
    if n is None:
        n = len(samples)

    resample_i = np.floor(np.random.rand(n) * len(samples)).astype(int)
    x_resample = samples[resample_i]
    return x_resample.tolist()


def resample_students(student_ans, n_samples=100):
    # student_ans = {
    # "workerId": [...]
    # }
    student_list = [s for s in student_ans]

    # print "student_list", student_list

    # sampled_students = sklearn.utils.resample(
    # student_list, replace=True, n_samples=n_samples)
    sampled_students = bootstrap_resample(student_list, n=n_samples)
    new_student_dict = {}
    for idx, stu in enumerate(sampled_students):
        sampled_stu_new_name = str(idx) + "_" + stu
        new_student_dict[sampled_stu_new_name] = student_ans[stu]

    return new_student_dict
