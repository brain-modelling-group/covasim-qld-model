'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop, policy_changes
import numpy as np

if __name__ == '__main__': # need this to run in parallel on windows

    # What to do
    todo = ['loaddata',
            'showplot',
            'saveplot',
            #'gen_pop',
            'runsim_indiv',
            'doplot_indiv',
            ]

    for_powerpoint = True
    verbose    = 1
    seed       = 1
    restart_imports = 5 # jump start epidemic with imports after day 60

    # load parameters
    state, start_day, end_day, n_days, date, folder, file_path, data_path, databook_path, popfile, pars, metapars, \
    population_subsets, trace_probs, trace_time = load_parameters.load_pars()

    # Process and read in data
    if 'loaddata' in todo:
        sd, i_cases, daily_tests = load_parameters.load_data(databook_path=databook_path, start_day=start_day, end_day=end_day, data_path=data_path)

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets = population_subsets)
        sc.saveobj(popfile, popdict)

    pars['beta'] = 0.07 # Scale beta
    pars['diag_factor'] = 1.6 # Scale proportion asymptomatic

    sim = cv.Sim(pars, popfile=popfile, datafile=data_path, use_layers=True, pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=popfile)

    # Read a variety of policies from databook sheet 'policies'
    policies = policy_changes.load_pols(databook_path=databook_path, layers=pars['contacts'].keys(), start_day=start_day)
    beta_policies = policies['beta_policies']
    import_policies = policies['import_policies']
    clip_policies = policies['clip_policies']
    policy_dates = policies['policy_dates']

    baseline_policies = utils.PolicySchedule(pars['beta_layer'], beta_policies) #create policy schedule with beta layer adjustments
    for d, dates in enumerate(policy_dates): # add start and end dates to beta layer, import and edge clipping policies
        if len(policy_dates[dates]) == 2:
            if dates in beta_policies:
                baseline_policies.add(dates, policy_dates[dates][0], policy_dates[dates][1])
            if dates in import_policies:
                import_policies[dates]['dates'] = np.arange(policy_dates[dates][0], policy_dates[dates][1])
            if dates in clip_policies:
                clip_policies[dates]['dates'] = [policy_dates[dates][0], policy_dates[dates][1]]
        elif len(policy_dates[dates]) == 1:
            if dates in beta_policies:
                baseline_policies.add(dates, policy_dates[dates][0])
            if dates in import_policies:
                import_policies[dates]['dates'] = np.arange(policy_dates[dates][0], n_days)
            if dates in clip_policies:
                clip_policies[dates]['dates'] = [policy_dates[dates][0], n_days]

    base_scenarios = {} #create baseline scenario according to policies from databook
    base_scenarios['baseline'] = {
        'name': 'Baseline',
        'pars': {
            'interventions': [
                baseline_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [restart_imports] * 30))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    # add edge clipping policies to baseline scenario
    for policy in clip_policies:
        if policy in policy_dates:
            details = clip_policies[policy]
            base_scenarios['baseline']['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1], change={layer:details['change'] for layer in details['layers']}))

    relax_scenarios = {}

    # Relax all policies
    relax_all_policies = sc.dcp(baseline_policies)
    for dates in policy_dates:
        if len(policy_dates[dates]) == 1 and dates in beta_policies:
            relax_all_policies.end(dates, 60)

    relax_scenarios['Full relaxation'] = {
        'name': 'Full relaxation',
        'pars': {
            'interventions': [
                relax_all_policies,
                cv.dynamic_pars({  # jump start with imported infections
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)),vals=np.append(i_cases, [restart_imports] * (n_days-60)))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    for policy in clip_policies: # Add relaxed clip edges policies
        if policy in policy_dates:
            details = clip_policies[policy]
            relax_scenarios['Full relaxation']['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=60, change={layer:details['change'] for layer in details['layers']}))

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
        torun['Full relax'] = {}
        torun['test1'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        # torun['test1']['turn_off']['Schools'] = ['schools']
        # torun['test1']['turn_off']['Pubs'] = ['pub_bar0']
        # torun['test1']['turn_off']['schools + pubs'] = ['schools', 'pub_bar0']
        # torun['test1']['turn_off']['Border opening'] = ['travel_dom']
        torun['test1']['turn_off'] = {'off_pols': ['schools', 'retail', 'pub_bar0', 'travel_dom'], 'dates': [60, 60, 65, 70]}
        torun['test1']['turn_on']['child_care'] = [60, 150]
        torun['test1']['turn_on']['NE_health'] = [60, 120]
        torun['test1']['turn_on']['schools'] = [80, 200]
        torun['test1']['replace']['outdoor2'] = {'replacements': ['outdoor10', 'outdoor200'], 'dates': [60, 90, 150]}
        torun['test1']['replace']['NE_work'] = {'replacements': ['church_4sqm'], 'dates': [70, 150]}


        scenarios = sc.dcp(base_scenarios) # Always add baseline scenario
        beta_schedule, adapt_clip_policies, adapt_beta_policies = sc.dcp(baseline_policies), sc.dcp(clip_policies), sc.dcp(beta_policies)
        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [restart_imports] * 30))
        for run_pols in torun:
            if run_pols == 'Full relaxation' or run_pols == 'Full relax':
                scenarios['Full relaxation'] = sc.dcp(relax_scenarios['Full relaxation'])
            else:
                torun[run_pols] = utils.check_policy_changes(torun[run_pols])  # runs check on consistency across input off/on/replace policies and dates and remove inconsistencies
                for off_on in torun[run_pols]:
                    if off_on == 'turn_off':
                        beta_schedule, imports_dict, clip_schedule, policy_dates = utils.turn_off_policies(torun[run_pols], beta_schedule, adapt_beta_policies, import_policies, adapt_clip_policies, i_cases, n_days, policy_dates, imports_dict)
                        # for each policy, check if it's already off at specified date, if it's on then turn off at specified date. Update beta, import and clip.
                    elif off_on == 'turn_on':
                        beta_schedule, imports_dict, clip_schedule, policy_dates = utils.turn_on_policies(torun[run_pols], beta_schedule, adapt_beta_policies, import_policies, adapt_clip_policies, i_cases, n_days, policy_dates, imports_dict)
                        # for each policy, check if it's already on at specified date, if it's off then turn on at specified date and off at
                        # specified date (if input). Update beta, import and clip.
                    elif off_on == 'replace':
                        beta_schedule, imports_dict, clip_schedule, policy_dates = utils.replace_policies(torun[run_pols], beta_schedule, adapt_beta_policies, import_policies, adapt_clip_policies, i_cases, n_days, policy_dates, imports_dict)
                        # for each policy, check if it's already off at specified date, if it's on then check if first replacement policy is
                        # already on at specified date, if replacement is off then turn on and iterate with following replacements. Update beta, import and clip.
                    else:
                        print('Invalid policy change type %s added to to_run dict, types should be turn_off, turn_on or replace.' % off_on)
                scenarios = utils.create_scen(scenarios, run_pols, beta_schedule, imports_dict, daily_tests, trace_probs, trace_time, clip_schedule)
    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=scenarios)
    scens.run(verbose=verbose)

    if 'doplot_indiv' in todo:
        do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

        # Configure plotting
        fig_args = dict(figsize=(5, 10))
        this_fig_path = file_path + 'scens' + 'tests.png'
        to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
        to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
        to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
        to_plot_capacity = ['n_severe', 'n_critical']
        if for_powerpoint:
            to_plot1 = ['new_infections', 'cum_infections', 'cum_deaths']
        else:
            to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

        scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28, fig_args=fig_args,font_size=8, to_plot=to_plot1)