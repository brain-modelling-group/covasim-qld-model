
import matplotlib
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop, policy_changes, os, plot_scenarios
dirname = os.path.dirname(os.path.abspath(__file__))
import load_parameters_int, load_pop_int

if __name__ == '__main__': # need this to run in parallel on windows
    # What to do
    todo = ['loaddata',
            'gen_pop',
            'gen_results', # Re-run the simulations, otherwise load pre-existing results
            ]

    for_powerpoint = False
    verbose    = 1
    seed       = 1

    # load parameters
    pars, metapars, extra_pars, population_subsets = load_parameters.load_pars()

    # Process and read in data
    if 'loaddata' in todo:
        sd, extra_pars['i_cases'], extra_pars['daily_tests'] = load_parameters.load_data(databook_path=extra_pars['databook_path'],
                                                                                         start_day=pars['start_day'],
                                                                                         end_day=extra_pars['end_day'],
                                                                                         data_path=extra_pars['data_path'],
                                                                                         setting=extra_pars['setting'])

    pars['pop_infected'] = 0
    pars['n_days'] = 90
    extra_pars['i_cases'][:] = 0
    extra_pars['restart_imports'] = 0,
    extra_pars['restart_imports_length'] = 0
    pars['rescale'] = 0
    pars['pop_scale'] = 1
    metapars['n_runs'] = 1000
    ncpus = 32

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'],
                                                  contact_numbers=pars['contacts'],
                                                  population_subsets = population_subsets,
                                                  setting=extra_pars['setting'])
        sc.saveobj(extra_pars['popfile'], popdict)
    else:
        popdict = sc.loadobj(extra_pars['popfile'])

    sim = cv.Sim(pars, popfile=extra_pars['popfile'], datafile=extra_pars['data_path'], pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=extra_pars['popfile'])

    # Read a variety of policies from databook sheet 'policies', and set up the baseline according to their start and end dates
    policies = policy_changes.load_pols(databook_path=extra_pars['databook_path'], layers=pars['contacts'].keys(),
                                        start_day=pars['start_day'])
    # ToDO: Tracing app policies need to be added to policies sheet and to policy read in function, also add start day (and end day?) to policies['policy_dates']
    policies['trace_policies'] = {'tracing_app': {'layers': ['H', 'S', 'C', 'Church', 'pSport', 'cSport', 'entertainment', 'cafe_restaurant',
                                                             'pub_bar', 'transport', 'national_parks', 'public_parks', 'large_events',
                                                             'social'], # Layers which the app can target, excluding beach, child_care and aged_care
                                                  'coverage': [0.05, 0.05], # app coverage at time in days
                                                  'dates': [60, 90], # days when app coverage changes
                                                  'trace_time': 0,
                                                  'start_day': 60,
                                                  'end_day': None}}
    policies['policy_dates']['tracing_app'] = [policies['trace_policies']['tracing_app']['start_day']]

    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, extra_pars, popdict)
    torun = plot_scenarios.plot_scenarios('1',extra_pars)
    scenarios, scenario_policies = policy_changes.create_scens(torun, policies, baseline_policies, base_scenarios, pars, extra_pars, popdict)

    # scenarios = {k:v for k,v in scenarios.items() if k == 'Full relaxation'}

    for scenario in scenarios.values():
        scenario['pars']['interventions'].append(utils.SeedInfection({61:1}))

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=scenarios)
    if 'gen_results' in todo:
        scens.run(verbose=verbose, debug=False, par_args={'ncpus':ncpus})
        scens.save('susceptibility_dump')
    else:
        scens = cv.Scenarios.load('susceptibility_dump')

    # Susceptibility distribution plots
    import matplotlib.pyplot as plt
    import numpy as np
    import scipy.stats as stats

    p_less_than_100 = []
    labels = []

    fig, ax = plt.subplots()
    for scen_name in scenarios.keys():
        vals = np.array([x.results['cum_infections'][-1] for x in scens.sims[scen_name]])
        value_range = (vals.min(), vals.max())
        kernel = stats.gaussian_kde(vals.ravel())
        p_less_than_100.append(sum(vals<100)/len(vals))
        # p_less_than_100.append(kernel.integrate_box(0,100)) # This is OK only if the KDE is good
        labels.append(scen_name)
        scale_up_range = 1.5  # Increase kernel density x range
        span = np.average(value_range) + np.diff(value_range) * [-1, 1] / 2 * scale_up_range
        x = np.linspace(*span, 100)
        h = plt.plot(x, kernel(x), label=scen_name)[0]
        color = h.get_color()
    plt.title('Number of infections after 30 days')
    plt.legend()

    idx = np.argsort(p_less_than_100)[::-1]
    p_less_than_100 = np.array(p_less_than_100)
    labels = np.array(labels)
    ind = np.arange(len(idx))  # the x locations for the groups
    width = 0.35  # the width of the bars: can also be len(x) sequence
    plt.figure()
    # p1 = plt.bar(ind, p_less_than_100[idx], width, label='< 100', color='b')
    p2 = plt.bar(ind, (1-p_less_than_100[idx]), width, label='> 100', color='r')
    plt.ylabel('Probability')
    plt.title('Probability of outbreak exceeding 100 people after 30 days')
    plt.xticks(ind, labels[idx])
    plt.show()

    # R_eff is quite noisy, maybe the algorithm could be changed
    # fig, ax = plt.subplots()
    # for scen_name in torun.keys():
    #     if scen_name == 'baseline':
    #         continue
    #     vals = np.array([x.results['r_eff'][-21:-7].mean() for x in scens.sims[scen_name]])
    #     value_range = (vals.min(), vals.max())
    #     kernel = stats.gaussian_kde(vals.ravel())
    #     scale_up_range = 1.5  # Increase kernel density x range
    #     span = np.average(value_range) + np.diff(value_range) * [-1, 1] / 2 * scale_up_range
    #     x = np.linspace(*span, 100)
    #     h = plt.plot(x, kernel(x), label=scen_name)[0]
    #     color = h.get_color()
    # plt.title('R_eff 7-14 days after initial infection')
    # plt.legend()

    fig, ax = plt.subplots()
    for scen_name in scenarios.keys():
        vals = np.array([x.results['doubling_time'][-21:-7].mean() for x in scens.sims[scen_name]])
        print(f'{scen_name}: {vals.mean()}')
        value_range = (vals.min(), vals.max())
        kernel = stats.gaussian_kde(vals.ravel())
        scale_up_range = 1.5  # Increase kernel density x range
        span = np.average(value_range) + np.diff(value_range) * [-1, 1] / 2 * scale_up_range
        x = np.linspace(*span, 100)
        h = plt.plot(x, kernel(x), label=scen_name)[0]
        color = h.get_color()
    plt.title('Doubling time 7-14 days after initial infection')
    plt.legend()


    # Just to check that a full exponential fit gives comparable results - it does
    #
    # def fit_doubling_time(sim):
    #     log_y = np.log(sim.results['cum_infections'][-21:-7])
    #     x = np.arange(0, len(log_y))
    #     coefs = np.polyfit(x, log_y, 1)
    #     doubling_time = np.log(2)/coefs[0]
    #     return doubling_time
    #
    # fig, ax = plt.subplots()
    # for scen_name in torun.keys():
    #     if scen_name == 'baseline':
    #         continue
    #     vals = np.array(list(map(fit_doubling_time, scens.sims[scen_name])))
    #     print(f'{scen_name}: {vals.mean()}')
    #
    #     value_range = (vals.min(), vals.max())
    #     kernel = stats.gaussian_kde(vals.ravel())
    #     scale_up_range = 1.5  # Increase kernel density x range
    #     span = np.average(value_range) + np.diff(value_range) * [-1, 1] / 2 * scale_up_range
    #     x = np.linspace(*span, 100)
    #     h = plt.plot(x, kernel(x), label=scen_name)[0]
    #     color = h.get_color()
    # plt.title('Doubling time (exponential fit) after initial infection')
    # plt.legend()