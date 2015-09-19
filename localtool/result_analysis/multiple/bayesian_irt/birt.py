__author__ = 'moonkey'

import pymc
import matplotlib.pyplot as plt
import numpy as np


def bayesian_irt(correctness_data, theta_true=None):
    # num_questions = 15
    # num_people = 21
    # correctness_data = np.zeros(num_questions, num_people)

    num_questions = correctness_data.shape[0]
    num_people = correctness_data.shape[1]
    num_thetas = 1

    # theta (student proficiency params)
    if theta_true is not None:
        theta = pymc.Normal(
            "theta", mu=0, tau=1, value=theta_true, observed=True)
    else:
        theta_initial = np.zeros((num_thetas, num_people))
        theta = pymc.Normal(
            "theta", mu=0, tau=1, value=theta_initial, observed=False)

    # question-parameters (IRT params)
    # values of tau can be chosen to be large to reflect "ignorance"
    # (note that the mean for the discrimination parameters isn't 0,
    # since in general questions will be somewhat diagnostic)

    a = pymc.Normal(
        "a", mu=1.0, tau=1, value=[[1.0] * num_thetas] * num_questions,
        observed=False)

    # Half Normal prior will cause
    # a = pymc.HalfNormal(
    # "a", tau=1, value=[[1.0] * num_thetas] * num_questions,
    # observed=False)

    b = pymc.Normal(
        "b", mu=0.0, tau=1, value=[0.0] * num_questions, observed=False)

    @pymc.deterministic
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
    correct = pymc.Bernoulli(
        'correct', p=sigmoid, value=correctness_data, observed=True)

    # create a pymc simulation object, including all the above variables
    m = pymc.MCMC([a, b, theta, sigmoid, correct])

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
    plt.style.use('ggplot')
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
        plt.title('Iteration ' + str(i))
        plt.ylim((-3, 3))
        plt.pause(0.01)

    plt.show()


def plot_sigmoid(item_params, filename='', fig_title=''):
    abilities_to_plot = np.arange(-3, 3, .01)
    items = item_params.keys()
    item_plots = {}

    def eval_conditional_probability(theta, a, b):
        return 1.0 / (1.0 + np.exp(b - np.dot(a, theta)))

    for item in items:
        item_plots[item] = []
        for ability in abilities_to_plot:
            conditional_probs = eval_conditional_probability(
                ability, item_params[item]['a'], item_params[item]['b'])
            item_plots[item].append(conditional_probs)

    # to make colors/style different for each curve
    # all_matplotlib_colors = []
    # for c_name, c_hex in matplotlib.colors.cnames.iteritems():
    # all_matplotlib_colors.append(c_name)
    # cmap = plt.get_cmap('jet')
    # colors = cmap(np.linspace(0, 1, len(items)))

    line_styles = ['-', '--', '-.', ':', ]
    # plt.style.use('ggplot')
    for idx, item in enumerate(items):
        plt.plot(abilities_to_plot, item_plots[item],
                 # color=all_matplotlib_colors[idx],
                 # color=colors[idx],
                 linestyle=line_styles[idx % len(line_styles)],
                 label=item)
    plt.xlabel('Student Ability')
    plt.ylabel('P(Answer Correctly)')
    plt.ylim((0, 1))
    plt.xlim((-3, 3))
    if not fig_title:
        plt.title('Two parameter IRT model')
    else:
        plt.title(fig_title)
    plt.legend(loc='best', prop={'size': 6})
    if not filename:
        plt.show()
    else:
        filename += '_sigmoid.pdf'
        plt.savefig(filename, bbox_inches='tight')
    plt.close()