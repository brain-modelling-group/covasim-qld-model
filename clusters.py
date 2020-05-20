import covasim.utils as cvu
import numpy as np


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
        this_cluster = cvu.poisson(mean_cluster_size)  # Sample the cluster size
        if this_cluster > n_remaining:
            this_cluster = n_remaining
        clusters.append(people_to_cluster[(n_people-n_remaining)+np.arange(this_cluster)].tolist())
        n_remaining -= this_cluster

    return clusters


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

