import clusters as cl
import collections
import covasim as cv
import covasim.defaults as cvd
import covasim.utils as cvu
import numpy as np


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


def make_random_contacts(include, mean_number_of_contacts, dispersion=None, array_output=False):
    """
    Makes the random contacts either by sampling the number of contacts per person from a Poisson or Negative Binomial distribution


    Parameters
    ----------
    include (boolean array) length equal to the population size, containing True/1 if that person is eligible for contacts
    mean_number_of_contacts (int) representing the mean number of contacts for each person
    dispersion (float) if not None, use a negative binomial distribution with this dispersion parameter instead of Poisson to make the contacts
    array_output (boolean) return contacts as arrays or as dicts

    Returns
    -------
    If array_output=False, return a contacts dictionary {1:[2,3,4],2:[1,5,6]} with keys for source person,
        and a values being a list of target contacts.

    If array_output=True, return arrays with `source` and `target` indexes. These could be interleaved to produce an edge list
        representation of the edges

    """
    include_inds = np.nonzero(include)[0].astype(cvd.default_int)
    n_people = len(include_inds)

    # sample the number of edges from a given distribution
    if dispersion is None:
        number_of_contacts = cvu.n_poisson(rate=mean_number_of_contacts, n=n_people)
    else:
        number_of_contacts = cvu.n_neg_binomial(rate=mean_number_of_contacts, dispersion=dispersion, n=n_people)

    total_number_of_half_edges = sum(number_of_contacts)

    if array_output:
        count = 0
        source = np.zeros(total_number_of_half_edges).astype(dtype=cvd.default_int)
        for i, person_id in enumerate(include_inds):
            n_contacts = number_of_contacts[i]
            source[count:count+n_contacts] = person_id
            count += n_contacts
        target = np.random.permutation(source)

        return source, target

    contacts = {}
    count = 0
    target = include_inds[cvu.choose_r(max_n=n_people, n=total_number_of_half_edges)]
    for i, person_id in enumerate(include_inds):
        n_contacts = number_of_contacts[i]
        contacts[person_id] = target[count:count+n_contacts]
        count += n_contacts

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


def make_custom_contacts(uids, n_contacts, pop_size, ages, custom_lkeys, cluster_types, dispersion, pop_proportion, age_lb, age_ub):
    contacts = {}
    for layer_key in custom_lkeys:
        cl_type = cluster_types[layer_key]
        num_contacts = n_contacts[layer_key]
        # get the uid of people in the layer
        n_people = int(pop_proportion[layer_key] * pop_size)
        # randomly choose people from right age
        agel = age_lb[layer_key]
        ageu = age_ub[layer_key]
        inds = np.random.choice(uids[(ages > agel) & (ages < ageu)], n_people)
        # 1 if in layer, else 0
        in_layer = np.zeros_like(ages)
        in_layer[inds] = 1

        # handle the cluster types differently
        if cl_type == 'complete':   # number of contacts not used for complete clusters
            contacts[layer_key] = clusters_to_contacts([inds])
        elif cl_type == 'random':
            contacts[layer_key] = make_random_contacts(include=in_layer, mean_number_of_contacts=num_contacts, dispersion=dispersion[layer_key])
            # contacts[layer_key] = random_contacts(in_layer, num_contacts)
        elif cl_type == 'cluster':
            miniclusters = []
            miniclusters.extend(cl.create_clustering(inds, num_contacts))
            contacts[layer_key] = clusters_to_contacts(miniclusters)
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
    dispersion = params.layerchars['dispersion']
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
    include = np.ones(len(ages))
    c_contacts = make_random_contacts(include=include, mean_number_of_contacts=com_no, dispersion=dispersion['C'])
    contacts[key] = c_contacts

    # Custom layers: those that are not households, work, school or community
    custom_contacts = make_custom_contacts(uids,
                                           n_contacts,
                                           pop_size,
                                           ages,
                                           custom_lkeys,
                                           cluster_types,
                                           dispersion,
                                           pop_proportion,
                                           age_lb,
                                           age_ub)
    contacts.update(custom_contacts)

    contacts_list = convert_contacts(contacts, uids, all_lkeys)

    return contacts_list, ages, uids


def make_people(params):

    contacts, ages, uids = make_contacts(params)

    # create the popdict object
    popdict = {}
    popdict['contacts'] = contacts
    popdict['age'] = ages
    popdict['uid'] = uids

    people = cv.People(pars=params.pars, **popdict)

    return people, popdict
