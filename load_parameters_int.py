def load_pars():
    import covasim as cv
    import sciris as sc
    import pandas as pd
    import numpy as np

    setting = 'Australia'

    date = '2020may05'
    folder = f'results_{date}'
    file_path = f'{folder}/{setting}_'
    data_path = f'data_int/{setting}-data-{date}.csv'  # This gets created and then read in
    databook_path = f'data_int/input_data.xlsx'
    popfile = f'data_int/{setting}_popfile.obj'

    layers = pd.read_excel(databook_path, sheet_name='layers-main', header=[0,1], index_col=0)
    layers2 = pd.read_excel(databook_path, sheet_name='layers-other', header=[0, 1], index_col=0)
    subset_names = list(np.unique([i[0] for i in list(layers.columns)]))
    subset_names2 = list(np.unique([i[0] for i in list(layers2.columns)]))

    other_par = pd.read_excel(databook_path, sheet_name='other_par', index_col=0)

    start_day = sc.readdate(str(other_par.start_day[setting]))
    end_day = sc.readdate(str(other_par.end_day[setting]))
    n_days = (end_day - start_day).days

    pars = cv.make_pars()  # generate some defaults
    metapars = cv.make_metapars()
    metapars['n_runs'] = other_par.n_runs[setting]

    pars['pop_size'] = other_par.pop_size[setting]
    pars['pop_scale'] = other_par.pop_scale[setting]
    pars['rescale'] = other_par.rescale[setting]
    pars['rescale_threshold'] = other_par.rescale_threshold[setting]
    pars['rescale_factor'] = other_par.rescale_factor[setting]
    pars['pop_infected'] = other_par.pop_infected[setting]
    pars['start_day'] = start_day  # Start date
    pars['n_days'] = n_days  # Number of days

    pars['contacts'] = {}
    pars['beta_layer'] = {}
    pars['quar_eff'] = {}

    for i in subset_names:
        pars['contacts'].update({i: layers.loc[setting, (i, 'contacts')]})
        pars['beta_layer'].update({i: layers.loc[setting, (i, 'beta_layer')]})
        pars['quar_eff'].update({i: layers.loc[setting, (i, 'quar_eff')]})

    for i in subset_names2:
        pars['contacts'].update({i: layers2.loc[setting, (i, 'contacts')]})
        pars['beta_layer'].update({i: layers2.loc[setting, (i, 'beta_layer')]})
        pars['quar_eff'].update({i: layers2.loc[setting, (i, 'quar_eff')]})

    population_subsets = {}
    population_subsets['proportion'] = {}
    population_subsets['age_lb'] = {}
    population_subsets['age_ub'] = {}
    population_subsets['cluster_type'] = {}

    for i in subset_names2:
        population_subsets['proportion'].update({i: layers2.loc[setting, (i, 'proportion')]})
        population_subsets['age_lb'].update({i: layers2.loc[setting, (i, 'age_lb')]})
        population_subsets['age_ub'].update({i: layers2.loc[setting, (i, 'age_ub')]})
        population_subsets['cluster_type'].update({i: layers2.loc[setting, (i, 'cluster_type')]})

    pars['beta'] = other_par.beta[setting]
    trace_probs = {}
    trace_time = {}

    for i in subset_names:
        trace_probs.update({i: layers.loc[setting, (i, 'trace_probs')]})
        trace_time.update({i: layers.loc[setting, (i, 'trace_time')]})

    for i in subset_names2:
        trace_probs.update({i: layers2.loc[setting, (i, 'trace_probs')]})
        trace_time.update({i: layers2.loc[setting, (i, 'trace_time')]})

    extra_pars = {}
    extra_pars['setting'] = setting
    extra_pars['date'] = date
    extra_pars['folder'] = folder
    extra_pars['file_path'] = file_path
    extra_pars['data_path'] = data_path
    extra_pars['databook_path'] = databook_path
    extra_pars['popfile'] = popfile
    extra_pars['trace_probs'] = trace_probs
    extra_pars['trace_time'] = trace_time
    extra_pars['end_day'] = end_day
    extra_pars['restart_imports'] = other_par.restart_imports[setting]  # jump start epidemic with imports after day 60
    extra_pars['restart_imports_length'] = other_par.restart_imports_length[setting]
    extra_pars['relax_day'] = other_par.relax_day[setting]
    extra_pars['future_daily_tests'] = other_par.future_daily_tests[setting]

    pars['beta'] = 0.125  # Scale beta
    pars['diag_factor'] = 1.6  # Scale proportion asymptomatic

    return pars, metapars, extra_pars, population_subsets