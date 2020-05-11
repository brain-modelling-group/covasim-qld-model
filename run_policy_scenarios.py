
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
            'runsim_indiv',
            'doplot_indiv',
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
                                                  'coverage': [0.05, 0.3], # app coverage at time in days
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

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=scenarios)
    scens.run(verbose=verbose, debug=False)


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
                          fig_args=fig_args,font_size=8, y_lim={'r_eff': 3}, to_plot=to_plot1)
