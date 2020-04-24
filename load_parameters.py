def load_pars():
    import covasim as cv
    import sciris as sc
    import pandas as pd

    state = 'vic'

    date = '2020apr19'
    folder = f'results_{date}'
    file_path = f'{folder}/{state}_'
    data_path = f'data/{state}-data-{date}.csv'  # This gets created and then read in
    databook_path = f'data/{state}-data.xlsx'
    popfile = f'data/popfile.obj'

    layers = pd.read_excel(databook_path, sheet_name='layers')
    subset_names = list(layers['name'].unique())
    layers = layers.set_index('name')

    other_par = pd.read_excel(databook_path, sheet_name='other_par')
    other_par = other_par.set_index('name')

    start_day = sc.readdate(str(other_par['value'].start_day))
    end_day = sc.readdate(str(other_par['value'].end_day))
    n_days = (end_day - start_day).days

    pars = cv.make_pars()  # generate some defaults
    metapars = cv.make_metapars()
    metapars['n_runs'] = other_par['value'].n_runs

    pars['pop_size'] = other_par['value'].pop_size
    pars['pop_scale'] = other_par['value'].pop_scale
    pars['rescale'] = other_par['value'].rescale
    pars['rescale_threshold'] = other_par['value'].rescale_threshold
    pars['rescale_factor'] = other_par['value'].rescale_factor
    pars['pop_infected'] = other_par['value'].pop_infected
    pars['start_day'] = start_day  # Start date
    pars['n_days'] = n_days  # Number of days

    pars['contacts'] = {}
    pars['beta_layer'] = {}
    pars['quar_eff'] = {}

    for i in subset_names:
        pars['contacts'].update({i: layers['contacts'][i]})
        pars['beta_layer'].update({i: layers['beta_layer'][i]})
        pars['quar_eff'].update({i: layers['quar_eff'][i]})

    subset_names2 = subset_names[4:]

    population_subsets = {}
    population_subsets['proportion'] = {}
    population_subsets['age_lb'] = {}
    population_subsets['age_ub'] = {}
    population_subsets['cluster_type'] = {}

    for i in subset_names2:
        population_subsets['proportion'].update({i: layers['proportion'][i]})
        population_subsets['age_lb'].update({i: layers['age_lb'][i]})
        population_subsets['age_ub'].update({i: layers['age_ub'][i]})
        population_subsets['cluster_type'].update({i: layers['cluster_type'][i]})

    pars['beta'] = other_par['value'].beta
    trace_probs = {}
    trace_time = {}

    for i in subset_names:
        trace_probs.update({i: layers['trace_probs'][i]})
        trace_time.update({i: layers['trace_time'][i]})

    return state, start_day, end_day, n_days, date, folder, file_path, data_path, databook_path, popfile, pars, metapars, population_subsets, trace_probs, trace_time


def load_data(databook_path, start_day, end_day, data_path):
    import pandas as pd
    import numpy as np

    sd = pd.read_excel(databook_path, sheet_name='epi_data')
    other_par = pd.read_excel(databook_path, sheet_name='other_par')
    other_par = other_par.set_index('name')
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
    sd['cum_infections'] = sd['cum_infections'] * (1 + other_par['value'].undiag)  # Assume 20% of cases never diagnosed
    sd.loc[start_day:end_day].to_csv(data_path)

    i_cases = np.array(sd['daily_imported_cases'])
    i_cases = i_cases[6:len(i_cases)]  # shift 7 days back to account for lag in reporting time
    daily_tests = np.array(sd['new_tests'])

    return sd, i_cases, daily_tests