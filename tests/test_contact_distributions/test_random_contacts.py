# tests the distribution produced by the random_contacts() function

import matplotlib.pyplot as plt
import numpy as np
import sciris as sc

from contacts import random_contacts


def make_distribution(size=100000):

    include = np.random.choice([0, 1], size=size, replace=True)
    mean_number_contacts = 10

    contacts = random_contacts(include, mean_number_contacts)

    return contacts


def get_number_of_contacts(contacts):
    number_of_contacts = np.zeros(len(contacts.keys()))

    for source, targets in contacts.items():
        number_of_contacts[source] = len(targets)

    return number_of_contacts


def get_degree(contacts):
    degree = [len(targets) for targets in contacts.values()]
    return degree


def plot_degree_distribution(contacts, show=True, save=False, fig_path=None):
    degree = get_degree(contacts)

    plt.hist(degree)
    plt.title("Degree distribution")
    plt.xlabel("Degree")
    plt.ylabel("Count")
    if save:
        if fig_path is None:
            fig_path = 'degree_distribution.png'
        fig_path = sc.makefilepath(fig_path)
        plt.savefig(fig_path)
    if show:
        plt.show()
    return


contacts = make_distribution()

plot_degree_distribution(contacts)

