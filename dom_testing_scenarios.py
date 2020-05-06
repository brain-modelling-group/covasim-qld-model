'''
Load Australian epi data
'''

import matplotlib

matplotlib.use('Agg')
matplotlib.use('TkAgg')
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop, policy_changes, os

dirname = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':  # need this to run in parallel on windows

    # What to do
    todo = ['loaddata',
            #'showplot',
            'saveplot',
            'gen_pop',
            'runsim_indiv',
            'doplot_indiv',
            ]

    for_powerpoint = False
    verbose = 1
    seed = 1

    # load parameters
    pars, metapars, extra_pars, population_subsets = load_parameters.load_pars()

    # Process and read in data
    if 'loaddata' in todo:
        sd, extra_pars['i_cases'], extra_pars['daily_tests'] = load_parameters.load_data(
            databook_path=extra_pars['databook_path'],
            start_day=pars['start_day'], end_day=extra_pars['end_day'], data_path=extra_pars['data_path'])

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'],
                                                  contact_numbers=pars['contacts'],
                                                  population_subsets=population_subsets)
        sc.saveobj(extra_pars['popfile'], popdict)

    sim = cv.Sim(pars, popfile=extra_pars['popfile'], datafile=extra_pars['data_path'], pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=extra_pars['popfile'])

    # Read a variety of policies from databook sheet 'policies', and set up the baseline according to their start and end dates
    policies = policy_changes.load_pols(databook_path=extra_pars['databook_path'], layers=pars['contacts'].keys(),
                                        start_day=pars['start_day'])
    # Set up a baseline scenario that includes all policy changes to date
    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, extra_pars)


    if 'runsim_indiv' in todo:  # run and plot a collection of policy scenarios together
        torun = {}

        torun['Pubs open'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        torun['Pubs open']['replace']['communication'] = {'replacements': ['comm_relax'],
                                                             'dates': [extra_pars['relax_day']]}
        torun['Pubs open']['turn_off'] = {'off_pols': ['pub_bar0'], 'dates': [extra_pars['relax_day']]}


        scenarios, scenario_policies = policy_changes.create_scens(torun, policies, baseline_policies, base_scenarios,
                                                                   pars, extra_pars)

        # fig = scenario_policies['Full relax'].plot_gantt(max_time=pars['n_days'], start_date=pars['start_day'])
        # fig.show()

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=scenarios)
    scens.run(verbose=verbose)

    if 'doplot_indiv' in todo:
        do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

        # Configure plotting
        fig_args = dict(figsize=(5, 10))
        this_fig_path = dirname + '/figures/dom/pubs' + 'prop25.png'
        if for_powerpoint:
            to_plot1 = ['new_infections', 'cum_infections', 'cum_deaths']
        else:
            to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

        utils.policy_plot(scens, plot_ints=True, do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28,
                          fig_args=fig_args, font_size=8, to_plot=to_plot1)
