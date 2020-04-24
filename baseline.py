
import matplotlib
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
import load_pop
import numpy as np
import load_parameters

if __name__ == '__main__': # need this to run in parallel on windows

    # What to do
    todo = ['loaddata',
            'runsim',
            'doplot',
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

    sim = cv.Sim(pars, popfile=popfile, load_pop=True, datafile=data_path, pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=popfile)

    # Cumulative impact of four policy changes on the beta_layers for H, S, W, C, Church, pSports
    beta_eff = np.array(((1.02,    1,      1,      0.98,        1,      1), # day 15: international travellers self isolate, public events >500 people cancelled
                         (1.05,    0.75,    1,    0.9,      0.0,      1), # day 19: indoor gatherings limited to 100 people
                         (1.06,    0.5,    0.88,    0.82,      0.0,    0.0), # day 22: pubs/bars/cafes take away only, church/sport etc. cancelled
                         (1.13,    0.25,    0.67,   0.55,     0.0,    0.0), # day 29: public gatherings limited to 2 people
                         (1,1,1,1,1,1))) # go back to pre-lockdown
    beta_eff2 = np.array(((1.02,    0,      0,      0.0,        1,      1), # day 15: international travellers self isolate, public events >500 people cancelled
                         (1.05,    0.75,    0,    0.0,      0.0,      1), # day 19: indoor gatherings limited to 100 people
                         (1.06,    0.5,    0.0,    0.0,      0.0,    0.0), # day 22: pubs/bars/cafes take away only, church/sport etc. cancelled
                         (1.13,    0.25,    0.0,   0.0,     0.0,    0.0), # day 29: public gatherings limited to 2 people
                         (1,1,1,1,1,1))) # go back to pre-lockdown

    beta_layer_tester = pars['beta_layer'] #{'H': 1.7, 'S': 0.8, 'W': 0.5, 'C': 0.1, 'Church': 0.5, 'pSport': 1.0} #{'H': 0.0, 'S': 0.0, 'W': 0.00, 'C': 0.05, 'Church': 0.00, 'pSport': 0.00} # using this to test while calibrating
    scenarios = {#'counterfactual': {'name': 'counterfactual', 'pars': {'interventions': None}}, # no interentions
                 'baseline': {'name': 'baseline', 'pars': {'interventions': [cv.dynamic_pars({ #this is what we actually did
                        'beta_layer': dict(days=[15, 19, 22, 29], # multiply the beta_layers by the beta_eff
                                            vals=[{'H': beta_eff[0,0]*pars['beta_layer']['H'], 'S': beta_eff[0,1]*pars['beta_layer']['S'], 'W': beta_eff[0,2]*pars['beta_layer']['W'], 'C': beta_eff[0,3]*pars['beta_layer']['C'],'Church': beta_eff[0,4]*pars['beta_layer']['Church'], 'pSport': beta_eff[0,5]*pars['beta_layer']['pSport']},
                                                  {'H': beta_eff[1,0]*pars['beta_layer']['H'], 'S': beta_eff[1,1]*pars['beta_layer']['S'], 'W': beta_eff[1,2]*pars['beta_layer']['W'], 'C': beta_eff[1,3]*pars['beta_layer']['C'],'Church': beta_eff[1,4]*pars['beta_layer']['Church'], 'pSport': beta_eff[1,5]*pars['beta_layer']['pSport']},
                                                  {'H': beta_eff[2,0]*pars['beta_layer']['H'], 'S': beta_eff[2,1]*pars['beta_layer']['S'], 'W': beta_eff[2,2]*pars['beta_layer']['W'], 'C': beta_eff[2,3]*pars['beta_layer']['C'],'Church': beta_eff[2,4]*pars['beta_layer']['Church'], 'pSport': beta_eff[2,5]*pars['beta_layer']['pSport']},
                                                  {'H': beta_eff[3,0]*pars['beta_layer']['H'], 'S': beta_eff[3,1]*pars['beta_layer']['S'], 'W': beta_eff[3,2]*pars['beta_layer']['W'], 'C': beta_eff[3,3]*pars['beta_layer']['C'],'Church': beta_eff[3,4]*pars['beta_layer']['Church'], 'pSport': beta_eff[3,5]*pars['beta_layer']['pSport']},
                                                 ]), # at different time points the FOI can change
                        'n_imports': dict(days=range(len(i_cases)), vals=i_cases)
                            }),
                        cv.test_num(daily_tests=np.append(daily_tests, [1000]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                            },
                 'baseline2': {'name': 'baseline2', 'pars': {'interventions': [cv.dynamic_pars({ # same as baseline but re-introduce imported infections to test robustness
                        'beta': dict(days=[15], vals=0.035),
                        'beta_layer': dict(days=[1, 15, 19, 22, 29], # multiply the beta_layers by the beta_eff
                                            vals=[beta_layer_tester,
                                                  {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                                  {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                                  {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                                  {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                                 ]), # at different time points the FOI can change
                        'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                          vals=np.append(i_cases,[5]*30))}),
                        cv.test_num(daily_tests=np.append(daily_tests, [0]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                            },
                 'Int1': {'name': 'Int1', 'pars': {'interventions': [cv.dynamic_pars({ # same as baseline 2 but with all restrictions lifted
                        'beta': dict(days=[1], vals=0.035),
                        'beta_layer': dict(days=[1, 15, 19, 22, 29, 60], # multiply the beta_layers by the beta_eff
                                            vals=[beta_layer_tester,
                                                  {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                                  {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                                  {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                                  {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                                  {'H': beta_eff2[4,0]*beta_layer_tester['H'], 'S': beta_eff2[4,1]*beta_layer_tester['S'], 'W': beta_eff2[4,2]*beta_layer_tester['W'], 'C': beta_eff2[4,3]*beta_layer_tester['C'],'Church': beta_eff2[4,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[4,5]*beta_layer_tester['pSport']}
                                                 ]), # at different time points the FOI can change
                        'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                          vals=np.append(i_cases,[5]*30))}),
                        cv.test_num(daily_tests=np.append(daily_tests, [0]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                            }
                 }


    if 'runsim' in todo:
        scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars = metapars, scenarios=scenarios)
        scens.run(verbose=verbose)

    if 'doplot' in todo:
        do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

        # Configure plotting
        fig_args = dict(figsize=(5, 8))
        this_fig_path = file_path + '.png'
        to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
        to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
        to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
        to_plot_capacity = ['n_severe', 'n_critical']
        to_plot1 = ['new_infections','cum_infections','new_diagnoses','cum_deaths']


        fig1 = scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=7, fig_args=fig_args, font_size=8, to_plot=to_plot1)



