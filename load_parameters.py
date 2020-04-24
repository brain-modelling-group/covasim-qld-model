def load_pars():
    import covasim as cv
    import sciris as sc

    state = 'vic'
    start_day = sc.readdate('2020-03-01')
    end_day = sc.readdate('2020-10-01')
    n_days = (end_day - start_day).days

    date = '2020apr19'
    folder = f'results_{date}'
    file_path = f'{folder}/{state}_'
    data_path = f'data/{state}-data-{date}.csv'  # This gets created and then read in
    databook_path = f'data/{state}-data.xlsx'
    popfile = f'data/popfile.obj'

    pars = cv.make_pars()  # generate some defaults
    metapars = cv.make_metapars()
    metapars['n_runs'] = 3

    pars['beta'] = 0.035
    pars['pop_size'] = 20000  # This will be scaled
    pars['pop_scale'] = 1  # 6.35e6/pars['pop_size']   # this gives a total VIC population
    pars['rescale'] = 1
    pars['rescale_threshold'] = 0.8  # Fraction susceptible population that will trigger rescaling if rescaling
    pars['rescale_factor'] = 2  # Factor by which we rescale the population
    pars['pop_infected'] = 5  # Number of initial infections
    pars['start_day'] = start_day  # Start date
    pars['n_days'] = n_days  # Number of days
    pars['contacts'] = {'H': 4, 'S': 7, 'W': 5, 'C': 5, 'Church': 10, 'pSport': 10,'beach_goer': 3}  # Number of contacts per person per day, estimated. Special contact types are between 1-100 (percentage)
    pars['beta_layer'] = {'H': 1.0, 'S': 0.5, 'W': 0.5, 'C': 0.1, 'Church': 0.5, 'pSport': 1.0, 'beach_goer': 0.1}
    pars['quar_eff'] = {'H': 1.0, 'S': 0.0, 'W': 0.0, 'C': 0.0, 'Church': 0.0, 'pSport': 0.0,
                        'beach_goer': 0.0}  # Set quarantine effect for each layer
    population_subsets = {}
    population_subsets['proportion'] = {'Church': 0.1, 'pSport': 0.01,
                                        'beach_goer': 0.05}  # proportion of the population who do these things
    population_subsets['age_lb'] = {'Church': 0, 'pSport': 18,
                                    'beach_goer': 0}  # proportion of the population who do these things
    population_subsets['age_ub'] = {'Church': 110, 'pSport': 40,
                                    'beach_goer': 110}  # proportion of the population who do these things
    population_subsets['cluster_type'] = {'Church': 'complete', 'pSport': 'complete',
                                          'beach_goer': 'partition'}  # proportion of the population who do these things


    trace_probs = {'H': 1.0, 'S': 0.8, 'W': 0.5, 'C': 0, 'Church': 0.05, 'pSport': 0.1,
                   'beach_goer': 0.1}  # contact tracing, probability of finding
    trace_time = {'H': 1, 'S': 2, 'W': 2, 'C': 20, 'Church': 10, 'pSport': 5, 'beach_goer': 20}  # number of days to find

    return state, start_day, end_day, n_days, date, folder, file_path, data_path, databook_path, popfile, pars, metapars, population_subsets, trace_probs, trace_time


def load_data(databook_path, start_day, end_day, data_path):
    import pandas as pd
    import numpy as np

    sd = pd.read_excel(databook_path, sheet_name='epi_data')
    sd.rename(columns={'Date': 'date',
                       'Cumulative case count': 'cum_infections',
                       'Cumulative deaths': 'cum_deaths',
                       'Tests conducted (total)': 'cum_test',
                       'Tests conducted (negative)': 'cum_neg',
                       'Hospitalisations (count)': 'n_severe',
                       'Intensive care (count)': 'n_critical',
                       'Recovered (cumulative)': 'cum_recovered',
                       'Daily imported cases': 'daily_imported_cases'
                       }, inplace=True)
    sd.set_index('date', inplace=True)
    sd['cum_infections'] = sd['cum_infections'] * 1.3  # Assume 20% of cases never diagnosed
    sd.loc[start_day:end_day].to_csv(data_path)

    i_cases = np.array(sd['daily_imported_cases'])
    i_cases = i_cases[6:len(i_cases)]  # shift 7 days back to account for lag in reporting time
    daily_tests = np.array(sd['new_tests'])

    return sd, i_cases, daily_tests