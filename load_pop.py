import pandas as pd
import numpy as np
from collections import defaultdict
import covasim.utils as cvu
import sciris as sc
import os
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

def random_contacts(weights, mean_contacts_per_person):
    # Weights should have the same number of entries as the total population size
    contacts = {}
    n_eligible = sum(weights > 0)
    for p in range(len(weights)):
        n_contacts = cvu.poisson(mean_contacts_per_person)  # Draw the number of Poisson contacts for this person
        contacts[p] = cvu.choose_w(weights, min(n_eligible, n_contacts))  # Choose people at random
    return contacts

def get_mixing_matrix(sheet_name: str):
    """
    Load Prem et al. matrices
    """
    mixing_matrix = pd.read_excel(dirname + '\\data\\demographic.xlsx', sheet_name=sheet_name, usecols=range(17), index_col=0)
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
            ages.append(bin_lower[bin] + np.random.randint(bin_upper[bin] - bin_lower[bin]))

    return np.array(ages)


def get_australian_popdict(setting='Melbourne', pop_size=100, contact_numbers={'H': 4,'S': 22,'W': 20,'C': 20}):
    """
    Make a population specification for CovaSim from Australian data and Prem matrices
    """

    reference = pd.read_excel(dirname + '\\data\\vic_reference.xlsx').set_index('Age')[setting]  # Age distribution of reference person
    household_dist = pd.read_excel(dirname + '\\data\\demographic.xlsx', sheet_name='households')['no. households']  # Household size distribution
    household_dist.index = household_dist.index + 1  # Convert from index to number of people in the household (starting at 1)

    # Calculate the number of households we need to fill to meet the population size requirement
    n_households = ((pop_size * household_dist.index * household_dist / sum(household_dist.index * household_dist)) / household_dist.index).astype(int)
    n_households[1] += pop_size - sum(n_households * n_households.index)  # Adjust single-person households to fill the gap

    # Select the ages of the heads of households
    household_heads = np.random.choice(reference.index, sum(n_households), p=reference.values / sum(reference.values))

    popdict = {}
    popdict['uid'] = np.arange(pop_size)  # Assign UIDs
    popdict['age'] = []
    contacts = {}  # store dict of contact dicts e.g. {'H':{1:[2,3],2:[1,3]...}}

    # Create households+people and store ages
    household_clusters = []
    mixing_matrix, bin_lower, bin_upper = get_mixing_matrix('contact matrices-home')
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

    # Create random school contacts (only certain ages eligible)
    classroom_size = contact_numbers['S']
    contacts['S'] = random_contacts((popdict['age'] >= 5) & (popdict['age'] <= 18), classroom_size)

    # Create random work contacts (only certain ages eligible)
    workplace_size = contact_numbers['W']
    contacts['W'] = random_contacts((popdict['age'] > 18) & (popdict['age'] <= 65), workplace_size)

    # Create random community contacts
    social_size = contact_numbers['C']
    contacts['C'] = random_contacts(popdict['age'], social_size)

    # Assign sexes
    sexes = pd.read_excel(dirname + '\\data\\vic_sexes.xlsx', header=[0, 1])[setting]
    sexes['frac_male'] = sexes['Male'] / (sexes['Male'] + sexes['Female'])  # Get fraction male
    sexes['frac_male'] = sexes['frac_male'].fillna(0.5)  # Fill NaNs with 0.5 (in cases where there were 0 people of either sex
    probability_male = sexes.loc[popdict['age'], 'frac_male']
    popdict['sex'] = np.random.binomial(1, probability_male) # nb. 1 means male

    # Convert contacts into the format expected by Covasim
    popdict['layer_keys'] = list(contacts.keys())
    popdict['contacts'] = []
    for i in range(0,pop_size):
        d = {layer: contacts[layer][i] if i in contacts[layer] else [] for layer in popdict['layer_keys']}
        popdict['contacts'].append(d)
    return popdict

