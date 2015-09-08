__author__ = 'moonkey'

import pymc as pm
import matplotlib.pyplot as plt
import numpy as np


def bayesian_irt(correctness_data):
    # num_questions = 15
    # num_people = 21
    # correctness_data = np.zeros(num_questions, num_people)

    num_questions = correctness_data.shape[0]
    num_people = correctness_data.shape[1]
    num_thetas = 1

    # theta (student proficiency params)
    theta_initial = np.zeros((num_thetas, num_people))
    theta = pm.Normal("theta", mu=0, tau=1, value=theta_initial, observed=False)

    # question-parameters (IRT params)
    # values of tau can be chosen to be large to reflect "ignorance"
    # (note that the mean for the discrimination parameters isn't 0,
    # since in general questions will be somewhat diagnostic)
    a = pm.Normal(
        "a", mu=1.0, tau=1e10, value=[[0.0] * num_thetas] * num_questions,
        observed=False)
    b = pm.Normal(
        "b", mu=0.0, tau=1e10, value=[0.0] * num_questions, observed=False)

    @pm.deterministic
    def sigmoid(theta=theta, a=a, b=b):
        """
        :param theta:
        :param a:
        :param b:
        :return: vector of prob of each person getting each question correct
        """
        bs = np.repeat(np.reshape(b, (len(b), 1)), num_people, 1)
        # print b.shape, a.shape, theta.shape
        return 1.0 / (1.0 + np.exp(bs - np.dot(a, theta)))

    # take the probabilities coming out of the sigmoid, and flip weighted coins
    correct = pm.Bernoulli(
        'correct', p=sigmoid, value=correctness_data, observed=True)

    # create a pymc simulation object, including all the above variables
    m = pm.MCMC([a, b, theta, sigmoid, correct])

    # run an interactive MCMC sampling session
    m.isample(iter=20000, burn=15000)

    return a, b, theta


def plot_theta_trace(theta, stepsize=20):
    """
    animated plot of theta values being sampled over time
    lines are thetas (dotted are original thetas used to generate),
    across the x axis is people.
    :param theta:
    :param stepsize:
    :return:
    """
    trace = theta.trace()
    theta_mean = trace.mean(0)[0]
    print 'theta_mean:', theta_mean

    theta_stderr = np.sqrt(trace.var(0)[0])
    print 'theta_stderr:', theta_stderr
    x_labels = range(0, len(theta_mean.T))

    for i in range(0, trace.shape[0], stepsize):
        # trace = theta.trace()
        sample = trace[i:i + stepsize, :, :].mean(0).T

        # in case we're running the simulation in another thread,
        # wait a bit for it to catch up
        if sample[-3:, :].mean() == 0:
            plt.pause(1)
            continue

        plt.clf()

        plt.plot(theta_mean.T, "--")
        plt.fill_between(x_labels,
                         (theta_mean - theta_stderr).T,
                         (theta_mean + theta_stderr).T,
                         facecolor=(0.8, 0.8, 0.8), linewidth=0.0)
        plt.plot(sample)
        plt.title(i)
        plt.ylim((-3, 3))
        plt.pause(0.01)

    plt.show()

def plot_sigmoid(a, b):
    # TODO:: refer to guacamole code
    pass