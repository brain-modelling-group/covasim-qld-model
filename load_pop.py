import os
from collections import defaultdict

import covasim.utils as cvu
import covasim.defaults as cvd
import numpy as np
import pandas as pd

dirname = os.path.dirname(os.path.abspath(__file__))
#dirname = 'C:\\Users\\nick.scott\\Desktop\\Github\\covasim-australia'
def clusters_to_contacts(clusters):
    """
    Convert clusters to contacts

    cluster of people [1,2,3] would result in contacts
        1: [2,3]
        2: [1,3]
        3: [1,2]

    """
    contacts = defaultdict(set)
    for cluster in clusters:
        for i in cluster:
            for j in cluster:
                if j <= i:
                    pass
                else:
                    contacts[i].add(j)
                    contacts[j].add(i)

    return {x: np.array(list(y)) for x, y in contacts.items()}

def random_contacts(include, mean_contacts_per_person, array_output:bool=False):
    """
    Sample random contacts

    Note that random contacts are directed and asymmetric (e.g. Person 1 can transmit to Person 2 but not vice-versa).

    The `include` argument allows a subset of the population to be selected

    Note that a person can contact themselves, and can contact the same person multiple times

    Args:
        include: Boolean array with length equal to population size, containing True if the person is eligible for contacts
        mean_contacts_per_person: Mean number of contacts (Poisson distribution)
        array_output: Return contacts as arrays or as dicts
    Returns:
        If array_output=False, return a contacts dictionary {1:[2,3,4],2:[1,5,6]} with keys for source person,
        and a values being a list of target contacts.

        If array_output=True, return arrays with `source` and `target` indexes. These could be interleaved to produce an edge list
        representation of the edges

    """

    include_inds = np.nonzero(include)[0].astype(cvd.default_int) # These are the indexes (person IDs) of people in the layer
    n_people = len(include_inds)
    n_contacts = n_people*mean_contacts_per_person
    source = include_inds[np.array(cvu.choose_r(max_n=n_people, n=n_contacts))]  # Choose with replacement
    target = include_inds[np.array(cvu.choose_r(max_n=n_people, n=n_contacts))]

    if array_output:
        return source, target
    else:
        contacts = defaultdict(list)
        for s,t in zip(source, target):
            contacts[s].append(t)
        contacts = {p:contacts[p] if p in contacts else list() for p in include_inds}
        return contacts

def create_clustering(people_to_cluster, mean_cluster_size):
    """
    Return random clustering of people

    Args:
        people_to_cluster: Indexes of people to cluster e.g. [1,5,10,12,13]
        mean_cluster_size: Mean cluster size (poisson distribution)

    Returns: List of lists of clusters e.g. [[1,5],[10,12,13]]
    """

    # people_to_cluster = np.random.permutation(people_to_cluster) # Optionally shuffle people to cluster - in theory not necessary?
    clusters = []
    n_people = len(people_to_cluster)
    n_remaining = n_people

    while n_remaining > 0:
        this_cluster =  cvu.poisson(mean_cluster_size)  # Sample the cluster size
        if this_cluster > n_remaining:
            this_cluster = n_remaining
        clusters.append(people_to_cluster[(n_people-n_remaining)+np.arange(this_cluster)].tolist())
        n_remaining -= this_cluster

    return clusters

def get_mixing_matrix(databook_path, sheet_name: str):
    """
    Load Prem et al. matrices
    """
    mixing_matrix0 = pd.read_excel(dirname + '/' + databook_path, sheet_name=sheet_name, usecols=range(17), index_col=0)
    #symmetrize
    mixing_matrix = mixing_matrix0.copy()
    for i in range(len(mixing_matrix0)):
        for j in range(len(mixing_matrix0)):
            mixing_matrix.values[i,j] = (mixing_matrix0.values[i,j] + mixing_matrix0.values[j,i]) / 2.0
    bin_lower = [int(x.split('-')[0]) for x in mixing_matrix.index]
    bin_upper = [int(x.split('-')[1]) for x in mixing_matrix.index]
    return mixing_matrix, bin_lower, bin_upper

def sample_household_cluster(mixing_matrix, bin_lower, bin_upper, reference_age, n):
    """
    Return list of ages in a household/location based on mixing matrix and reference person age
    """

    ages = [reference_age]  # The reference person is in the household/location

    if n > 1:
        idx = np.digitize(reference_age, bin_lower) - 1  # First, find the index of the bin that the reference person belongs to
        p = mixing_matrix.iloc[idx, :]
        sampled_bins = np.random.choice(len(bin_lower), n - 1, replace=True, p=p / sum(p))

        for bin in sampled_bins:
            ages.append(int(round(np.random.uniform(bin_lower[bin]-0.5, bin_upper[bin]+0.5))))

    return np.array(ages)


def get_australian_popdict(databook_path, pop_size=100, contact_numbers={'H': 4,'S': 22,'W': 20,'C': 20}, population_subsets=None, setting=None):
    """
    Make a population specification for CovaSim from Australian data and Prem matrices
    """

    reference = pd.read_excel(dirname + '/' + databook_path, sheet_name='age_sex')['Total']
    reference.iloc[0:18] = 0
    reference.iloc[18:28] = reference.iloc[18:28] * np.linspace(0.1, 1, 10)

    household_dist = pd.read_excel(dirname + '/' + databook_path, sheet_name='households')['no. households']  # Household size distribution
    # calculate the population size generated by the household data, so that the household distribution can be scaled based no model population
    household_dist.index = household_dist.index + 1  # Convert from index to number of people in the household (starting at 1)
    # Calculate the number of households we need to fill to meet the population size requirement
    n_households = (pop_size * (household_dist / sum(household_dist.index * household_dist))).round().astype(int)
    n_households[1] += pop_size - sum(n_households * n_households.index)  # Adjust single-person households to fill the gap

    # Select the ages of the heads of households
    household_heads = np.random.choice(reference.index, sum(n_households), p=reference.values / sum(reference.values))
    #plt.hist(household_heads, bins=max(household_heads) - min(household_heads))
    popdict = {}
    popdict['uid'] = np.arange(pop_size)  # Assign UIDs
    popdict['age'] = []
    contacts = {}  # store dict of contact dicts e.g. {'H':{1:[2,3],2:[1,3]...}}

    # Create households+people and store ages
    household_clusters = []
    mixing_matrix, bin_lower, bin_upper = get_mixing_matrix(databook_path, 'contact matrices-home')
    households_completed = 0
    people_added = 0
    for household_size in n_households.index:
        for i in range(n_households.loc[household_size]):
            household_ages = sample_household_cluster(mixing_matrix, bin_lower, bin_upper, household_heads[households_completed], household_size)
            household_indexes = np.arange(people_added, people_added + household_size)  # Get the person IDs for these new people (just increments automatically)
            household_clusters.append(household_indexes.tolist())  # Put the people into the households
            popdict['age'] += household_ages.tolist()  # Add their ages to the age list

            households_completed += 1
            people_added += household_size

    popdict['age'] = np.array(popdict['age'])
    contacts['H'] = clusters_to_contacts(household_clusters)

    # Create school contacts, with children of each age clustered in groups
    classrooms = []
    for a in range(5,18):
        children_to_allocate = popdict['uid'][popdict['age'] == a]
        classrooms.extend(create_clustering(children_to_allocate, contact_numbers['S']))
    for i in range(len(classrooms)): # add a random adult to each classroom as the teacher
        classrooms[i].extend([np.random.choice(popdict['uid'][popdict['age'] > 18])])

    contacts['S'] = clusters_to_contacts(classrooms)

    # Create random work contacts (only certain ages eligible)
    workplaces = []
    workplaces.extend(create_clustering(popdict['uid'][(popdict['age'] > 18) & (popdict['age'] <= 65)], contact_numbers['W']))
    contacts['W'] = clusters_to_contacts(workplaces)

    # Create random community contacts
    social_size = contact_numbers['C']
    contacts['C'] = random_contacts(popdict['age'], social_size)

    extra_layers = {k: v for k, v in contact_numbers.items() if k not in {'H','W','S','C'}}
    for i, key in enumerate(extra_layers.keys()):
        n_layer = int(population_subsets['proportion'][key] * pop_size)
        inds = np.random.choice(popdict['uid'][(popdict['age'] > population_subsets['age_lb'][key]) & (popdict['age'] < population_subsets['age_ub'][key])], n_layer)
        x = np.zeros_like(popdict['age'])
        x[inds] = 1

        if population_subsets['cluster_type'][key] == 'complete':
            contacts[key] = clusters_to_contacts([inds])

        if population_subsets['cluster_type'][key] == 'random':
            n_contacts_per_layer = contact_numbers[key]
            contacts[key] = random_contacts(x, n_contacts_per_layer)

        if population_subsets['cluster_type'][key] == 'clusters':
            miniclusters = []
            miniclusters.extend(create_clustering(popdict['uid'][(popdict['age'] > population_subsets['age_lb'][key]) & (popdict['age'] < population_subsets['age_ub'][key])], contact_numbers[key]))
            contacts[key] = clusters_to_contacts(miniclusters)

        if population_subsets['cluster_type'][key] == 'partition':
            x = np.zeros_like(popdict['age'])
            x[inds] = 1
            y = np.ones_like(popdict['age'])
            y[inds] = 0
            n_contacts_per_layer = contact_numbers[key]
            contacts[key] = random_contacts(x, n_contacts_per_layer)
            part2 = random_contacts(y, n_contacts_per_layer)
            for j in range(pop_size):
                if  contacts[key][j] == []:
                    contacts[key][j] = part2[j]

    # Assign sexes
    sexes = pd.read_excel(dirname + '/' + databook_path, sheet_name = 'age_sex')
    sexes['frac_male'] = sexes['Male'] / (sexes['Male'] + sexes['Female'])  # Get fraction male
    sexes['frac_male'] = sexes['frac_male'].fillna(0.5)  # Fill NaNs with 0.5 (in cases where there were 0 people of either sex
    probability_male = sexes.loc[popdict['age'], 'frac_male']
    popdict['sex'] = np.random.binomial(1, probability_male) # nb. 1 means male

    # Convert contacts into the format expected by Covasim
    popdict['contacts'] = []
    for i in range(0,pop_size):
        d = {layer: contacts[layer][i] if i in contacts[layer] else [] for layer in contacts}
        popdict['contacts'].append(d)

    return popdict


# if __name__ == '__main__':
#     # This block allows quickly running this file directly to test the functions and set breakpoints
#     import sciris as sc
#     with sc.Timer() as t:
#         popdict = get_australian_popdict()


