
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
                                                                                         start_day=pars['start_day'], end_day=extra_pars['end_day'], data_path=extra_pars['data_path'], setting=extra_pars['setting'])

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets = population_subsets, setting=extra_pars['setting'])
        sc.saveobj(extra_pars['popfile'], popdict)
    else:
        popdict = sc.loadobj(extra_pars['popfile'])

    sim = cv.Sim(pars, popfile=extra_pars['popfile'], datafile=extra_pars['data_path'], pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=extra_pars['popfile'])

    # Read a variety of policies from databook sheet 'policies', and set up the baseline according to their start and end dates
    policies = policy_changes.load_pols(databook_path=extra_pars['databook_path'], layers=pars['contacts'].keys(),
                                        start_day=pars['start_day'])
    # ToDO: Tracing app policies need to be added to policies sheet and to policy read in function, also add start day (and end day?) to policies['policy_dates']
    policies['trace_policies'] = {'tracing_app': {'layers': ['pub_bar'], # Layers which the app can target, excluding beach, child_care and aged_care
                                                  'coverage': [0.05], # app coverage at time in days
                                                  'dates': [extra_pars['relax_day']], # days when app coverage changes
                                                  'trace_time': 0,
                                                  'start_day': extra_pars['relax_day'],
                                                  'end_day': None}}
    policies['policy_dates']['tracing_app'] = [policies['trace_policies']['tracing_app']['start_day']]
    # Set up a baseline scenario that includes all policy changes to date
    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, extra_pars, popdict)

    cov_values = [0.2, 0.4, 0.6, 0.8]
    policy = {'off_pols': ['pub_bar0'], 'dates': [extra_pars['relax_day']]}
    torun = {}
    torun['No app'] = {}
    torun['No app']['Pubs/bars open with no restrictions'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun['No app']['Pubs/bars open with no restrictions']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    torun['No app']['Pubs/bars open with no restrictions']['replace']['outdoor2'] = {'replacements': ['outdoor10'],'dates': [extra_pars['relax_day']]}
    torun['No app']['Pubs/bars open with no restrictions']['turn_off'] = {'off_pols': ['pub_bar0'], 'dates': [extra_pars['relax_day']]}
    torun['No app']['Pubs/bars open with 50% reduced trans.'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun['No app']['Pubs/bars open with 50% reduced trans.']['replace']['communication'] = {'replacements': ['comm_relax'],
                                                                     'dates': [extra_pars['relax_day']]}
    torun['No app']['Pubs/bars open with 50% reduced trans.']['replace']['outdoor2'] = {'replacements': ['outdoor10'],'dates': [extra_pars['relax_day']]}
    torun['No app']['Pubs/bars open with 50% reduced trans.']['replace']['pub_bar0'] = {'replacements': ['pub_bar_4sqm'],
                                                                                    'dates': [extra_pars['relax_day']]}
    scenarios, scenario_policies = policy_changes.create_scens(torun['No app'], policies, baseline_policies, base_scenarios,pars, extra_pars, popdict)
    for i, cov in enumerate(cov_values):
        policies['trace_policies']['tracing_app']['coverage'] = [cov]
        torun['App cov = '+str(round(100*cov))] = {}
        torun['App cov = '+str(round(100*cov))]['Pubs/bars open with ID checks (' + str(round(100*cov)) + '%)'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        torun['App cov = '+str(round(100*cov))]['Pubs/bars open with ID checks (' + str(round(100*cov)) + '%)']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
        torun['App cov = '+str(round(100*cov))]['Pubs/bars open with ID checks (' + str(round(100*cov)) + '%)']['replace']['outdoor2'] = {'replacements': ['outdoor10'], 'dates': [extra_pars['relax_day']]}
        torun['App cov = '+str(round(100*cov))]['Pubs/bars open with ID checks (' + str(round(100*cov)) + '%)']['turn_off'] = policy
        scenarios1, scenario_policies1 = policy_changes.create_scens(torun['App cov = '+str(round(100*cov))], policies, baseline_policies, base_scenarios, pars, extra_pars, popdict)
        scenarios = {**scenarios, **scenarios1}
    policies['trace_policies']['tracing_app']['coverage'] = [0.8]
    torun['No app 2'] = {}
    torun['No app 2']['Pubs/bars; 50% reduced trans. + ID (80%)'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun['No app 2']['Pubs/bars; 50% reduced trans. + ID (80%)']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    torun['No app 2']['Pubs/bars; 50% reduced trans. + ID (80%)']['replace']['outdoor2'] = {'replacements': ['outdoor10'], 'dates': [extra_pars['relax_day']]}
    torun['No app 2']['Pubs/bars; 50% reduced trans. + ID (80%)']['replace']['pub_bar0'] = {'replacements': ['pub_bar_4sqm'],'dates': [extra_pars['relax_day']]}
    scenarios1, scenario_policies1 = policy_changes.create_scens(torun['No app 2'], policies,baseline_policies, base_scenarios, pars, extra_pars, popdict)
    scenarios = {**scenarios, **scenarios1}

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=scenarios)
    scens.run(verbose=verbose)

    if 'doplot_indiv' in todo:
        do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

        # Configure plotting
        fig_args = dict(figsize=(5, 5))
        this_fig_path = dirname + '/figures/COVIDSafe_pubs' + '.png'
        to_plot1 = ['cum_infections', 'new_infections']

        utils.policy_plot(scens, plot_ints=True, do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28,
                          fig_args=fig_args,font_size=8, y_lim={'r_eff': 3,'cum_infections': 12000, 'new_infections': 200}, to_plot=to_plot1)
