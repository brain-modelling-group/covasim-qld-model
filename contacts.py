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
        if cl_type == 'complete':   # number of contacts not used for complete clusters
            contacts[layer_key] = clusters_to_contacts([custom_clusters])
        elif cl_type == 'random':
            contacts[layer_key] = random_contacts(in_layer, num_contacts)
        elif cl_type == 'cluster':
            in_layer_inds = np.where(in_layer)[0] #todo: currently return tuple (error), also could be more efficient doing this earlier
            clus = cl.create_clustering(in_layer_inds, num_contacts)
            contacts[layer_key] = clusters_to_contacts(clus)
        else:
            raise Exception(f'Error: Unknown network structure: {cl_type}')

    return contacts


def convert_contacts(contacts, uids, all_lkeys):
    """ Convert contacts structure to be compatible with Covasim

    :return a list of length pop_size, where each entry is a dictionary by layer,
            and each dictionary entry is the UIDs of the agent's contacts"""
    contacts_list = [None] * len(uids)
    for uid in uids:
        contacts_list[uid] = {}
        for layer_key in all_lkeys:
            layer_contacts = contacts[layer_key]
            if layer_contacts.get(uid) is not None:
                contacts_list[uid][layer_key] = layer_contacts[uid]
            else:
                contacts_list[uid][layer_key] = np.empty(0)
    return contacts_list


def get_uids(pop_size):
    people_id = np.arange(start=0, stop=pop_size, step=1)
    return people_id


def get_numhouseholds(household_dist, pop_size):
    """Calculates the number of households we need to create to meet the population size"""
    n_people = sum(household_dist.index * household_dist)  # n_people = household_size * n_households
    household_percent = household_dist / n_people
    n_households = (pop_size * household_percent).round().astype(int)
    n_households[1] += pop_size - sum(n_households * n_households.index)  # adjust single-person households to fill the gap
    return n_households


def get_household_heads(age_dist, n_households):
    """Selects the ages of the household heads by randomly selecting from the available ages"""
    # prevent anyone under the age of 18 being chosen
    age_dist.iloc[0:18] = 0
    # decrease probability of someone aged 18-28 being chosen
    age_dist.iloc[18:28] *= np.linspace(0.1, 1, 10)

    # randomly choose household head, given the number of people in each age
    age_prob = age_dist.values / sum(age_dist.values)
    household_heads = np.random.choice(age_dist.index, size=sum(n_households), p=age_prob)
    return household_heads


def make_contacts(params):
    contacts = {}

    pop_size = params.pars['pop_size']
    household_dist = params.household_dist
    age_dist = params.age_dist
    contact_matrix = params.contact_matrix
    n_contacts = params.pars['contacts']
    all_lkeys = params.all_lkeys

    # for custom layers
    custom_lkeys = params.custom_lkeys
    cluster_types = params.layerchars['cluster_type']
    pop_proportion = params.layerchars['proportion']
    age_lb = params.layerchars['age_lb'] # todo: potentially confusing with the age_up in the contact matrix
    age_ub = params.layerchars['age_ub']

    uids = get_uids(pop_size)

    # household contacts
    n_households = get_numhouseholds(household_dist, pop_size)
    household_heads = get_household_heads(age_dist, n_households)
    h_contacts, ages = make_hcontacts(n_households,
                                      pop_size,
                                      household_heads,
                                      uids,
                                      contact_matrix)
    contacts['H'] = h_contacts

    # school contacts
    key = 'S'
    social_no = n_contacts[key]
    s_contacts = make_scontacts(uids, ages, social_no)
    contacts[key] = s_contacts

    # workplace contacts
    key = 'W'
    work_no = n_contacts[key]
    w_contacts = make_wcontacts(uids, ages, work_no)
    contacts[key] = w_contacts

    # random community contacts
    key = 'C'
    com_no = n_contacts[key]
    c_contacts = random_contacts(ages, com_no)
    contacts[key] = c_contacts

    # Custom layers: those that are not households, work, school or community
    custom_contacts = make_custom_contacts(uids,
                                           n_contacts,
                                           pop_size,
                                           ages,
                                           custom_lkeys,
                                           cluster_types,
                                           pop_proportion,
                                           age_lb,
                                           age_ub)
    contacts.update(custom_contacts)

    contacts_list = convert_contacts(contacts, uids, all_lkeys)

    return contacts_list, ages, uids
