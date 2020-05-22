import collections
import covasim.defaults as cvd
import covasim.utils as cvu
import numpy as np
import clusters as cl


def clusters_to_contacts(clusters):
    """
    Convert clusters to contacts

    cluster of people [1,2,3] would result in contacts
        1: [2,3]
        2: [1,3]
        3: [1,2]

    """
    contacts = collections.defaultdict(set)
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
        contacts = collections.defaultdict(list)
        for s, t in zip(source, target):
            contacts[s].append(t)
        contacts = {p:contacts[p] if p in contacts else list() for p in include_inds}
        return contacts


def make_hcontacts(n_households, pop_size, household_heads, uids, contact_matrix):
    """

    :param n_households:
    :param pop_size:
    :param household_heads:
    :return:
    """
    h_clusters, h_ages = cl.make_household_clusters(n_households, pop_size, household_heads, uids, contact_matrix)
    h_contacts = clusters_to_contacts(h_clusters)
    return h_contacts, h_ages


def make_scontacts(uids, ages, s_contacts):
    """Create school contacts, with children of each age clustered in groups"""
    class_cl = cl.make_sclusters(uids, ages, s_contacts)
    class_co = clusters_to_contacts(class_cl)
    return class_co


def make_wcontacts(uids, ages, w_contacts):
    work_cl = cl.make_wclusters(uids, ages, w_contacts)
    work_co = clusters_to_contacts(work_cl)
    return work_co


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
        contacts = collections.defaultdict(list)
        for s, t in zip(source, target):
            contacts[s].append(t)
        contacts = {p: contacts[p] if p in contacts else list() for p in include_inds}
        return contacts


def make_custom_contacts(uids, n_contacts, pop_size, ages, custom_lkeys, cluster_types, pop_proportion, age_lb, age_ub):
    contacts = {}

    for layer_key in custom_lkeys:
        cl_type = cluster_types[layer_key]
        num_contacts = n_contacts[layer_key]
        custom_clusters, in_layer = cl.make_custom_clusters(uids, pop_size, ages, custom_lkeys, pop_proportion, age_lb, age_ub)
        # handle the cluster types differently
        if cl_type == 'complete':   # number of contacts not used for complete
            contacts[layer_key] = clusters_to_contacts([custom_clusters])
        elif cl_type == 'random':
            contacts[layer_key] = random_contacts(in_layer, num_contacts)
        elif cl_type == 'cluster':
            in_layer_inds = np.where(in_layer)
            clus = [cl.create_clustering(in_layer_inds, num_contacts)]
            contacts[layer_key] = clusters_to_contacts(clus)
        else:
            raise Exception(f'Error: Unknown network structure: {cl_type}')

    return contacts


