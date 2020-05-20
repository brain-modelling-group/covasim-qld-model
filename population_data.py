import numpy as np


def get_numhouseholds(household_dist, pop_size):
    """Calculates the number of households we need to create to meet the population size"""
    n_people = household_dist.index * household_dist  # n_people = household_size * n_households
    household_percent = household_dist / n_people
    n_households = (pop_size * household_percent).round().astype(int)
    n_households[1] += pop_size - sum(n_households * n_households.index)  # adjust single-person households to fill the gap
    return n_households


def get_household_heads(age_dist, n_households):
    """Selects the ages of the household heads by randomly choosing selecting from the available ages"""
    # prevent anyone under the age of 18 being chosen
    age_dist.iloc[0:18] = 0
    # decrease probability of someone aged 18-28 being chosen
    age_dist.iloc[18:28] *= np.linspace(0.1, 1, 10)

    # randomly choose household head, given the number of people in each age
    age_prob = age_dist.values / sum(age_dist.values)
    household_heads = np.random.choice(age_dist.index, size=sum(n_households), p=age_prob)
    return household_heads




# def read_sex(databook):
#     sex = databook.parse('age_sex')
#     sex['frac_male'] = sex['Male'] / (sex['Male'] + sex['Female'])
#     sex['frac_male'] = sex['frac_male'].fillna(0.5)  # if 0, replace with 0.5
#

class PopulationData:
    def __init__(self):
        self.foo = None