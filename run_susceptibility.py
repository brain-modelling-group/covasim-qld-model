
import matplotlib
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop, policy_changes, os, plot_scenarios
dirname = os.path.dirname(os.path.abspath(__file__))
import load_parameters_int, load_pop_int

if __name__ == '__main__': # need this to run in parallel on windows
    # What to do
    todo = ['loaddata',
            'showplot',
            'saveplot',
            'gen_pop',
            'gen_results', # Re-run the simulations, otherwise load pre-existing results
            # 'doplot_indiv',
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

    extra_pars['i_cases'][:] = 0

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
    # Set up a baseline scenario that includes all policy changes to date
    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, extra_pars, popdict)

    torun = plot_scenarios.plot_scenarios('1',extra_pars)
    scenarios, scenario_policies = policy_changes.create_scens(torun, policies, baseline_policies, base_scenarios, pars, extra_pars, popdict)

    labels = utils.pretty_labels  # A list of short, but nicer labels for policies currently in vic-data
    #fig = scenario_policies['Cafes/restaurants open'].plot_gantt(max_time=pars['n_days'], start_date=pars['start_day'], pretty_labels=labels)
    #fig.show()

    # torun = {k:v for k,v in scenarios.items() if k in ['Cafes/restaurants open','Schools','Social gatherings <10']}

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=scenarios)
    if 'gen_results' in todo:
        scens.run(verbose=verbose, debug=False)
        scens.save('susceptibility_dump')
    else:
        scens = cv.Scenarios.load('susceptibility_dump')

    if 'doplot_indiv' in todo:
        do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

        # Configure plotting
        fig_args = dict(figsize=(5, 5))
        this_fig_path = dirname + '/figures/combination' + '.png'
        to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
        to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
        to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
        to_plot_capacity = ['n_severe', 'n_critical']
        if for_powerpoint:
            to_plot1 = ['new_infections', 'cum_infections', 'cum_deaths']
        else:
            to_plot1 = ['cum_infections', 'new_infections']

        utils.policy_plot(scens, plot_ints=True, do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28,
                          fig_args=fig_args,font_size=8, y_lim={'r_eff': 3, 'cum_infections': 12000, 'new_infections': 500}, to_plot=to_plot1)



    # Susceptibility distribution plots
    import matplotlib.pyplot as plt
    import numpy as np
    import scipy.stats as stats

    p_less_than_100 = []

    fig, ax = plt.subplots()
    for scen_name in torun.keys():
        if scen_name == 'baseline':
            continue
        vals = np.array([x.results['cum_infections'][-1] for x in scens.sims[scen_name]])
        value_range = (vals.min(), vals.max())
        kernel = stats.gaussian_kde(vals.ravel())
        p_less_than_100.append(kernel.integrate_box(0,100))
        scale_up_range = 1.5  # Increase kernel density x range
        span = np.average(value_range) + np.diff(value_range) * [-1, 1] / 2 * scale_up_range
        x = np.linspace(*span, 100)
        h = plt.plot(x, kernel(x), label=scen_name)[0]
        color = h.get_color()
    plt.title('Number of infections after 30 days')
    plt.legend()

    idx = np.argsort(p_less_than_100)[::-1]
    p_less_than_100 = np.array(p_less_than_100)
    labels = np.array(list(torun.keys()))
    ind = np.arange(len(torun))  # the x locations for the groups
    width = 0.35  # the width of the bars: can also be len(x) sequence
    plt.figure()
    p1 = plt.bar(ind, p_less_than_100[idx], width, label='< 100', color='b')
    # p2 = plt.bar(ind, (1-p_less_than_100), width, bottom=p_less_than_100, label='> 100', color='r')
    plt.ylabel('Probability')
    plt.title('Probability of outbreak being contained to less than 100 people after 30 days')
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
    for scen_name in torun.keys():
        if scen_name == 'baseline':
            continue
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