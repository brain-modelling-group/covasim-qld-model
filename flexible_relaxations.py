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

def replace_pols(pol_scen, policy, beta_policies, adapt_beta_policies, import_policies, adapt_clip_policies, policy_dates):
    for n, new_policy in enumerate(pol_scen[policy]['replacements']):
        if new_policy in beta_policies:
            if new_policy in policy_dates:
                if pol_scen[policy]['dates'][n] > policy_dates[new_policy][1]:
                    if n == 0:
                        adapt_beta_policies.add(new_policy, pol_scen[policy]['dates'][n])
                    else:
                        adapt_beta_policies.end(pol_scen[policy]['replacements'][n - 1], pol_scen[policy]['dates'][n])
                        if n == len(pol_scen[policy]['replacements']) - 1 and len(pol_scen[policy]['replacements']) < len(pol_scen[policy]['dates']):
                            adapt_beta_policies.add(new_policy, pol_scen[policy]['dates'][n], pol_scen[policy]['dates'][n+1])
                        else:
                            adapt_beta_policies.add(new_policy, pol_scen[policy]['dates'][n])
                else:
                    print('Beta layer policy %s could not be started on day %s because it is already set to run until day %s' % (policy, str(pol_scen[policy]['dates'][n]), str(policy_dates[new_policy][1])))
            else:
                if n == 0:
                    adapt_beta_policies.add(new_policy, pol_scen[policy]['dates'][n])
                else:
                    adapt_beta_policies.end(pol_scen[policy]['replacements'][n - 1], pol_scen[policy]['dates'][n])
                    if n == len(pol_scen[policy]['replacements']) - 1 and len(pol_scen[policy]['replacements']) < len(pol_scen[policy]['dates']):
                        adapt_beta_policies.add(new_policy, pol_scen[policy]['dates'][n], pol_scen[policy]['dates'][n + 1])
                    else:
                        adapt_beta_policies.add(new_policy, pol_scen[policy]['dates'][n])
        if new_policy in import_policies:
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(relax_day, pol_scen[policy]['dates'][0])),
                                vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (
                                            pol_scen[policy]['dates'][0] - relax_day)))
            trigger = True
        else:
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                vals=np.append(i_cases, [restart_imports] * 30))
            trigger = False
        if new_policy in adapt_clip_policies:
            if new_policy in policy_dates:
                if len(policy_dates[policy]) > 1:
                    if pol_scen[policy]['dates'][n] > policy_dates[new_policy][1]:
                        if n == 0:
                            adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                            if len(pol_scen[policy]['dates']) > 1:
                                adapt_clip_policies[new_policy + 'v2']['dates'] = [pol_scen[policy]['dates'][n], pol_scen[policy]['dates'][n+1]]
                            else:
                                adapt_clip_policies[new_policy + 'v2']['dates'] = [pol_scen[policy]['dates'][n], n_days]
                        else:
                            adapt_clip_policies[pol_scen[policy]['replacements'][n - 1] + 'v2'][1] = pol_scen[policy]['dates'][n]
                            adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                            if len(pol_scen[policy]['dates']) > n + 1:
                                adapt_clip_policies[new_policy + 'v2']['dates'] = [pol_scen[policy]['dates'][n], pol_scen[policy]['dates'][n+1]]
                            else:
                                adapt_clip_policies[new_policy + 'v2']['dates'] = [pol_scen[policy]['dates'][n], n_days]
                    else:
                        print('Clip edges policy %s could not be started on day %s because it is already set to run until day %s' % (policy, str(pol_scen[policy]['dates'][n]), str(policy_dates[new_policy][1])))
                else:
                    print('Clip edges policy %s could not be started on day %s because it is already set to run until the final day' % (policy, str(pol_scen[policy]['dates'][n])))
            else:
                if n == 0:
                    adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                    if len(pol_scen[policy]['dates']) > 1:
                        adapt_clip_policies[new_policy + 'v2']['dates'] = [pol_scen[policy]['dates'][n], pol_scen[policy]['dates'][n+1]]
                    else:
                        adapt_clip_policies[new_policy + 'v2']['dates'] = [pol_scen[policy]['dates'][n], n_days]
                else:
                    adapt_clip_policies[pol_scen[policy]['replacements'][n - 1] + 'v2'][1] = pol_scen[policy]['dates'][n]
                    adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                    if len(pol_scen[policy]['dates']) > n + 1:
                        adapt_clip_policies[new_policy + 'v2']['dates'] = [pol_scen[policy]['dates'][n], pol_scen[policy]['dates'][n+1]]
                    else:
                        adapt_clip_policies[new_policy + 'v2']['dates'] = [pol_scen[policy]['dates'][n], n_days]
    return adapt_beta_policies, imports_dict, trigger, adapt_clip_policies

def create_scen(scenarios, run, beta_policies, imports_dict, daily_tests, trace_probs, trace_time, clip_policies, policy_dates):
    scenarios[run] = {'name': run,
                      'pars': {
                      'interventions': [
                        beta_policies,
                        cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                            'n_imports': imports_dict
                        }),
                        cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                            ]
                        }
                     }
    # add edge clipping policies to relax scenario
    for policy in adapt_clip_policies:
        if len(adapt_clip_policies[policy]) >= 3:
            details = adapt_clip_policies[policy]
            scenarios[run]['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1], change={layer: details['change'] for layer in details['layers']}))
    return scenarios


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

    scen_names = []
    for policy in policy_dates:
        if len(policy_dates[policy]) == 1: #create list of ongoing policies
            scen_names.append(policy)
    non_beta_policies = {**import_policies, **clip_policies}
    for policy in non_beta_policies:
        if policy not in scen_names and policy in policy_dates:
            if policy_dates[policy][1] > 60:
                scen_names.append(policy)

    for n, name in enumerate(scen_names): #loop through all active policies and relax one at a time
        scen_policies = sc.dcp(baseline_policies)
        if name in beta_policies:
            scen_policies.end(name, 60) #add end day if policy is relaxed
        if name in import_policies: # add imports if border scenario is relaxed
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, import_policies[name]['dates'][-1])), vals=np.append(i_cases, [import_policies[name]['n_imports']] * (import_policies[name]['dates'][-1]-60)))
        else:
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [restart_imports] * 30))

        relax_scenarios[scen_names[n]] = {
            'name': scen_names[n],
            'pars': {
                'interventions': [
                    scen_policies,
                    cv.dynamic_pars({  # re-introduce imported infections to jump start
                        'n_imports': imports_dict
                    }),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                ]
            }
        }
        # add edge clipping policies to relax scenario
        for policy in clip_policies:
            if policy in policy_dates:
                details = clip_policies[policy]
                if name == policy:
                    end_day = 60  # change end day if policy is relaxed
                else:
                    end_day = details['dates'][1]
                relax_scenarios[scen_names[n]]['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=end_day, change={layer: details['change'] for layer in details['layers']}))

    '''
    The baseline scenario can be added to any of the turn_off, turn_on or replace dicts as ['baseline'].
    The relax all policies scenario must be added to the turn_off dict as ['Full relaxation'].
    Adding policies to the turn_off dict must be input as a list and will be relaxed on relax_day. Works with beta layer, import and clip edges policies.
    Adding policies to the turn_on dict must be input as a dict of {policy_name: [start_day, end_day]} for each policy, 
    with end_day being optional and n_days being used if it is not included. Import policies don't really work here as of yet.
    To add a policy it must either not be running in baseline, or end before start_day otherwise it will not be added (the scenario will still run).
    Adding policies to the replace dict must be input as a dict of dicts in the form 
    {policy_name: {'replacements': [policy_1,...,policy_n], 'dates': [start_day_1,..., start_day_n, end_day]}} for each policy, 
    with end_day being optional and n_days being used if it is not included. I think import policies work here, but testing hasn't been expansive.
    To add a replacement policy it must either not be running in baseline, or end before start_day otherwise it will not be added (the scenario will still run).
    '''
    if 'runsim_indiv' in todo: # run and plot a collection of policy scenarios together
        torun = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
        torun['turn_off']['Baseline'] = ['baseline']
        torun['turn_off']['Full relaxation'] = ['Full relaxation']
        #torun['turn_off']['Schools'] = ['schools']
        #torun['turn_off']['Pubs'] = ['pub_bar0']
        #torun['turn_off']['schools + pubs'] = ['schools', 'pub_bar0']
        #torun['turn_off']['Border opening'] = ['travel_dom']
        torun['turn_off'][' relax borders + schools + pubs'] = ['schools', 'pub_bar0', 'travel_dom']
        torun['replace']['replace Outdoors'] = {'outdoor2': {'replacements': ['outdoor10', 'outdoor200'], 'dates': [60, 90, 150]}}
        torun['replace']['replace NE work'] = {'NE_work': {'replacements': ['NE_health'], 'dates': [70, 150]}}
        torun['turn_on']['turn on Child care'] = {'child_care': [60, 150]}
        torun['turn_on']['turn on NE healthcare'] = {'NE_health': [70, 200]}
        relax_day = 60

        scenarios = {}
        #torun = scen_names
        for on_off in torun:
            if torun[on_off] and on_off == 'turn_off':
                for run in torun[on_off]:
                    pol_scen = torun[on_off][run]
                    trigger = False
                    if pol_scen == ['baseline']:
                        scenarios[pol_scen[0]] = base_scenarios[pol_scen[0]]
                    elif len(pol_scen) == 1:
                        try:
                            scenarios[pol_scen[0]] = relax_scenarios[pol_scen[0]]
                        except KeyError:
                            print("%s was not found as a policy to relax" % pol_scen[0])
                    elif len(pol_scen) > 1:
                        adapt_beta_policies = sc.dcp(baseline_policies)
                        adapt_clip_policies = sc.dcp(clip_policies)
                        for policy in pol_scen:
                            if policy in beta_policies:
                                adapt_beta_policies.end(policy, relax_day)
                            if policy in import_policies:
                                imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(relax_day, n_days)), vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (n_days-relax_day)))
                                trigger = True
                            elif not trigger:
                                imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [restart_imports] * 30))
                            if policy in clip_policies:
                                adapt_clip_policies[policy]['dates'] = [policy_dates[policy][0], relax_day]
                        scenarios = create_scen(scenarios, run, adapt_beta_policies, imports_dict, daily_tests, trace_probs, trace_time, adapt_clip_policies, policy_dates)
            elif torun[on_off] and on_off == 'replace':
                for run in torun[on_off]:
                    pol_scen = torun[on_off][run]
                    trigger = False
                    if pol_scen == ['baseline']:
                        scenarios[pol_scen[0]] = base_scenarios[pol_scen[0]]
                    else:
                        adapt_beta_policies = sc.dcp(baseline_policies)
                        adapt_clip_policies = sc.dcp(clip_policies)
                        for policy in pol_scen:
                            if policy in beta_policies:
                                adapt_beta_policies.end(policy, pol_scen[policy]['dates'][0])
                                adapt_beta_policies, imports_dict, trigger, adapt_clip_policies = replace_pols(pol_scen, policy, beta_policies, adapt_beta_policies, import_policies, adapt_clip_policies, policy_dates)
                            if policy in import_policies:
                                adapt_beta_policies, imports_dict, trigger, adapt_clip_policies = replace_pols(pol_scen, policy, beta_policies, adapt_beta_policies, import_policies, adapt_clip_policies, policy_dates)
                            elif not trigger:
                                imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [restart_imports] * 30))
                            if policy in clip_policies:
                                adapt_clip_policies[policy]['dates'][1] = pol_scen[policy]['dates'][0]
                                adapt_beta_policies, imports_dict, trigger, adapt_clip_policies = replace_pols(pol_scen, policy, beta_policies, adapt_beta_policies, import_policies, adapt_clip_policies, policy_dates)
                        scenarios = create_scen(scenarios, run, adapt_beta_policies, imports_dict, daily_tests, trace_probs, trace_time, adapt_clip_policies, policy_dates)
            elif torun[on_off] and on_off == 'turn_on':
                for run in torun[on_off]:
                    pol_scen = torun[on_off][run]
                    trigger = False
                    if pol_scen == ['baseline']:
                        scenarios[pol_scen[0]] = base_scenarios[pol_scen[0]]
                    else:
                        adapt_beta_policies = sc.dcp(baseline_policies)
                        adapt_clip_policies = sc.dcp(clip_policies)
                        for policy in pol_scen:
                            if policy in beta_policies:
                                if policy in policy_dates:
                                    if pol_scen[policy][0] > policy_dates[policy][1]:
                                        if len(pol_scen[policy]) > 1:
                                            adapt_beta_policies.add(policy, pol_scen[policy][0], pol_scen[policy][1])
                                        else:
                                            adapt_beta_policies.add(policy, pol_scen[policy][0], n_days)
                                    else:
                                        print('Beta layer policy %s could not be started on day %s because it is already set to run until day %s' % (policy, str(pol_scen[policy][0]), str(policy_dates[policy][1])))
                                else:
                                    if len(pol_scen[policy]) > 1:
                                        adapt_beta_policies.add(policy, pol_scen[policy][0], pol_scen[policy][1])
                                    else:
                                        adapt_beta_policies.add(policy, pol_scen[policy][0], n_days)
                            if policy in import_policies and policy not in policy_dates:
                                if len(pol_scen[policy]) > 1:
                                    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(pol_scen[policy][0], pol_scen[policy][1])), vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (pol_scen[policy]['dates'][1]-pol_scen[policy][0])))
                                else:
                                    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(pol_scen[policy][0], n_days)), vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (n_days-pol_scen[policy][0])))
                                trigger = True
                            elif policy in import_policies and policy in policy_dates:
                                if policy_dates[policy][1] < pol_scen[policy][0]:
                                    if len(pol_scen[policy]) > 1:
                                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[policy][0], policy_dates[policy][1]) + np.arange(pol_scen[policy][0], pol_scen[policy][1])), vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (policy_dates[policy][1] - policy_dates[policy][0]) + [import_policies[policy]['n_imports']] * (pol_scen[policy]['dates'][1]-pol_scen[policy][0])))
                                    else:
                                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[policy][0], policy_dates[policy][1]) + np.arange(pol_scen[policy][0], n_days)), vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (policy_dates[policy][1] - policy_dates[policy][0]) + [import_policies[policy]['n_imports']] * (n_days-pol_scen[policy][0])))
                                    trigger = True
                                else:
                                    print('Import policy %s could not be started on day %s because it is already set to run until day %s' % (policy, str(pol_scen[policy][0]), str(policy_dates[policy][1])))
                                    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [restart_imports] * 30))
                            elif not trigger:
                                imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [restart_imports] * 30))
                            if policy in clip_policies and policy not in policy_dates:
                                if len(pol_scen[policy]) > 1:
                                    adapt_clip_policies[policy]['dates'] = [pol_scen[policy][0], pol_scen[policy][1]]
                                else:
                                    adapt_clip_policies[policy]['dates'] = [pol_scen[policy][0], n_days]
                            elif policy in clip_policies and policy in policy_dates:
                                if len(policy_dates[policy]) > 1:
                                    if policy_dates[policy][1] > pol_scen[policy][0]:
                                        adapt_clip_policies[policy]['dates'] = [policy_dates[policy][0], n_days]
                                    else:
                                        print('Clip edges policy %s could not be started on day %s because it is already set to run until day %s' % (policy, str(pol_scen[policy][0]), str(policy_dates[policy][1])))
                                else:
                                    print('Clip edges policy %s could not be started on day %s because it is already set to run until the final day' % (policy, str(pol_scen[policy][0])))
                        scenarios = create_scen(scenarios, run, adapt_beta_policies, imports_dict, daily_tests, trace_probs, trace_time, adapt_clip_policies, policy_dates)
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
                to_plot1 = ['new_infections','cum_infections','cum_deaths']
            else:
                to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

            scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28, fig_args=fig_args, font_size=8, to_plot=to_plot1)
