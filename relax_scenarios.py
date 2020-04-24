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
    '''Include runsim_indiv and doplot_indiv if you want to produce individual scenario plots against a baseline (assuming 5 importations per day from days 60-90)
    Include runsim_import and doplot_import if you want to produce plots of all scenarios against a baseline (assuming 5, 10, 20, 50 importations per day from days 60-90)'''
    todo = ['loaddata',
            #'runsim_indiv',
            #'doplot_indiv',
            'runsim_import',
            'doplot_import',
            'showplot',
            'saveplot',
            'gen_pop'
            ]

    verbose    = 1
    seed       = 1

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

    sim = cv.Sim(pars, popfile=popfile, datafile=data_path, use_layers=True, pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=popfile)

    policies = {}
    policies['day15'] = dict(H=1.02, S=1, W=1, C=0.98, Church=1, pSport=1)  # day 15: international travellers self isolate                            , public events >500 people cancelled
    policies['day19'] = dict(H=1.05, S=0.75, W=1, C=0.9, Church=0.0, pSport=1)  # day 19: indoor gatherings limited to 100 people
    policies['day22'] = dict(H=1.06, S=0.5, W=0.88, C=0.82, Church=0.0, pSport=0.0)  # day 22: pubs/bars/cafes take away only                                     , church/sport etc. cancelled
    policies['day29'] = dict(H=1.13, S=0.25, W=0.67, C=0.55, Church=0.0, pSport=0.0)  # day 29: public gatherings limited to 2 people

    # CAUTION - make sure these values are relative to baseline, not relative to day 29
    policies['Outdoor10'] = dict(H=1.13, S=0.25, W=0.67, C=0.69, Church=0.0, pSport=0.0)  # day 60: relax outdoor gatherings to 10 people
    policies['Retail'] = dict(H=1.13, S=0.25, W=0.72, C=0.82, Church=0.0, pSport=0.0)  # day 60: non-essential retail outlets reopen
    policies['Hospitalitylimited'] = dict(H=1.13, S=0.25, W=0.71, C=0.71, Church=0.0, pSport=0.0)  # day 60: restaurants/cafes/bars allowed to do eat in with 4 sq m distancing
    policies['Outdoor200'] = dict(H=1.13, S=0.25, W=0.67, C=0.59, Church=0.0, pSport=0.0)  # day 60: relax outdoor gatherings to 200 people
    policies['Sports'] = dict(H=1.13, S=0.25, W=0.67, C=0.63, Church=0.0, pSport=0.0)  # day 60: community sports reopen
    policies['School'] = dict(H=1.13, S=1, W=0.67, C=0.55, Church=0.0, pSport=0.0)  # day 60: childcare and schools reopen
    policies['Work'] = dict(H=1.13, S=0.25, W=1, C=0.55, Church=0.0, pSport=0.0)  # day 60: non-essential work reopens
    policies['ProSports'] = dict(H=1.13, S=0.25, W=0.67, C=0.55, Church=0.0, pSport=1)  # day 60: professional sport without crowds allowed
    policies['Church'] = dict(H=1.13, S=0.25, W=0.67, C=0.55, Church=1, pSport=0.0)  # day 60: places of worship reopen

    baseline_policies = utils.PolicySchedule(pars['beta_layer'],policies)
    baseline_policies.add('day15',15,19)
    baseline_policies.add('day19',19,22)
    baseline_policies.add('day22',22,29)
    baseline_policies.add('day29',29) # Add this policy without an end day

    base_scenarios = {}
    base_scenarios['baseline2'] = {
        'name': 'baseline2',
        'pars': {
            'interventions': [
                baseline_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),vals=np.append(i_cases, [5] * 30))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }

    relax_scenarios = {}

    # Relax all policies
    relax_all_policies = sc.dcp(baseline_policies)
    relax_all_policies.end('day29',60)
    relax_scenarios['Int0'] = {
        'name': 'Fullrelax',
        'pars': {
            'interventions': [
                relax_all_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),vals=np.append(i_cases, [5] * 30))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }


    scen_names = ['Outdoor10', 'Retail', 'Hospitalitylimited', 'Outdoor200', 'Sports', 'School', 'Work', 'ProSports', 'Church']

    for n, name in enumerate(scen_names):
        scen_policies = sc.dcp(baseline_policies)
        scen_policies.end('day29', 60) # End the day29 restrictions on day 60
        scen_policies.start(name, 60) # Start the scenario's restrictions on day 60

        relax_scenarios['Int'+str(n+1)] = {
            'name': scen_names[n],
            'pars': {
                'interventions': [
                    scen_policies,
                    cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                        'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [5] * 30))
                    }),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                ]
            }
        }

    # Same as baseline2 but increase importations for border reopening
    relax_scenarios['Int10'] = {
        'name': 'baseline2',
        'pars': {
            'interventions': [
                baseline_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),vals=np.append(i_cases, [10] * 30))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0), # CAUTION - the number of tests would probably go up as well as being targeted at people with a travel history...?
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }


    for run in relax_scenarios.keys():
        if 'runsim_indiv' in todo:
            scenarios = base_scenarios
            scenarios[run] = relax_scenarios[run]
            scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars = metapars, scenarios=scenarios)
            scens.run(verbose=verbose)
            del base_scenarios[run]

        if 'doplot_indiv' in todo:
            do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

            # Configure plotting
            fig_args = dict(figsize=(5, 8))
            this_fig_path = file_path + relax_scenarios[run]['name'] + '.png'
            to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
            to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
            to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
            to_plot_capacity = ['n_severe', 'n_critical']
            to_plot1 = ['new_infections','cum_infections','new_diagnoses','cum_deaths']

            scens.plot(do_save=do_save, do_show=False, fig_path=this_fig_path, interval=7, fig_args=fig_args, font_size=8, to_plot=to_plot1)

    for imports in [5, 10, 20, 50]:
        import_scenarios = {}
        import_scenarios['baseline2'] = {
            'name': 'baseline2',
            'pars': {
                'interventions': [
                    baseline_policies,
                    cv.dynamic_pars({
                        'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),vals=np.append(i_cases, [imports] * 30))
                    }),
                    cv.test_num(daily_tests=np.append(daily_tests, [10000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                ]
            }
        }

        import_scenarios['Int0'] = {
            'name': 'Fullrelax',
            'pars': {
                'interventions': [
                    relax_all_policies,
                    cv.dynamic_pars({
                        'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [imports] * 30))
                    }),
                    cv.test_num(daily_tests=np.append(daily_tests, [10000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                ]
            }
        }

        for n, name in enumerate(scen_names):
            scen_policies = sc.dcp(baseline_policies)
            scen_policies.end('day29', 60)  # End the day29 restrictions on day 60
            scen_policies.start(name, 60)  # Start the scenario's restrictions on day 60

            import_scenarios['Int'+str(n+1)] = {
                'name': 'name',
                'pars': {
                    'interventions': [
                        scen_policies,
                        cv.dynamic_pars({
                            'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)), vals=np.append(i_cases, [imports] * 30))
                        }),
                        cv.test_num(daily_tests=np.append(daily_tests, [10000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                    ]
                }
            }

        if 'runsim_import' in todo:
            scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=import_scenarios)
            scens.run(verbose=verbose)

        if 'doplot_import' in todo:
            do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

            # Configure plotting
            fig_args = dict(figsize=(8, 8))
            this_fig_path = file_path + str(imports) + 'imports.png'
            to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
            to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
            to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
            to_plot_capacity = ['n_severe', 'n_critical']
            to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

            scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=7, fig_args=fig_args, font_size=8, to_plot=to_plot1, as_dates=False)


