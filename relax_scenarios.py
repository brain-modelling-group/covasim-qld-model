'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop
import numpy as np


if __name__ == '__main__': # need this to run in parallel on windows

    # What to do
    todo = ['loaddata',
            'showplot',
            'saveplot',
            'gen_pop',
            'runsim_indiv',
            'doplot_indiv',
            #'runsim_import',
            #'doplot_import'
            ]

    for_powerpoint = False
    verbose    = 1
    seed       = 1
    restart_imports = 10 # jump start epidemic with imports after day 60

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

    sim = cv.Sim(pars, popfile=popfile, datafile=data_path, pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=popfile)

    # Read a variety of policies from databook sheet 'policies'
    beta_policies, import_policies, clip_policies, policy_dates = load_parameters.load_pols(databook_path=databook_path, layers=pars['contacts'].keys(), start_day=start_day)

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
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)), vals=np.append(i_cases, [restart_imports] * (n_days - 60)))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * (n_days - len(daily_tests))), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    # add edge clipping policies to baseline scenario
    for policy in clip_policies:
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
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)),vals=np.append(i_cases, [restart_imports] * (n_days-60)))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * (n_days - len(daily_tests))), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    for policy in clip_policies: # Add relaxed clip edges policies
        details = clip_policies[policy]
        relax_scenarios['Full relaxation']['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=60, change={layer:details['change'] for layer in details['layers']}))

    scen_names = []
    for policy in policy_dates:
        if len(policy_dates[policy]) == 1: #create list of ongoing policies
            scen_names.append(policy)
    non_beta_policies = {**import_policies, **clip_policies}
    for policy in non_beta_policies:
        if policy not in scen_names and policy_dates[policy][1] > 60:
            scen_names.append(policy)

    for n, name in enumerate(scen_names):
        scen_policies = sc.dcp(baseline_policies)
        if name in beta_policies:
            scen_policies.end(name, 60) #add end day if policy is relaxed
        if name in import_policies: # add imports if border scenario is relaxed
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, import_policies[name]['dates'][-1])), vals=np.append(i_cases, [import_policies[name]['n_imports']] * (import_policies[name]['dates'][-1]-60)))
        else:
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)), vals=np.append(i_cases, [restart_imports] * (n_days - 60)))

        relax_scenarios[scen_names[n]] = {
            'name': scen_names[n],
            'pars': {
                'interventions': [
                    scen_policies,
                    cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                        'n_imports': imports_dict
                    }),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000] * (n_days - len(daily_tests))), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                ]
            }
        }
        # add edge clipping policies to relax scenario
        for policy in clip_policies:
            details = clip_policies[policy]
            if name == policy:
                end_day = 60  # change end day if policy is relaxed
            else:
                end_day = details['dates'][1]
            relax_scenarios[scen_names[n]]['pars']['interventions'].append(
                cv.clip_edges(start_day=details['dates'][0], end_day=end_day,
                              change={layer: details['change'] for layer in details['layers']}))


    if 'runsim_indiv' in todo:
        torun = {}
        torun['Baseline'] = ['baseline']
        torun['Full relaxation'] = ['Full relaxation']
        torun['Schools'] = ['schools']
        torun['Pubs'] = ['pub_bar0']
        #torun['schools + pubs'] = ['schools', 'pub_bar0']
        #torun['Border opening'] = ['travel_dom']
        #torun['borders + schools + pubs'] = ['schools', 'pub_bar0', 'travel_dom']
        relax_day = 60

        scenarios = {}
        #torun = scen_names
        for run in torun:
            trigger = False
            if torun[run] == ['baseline']:
                scenarios[torun[run][0]] = base_scenarios[torun[run][0]]
            elif len(torun[run]) == 1:
                try:
                    scenarios[torun[run][0]] = relax_scenarios[torun[run][0]]
                except KeyError:
                    print("%s was not found as a policy to relax" % torun[run][0])
            elif len(torun[run]) > 1:
                adapt_beta_policies = sc.dcp(baseline_policies)
                adapt_clip_policies = sc.dcp(clip_policies)
                for policy in torun[run]:
                    if policy in beta_policies:
                        adapt_beta_policies.end(policy, relax_day)
                    if policy in import_policies:
                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(relax_day, n_days)), vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (n_days-relax_day)))
                        trigger = True
                    elif not trigger:
                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)), vals=np.append(i_cases, [restart_imports] * (n_days-relax_day)))
                    if policy in clip_policies:
                        adapt_clip_policies[policy]['dates'] = [policy_dates[policy][0], relax_day]
                scenarios[run] = {
                    'name': run,
                    'pars': {
                    'interventions': [
                    adapt_beta_policies,
                    cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                        'n_imports': imports_dict
                    }),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000] * (n_days-len(daily_tests))), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                        ]
                    }
                }
                # add edge clipping policies to relax scenario
                for policy in adapt_clip_policies:
                    details = adapt_clip_policies[policy]
                    scenarios[run]['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1], change={layer: details['change'] for layer in details['layers']}))

        scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=scenarios)
        scens.run(verbose=verbose)

        ''' To individually run a relaxation of each policy againt the baseline
        for index, name in enumerate(relax_scenarios.keys()):
            if relax_scenarios[name]['name'] == run:
                scenarios = base_scenarios
                scenarios[name] = relax_scenarios[name]
        scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars = metapars, scenarios=scenarios)
        scens.run(verbose=verbose)
                    #del base_scenarios[run]
        '''

        if 'doplot_indiv' in todo:
            do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

            # Configure plotting
            fig_args = dict(figsize=(5, 10))
            this_fig_path = file_path + 'scens' + '.png'
            to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
            to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
            to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
            to_plot_capacity = ['n_severe', 'n_critical']
            if for_powerpoint:
                to_plot1 = ['new_infections','cum_infections','cum_deaths']
            else:
                to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

            scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28, fig_args=fig_args, font_size=8, to_plot=to_plot1)


    """ Sensitivity analysis around the number of imported infections per day

    for imports in [5, 10, 20, 50]:
        import_scenarios = {}
        import_scenarios['baseline'] = {
        'name': 'Baseline',
        'pars': {
            'interventions': [
                baseline_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [imports] * 30))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    # add edge clipping policies to baseline scenario
    for policy in clip_policies:
        details = clip_policies[policy]
        import_scenarios['baseline']['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1], change={layer:details['change'] for layer in details['layers']}))


        import_scenarios['Int0'] = {
        'name': 'Full relaxation',
        'pars': {
            'interventions': [
                relax_all_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)),vals=np.append(i_cases, [imports] * (n_days-60)))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    for policy in clip_policies: # Add relaxed clip edges policies
        details = clip_policies[policy]
        import_scenarios['Int0']['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=60, change={layer:details['change'] for layer in details['layers']}))


        for n, name in enumerate(scen_names):
            scen_policies = sc.dcp(baseline_policies)
            if name in beta_policies:
                scen_policies.end(name, 60) #add end day if policy is relaxed
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [imports] * 30))

            import_scenarios['Int'+str(n+1)] = {
                'name': scen_names[n],
                'pars': {
                    'interventions': [
                        scen_policies,
                        cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                            'n_imports': imports_dict
                        }),
                        cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                    ]
                }
            }
            # add edge clipping policies to relax scenario
            for policy in clip_policies:
                details = clip_policies[policy]
                if name == policy:
                    end_day = 60  # change end day if policy is relaxed
                else:
                    end_day = details['dates'][1]
                import_scenarios['Int'+str(n+1)]['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=end_day, change={layer: details['change'] for layer in details['layers']}))

        if 'runsim_import' in todo:
            scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=import_scenarios)
            scens.run(verbose=verbose)

        if 'doplot_import' in todo:
            do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

            # Configure plotting
            fig_args = dict(figsize=(8, 12))
            this_fig_path = file_path + str(imports) + 'imports.png'
            to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
            to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
            to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
            to_plot_capacity = ['n_severe', 'n_critical']
            if for_powerpoint:
                to_plot1 = ['new_infections', 'cum_deaths']
            else:
                to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

            scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28, fig_args=fig_args, font_size=8, to_plot=to_plot1)

    """
