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
                                                                                         start_day=pars['start_day'], end_day=extra_pars['end_day'], data_path=extra_pars['data_path'])

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets = population_subsets)
        sc.saveobj(extra_pars['popfile'], popdict)

    sim = cv.Sim(pars, popfile=extra_pars['popfile'], datafile=extra_pars['data_path'], pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=extra_pars['popfile'])

    # Read a variety of policies from databook sheet 'policies', and set up the baseline according to their start and end dates
    policies = policy_changes.load_pols(databook_path=extra_pars['databook_path'], layers=pars['contacts'].keys(),
                                        start_day=pars['start_day'])
    # Set up a baseline scenario that includes all policy changes to date
    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, extra_pars)

    '''
    The required structure for the torun dict is:
    torun[scen_name] = {
                        'turn_off': {'off_pols': [off_pol_1, ..., off_pol_n], 'dates': [day_1, ..., day_n]},
                        'turn_on': {on_pol_1: [start_day_1, end_day_1], ..., on_pol_m: [start_day_m, end_day_m]},
                        'replace': {old_pol_1: {'replacements': [new_pol_11, ..., new_pol_1p], 'dates': [start_day_11, ..., start_day_1p, end_day_1]},
                                    ...
                                    old_pol_q: {'replacements': [new_pol_q1, ..., new_pol_qr], 'dates': [start_day_q1, ..., start_day_qr, end_day_q]}}
                        }

    The baseline scenario is automatically added to the scenarios first.
    The relax all policies scenario must be added to the torun dict as the key 'Full relaxation' or 'Full relax'.
    Adding policies to the turn_off dict must be added as a list of policies and a list of days to turn them off. Works with beta layer, import and clip edges policies.
    The policy being turned off must be on in the baseline or nothing will happen.
    Adding policies to the turn_on dict must be input as a dict of {policy_name: [start_day, end_day]} for each policy, 
    with end_day being optional and n_days being used if it is not included. Import policies don't really work here as of yet.
    To add a policy it must either not be running in baseline, or end before start_day otherwise it will not be added (the scenario will still run).
    Adding policies to the replace dict must be input as a dict of dicts in the form 
    {policy_name: {'replacements': [policy_1,...,policy_n], 'dates': [start_day_1,..., start_day_n, end_day]}} for each policy, 
    with end_day being optional and n_days being used if it is not included. I think import policies work here, but testing hasn't been expansive.
    To add a replacement policy it must either not be running in baseline, or end before start_day otherwise it will not be added (the scenario will still run).
    
    The function check_policy_changes reads the scenario being run from torun and checks for clashes between policies being turned off/policies being replaced 
    and policies being turned on/policies being replaced. It removes clashing policy changes, prioritising replacements over turning policies off/on.
    For example, if the pub_bar0 policy (running from day 21 to n_day) was set in the turn_off dict with a date of day 70 AND it was set 
    in the replace dict (as an old_pol) with a date of day 100 then it would be removed from the turn_off dict. I haven't figured out how to check
    consistencies across the replacement policies so please check that they are sensible (e.g., don't replace the same policy twice in the same scenario etc).
    Other checks for whether policies are off/on before being turned off/on are included within the turn_off_policies, turn_on_policies and replace_policies functions.
    '''
    if 'runsim_indiv' in todo: # run and plot a collection of policy scenarios together
        torun = {}
        #torun['Full relax'] = {}
        #torun['test1'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        # torun['test1']['turn_off']['Schools'] = ['schools']
        # torun['test1']['turn_off']['Pubs'] = ['pub_bar0']
        # torun['test1']['turn_off']['schools + pubs'] = ['schools', 'pub_bar0']
        # torun['test1']['turn_off']['Border opening'] = ['travel_dom']
        #torun['test1']['turn_off'] = {'off_pols': ['schools', 'retail', 'pub_bar0', 'travel_dom'], 'dates': [60, 60, 65, 70]}
        #torun['test1']['turn_on']['child_care'] = [60, 150]
        #torun['test1']['turn_on']['NE_health'] = [60, 120]
        #torun['test1']['turn_on']['schools'] = [80, 200]
        #torun['test1']['replace']['outdoor2'] = {'replacements': ['outdoor10', 'outdoor200'], 'dates': [60, 90, 150]}
        #torun['test1']['replace']['NE_work'] = {'replacements': ['church_4sqm'], 'dates': [70, 150]}
        #torun['Relax physical distancing'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        #torun['Relax physical distancing']['replace']['communication'] = {'replacements': ['comm2'], 'dates': [60]}

        torun['Schools open'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        torun['Schools open']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}
        torun['Schools open']['turn_off'] = {'off_pols': ['schools'], 'dates': [extra_pars['relax_day']]}
        torun['Pubs open'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        torun['Pubs open']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}
        torun['Pubs open']['turn_off'] = {'off_pols': ['pub_bar0'], 'dates': [extra_pars['relax_day']]}
        torun['Community sports start'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        torun['Community sports start']['turn_off'] = {'off_pols': ['cSports', 'communication'], 'dates': [extra_pars['relax_day'], extra_pars['relax_day']]}
        torun['Cafe/restaurant open with 4sqm'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        torun['Cafe/restaurant open with 4sqm']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}
        torun['Cafe/restaurant open with 4sqm']['replace']['cafe_restaurant0'] = {'replacements': ['cafe_restaurant_4sqm'], 'dates': [extra_pars['relax_day']]}
        torun['Large events'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        # torun['Schools + relax']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [60]}
        torun['Large events']['turn_off'] = {'off_pols': ['large_events'], 'dates': [60]}
        torun['Large events']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
        #torun['Return non-essential workers'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        #torun['Return non-essential workers']['turn_off'] = {'off_pols': ['NE_work'], 'dates': [extra_pars['relax_day']]}
        torun['Social gatherings <10'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        torun['Social gatherings <10']['turn_off'] = {'off_pols': ['social'], 'dates': [extra_pars['relax_day']]}
        torun['Social gatherings <10']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}

        intervention_plotting

        labels = utils.pretty_labels # A list of short, but nicer labels for policies currently in vic-data


        scenarios, poliy_schedule = policy_changes.create_scens(torun, policies, baseline_policies, base_scenarios, pars, extra_pars)

        fig = policy_schedule.plot_gantt(max_time=pars['n_days'], start_date=pars['start_day'], pretty_labels=labels)
        fig.show()

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=scenarios)
    scens.run(verbose=verbose)

    if 'doplot_indiv' in todo:
        do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

        # Configure plotting
        fig_args = dict(figsize=(5, 10))
        this_fig_path = dirname + '/figures/scens' + 'tests.png'
        to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
        to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
        to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
        to_plot_capacity = ['n_severe', 'n_critical']
        if for_powerpoint:
            to_plot1 = ['new_infections', 'cum_infections', 'cum_deaths']
        else:
            to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

        utils.policy_plot(scens, plot_ints=True, do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28, fig_args=fig_args,font_size=8, to_plot=to_plot1)

