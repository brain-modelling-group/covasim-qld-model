# tests the distribution produced by the make_random_contacts() function

from collections import Counter
import contacts as co
import matplotlib.pyplot as plt
import numpy as np
import sciris as sc


def make_contacts(size=100000, mean_number_contacts=3, dispersion=None, array_output=False):
    include = np.random.choice([0, 1], size=size)

    contacts = co.make_random_contacts(include, mean_number_contacts, dispersion, array_output)
    return contacts


def get_degree_from_dict(contacts):
    degree = [len(targets) for targets in contacts.values()]
    return degree


def get_degree_from_array(source):
    degree_dict = Counter(source)  # degree is the number of times each occurs
    degree = list(degree_dict.values())
    return degree


def plot_degree(contacts, array_output=True, bins=None, show=True, save=False, fig_path=None):
    if array_output:
        degree = get_degree_from_array(contacts)
    else:
        degree = get_degree_from_dict(contacts)

    plt.hist(degree, bins=bins)
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

### Examples of testing

# generate and plot the contacts dictionary
contacts = make_contacts()
bins = np.linspace(0, 20, 20)
plot_degree(contacts, bins=bins)

# generate and plot the source array (alternative output)
source, target = make_contacts(array_output=True)
bins = np.linspace(0, 20, 20)
plot_degree(source, bins=bins, array_output=True)

