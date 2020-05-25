import numpy as np
import contacts as co


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


def get_uids(pop_size):
    people_id = np.arange(start=0, stop=pop_size, step=1)
    return people_id


def get_popdict(params):
    contacts = {}

    pop_size = params.pars['pop_size']
    household_dist = params.household_dist
    age_dist = params.age_dist
    contact_matrix = params.contact_matrix
    n_contacts = params.pars['contacts']

    uids = get_uids(pop_size)

    # household contacts
    n_households = get_numhouseholds(household_dist, pop_size)
    household_heads = get_household_heads(age_dist, n_households)
    h_contacts, ages = co.make_hcontacts(n_households,
                                         pop_size,
                                         household_heads,
                                         uids,
                                         contact_matrix)
    contacts['H'] = h_contacts

    # school contacts
    key = 'S'
    social_no = n_contacts[key]
    s_contacts = co.make_scontacts(uids, ages, social_no)
    contacts[key] = s_contacts

    # workplace contacts
    key = 'W'
    work_no = n_contacts[key]
    w_contacts = co.make_wcontacts(uids, ages, work_no)
    contacts[key] = w_contacts

    # random community contacts
    key = 'C'
    com_no = n_contacts[key]
    c_contacts = co.random_contacts(ages, com_no)
    contacts[key] = c_contacts

    # Custom layers: those that are not households, work, school or community
    custom_lkeys = params.custom_lkeys
    cluster_types = params.layerchars['cluster_type']
    pop_proportion = params.layerchars['proportion']
    age_lb = params.layerchars['age_lb'] # todo: potentially confusing with the age_up in the contact matrix
    age_ub = params.layerchars['age_ub']

    custom_contacts = co.make_custom_contacts(uids, n_contacts, pop_size, ages, custom_lkeys, cluster_types, pop_proportion, age_lb, age_ub)
    contacts.update(custom_contacts)

    return
