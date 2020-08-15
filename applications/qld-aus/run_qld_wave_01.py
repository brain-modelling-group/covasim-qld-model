#!/usr/bin/env python
# coding: utf-8
"""
Replicate first coronavirus outbreak in Queensland Australia
=============================================================


# author: For QLD Paula Sanz-Leon, QIMRB, August 2020
#         based on NSW analysis originally written by Robyn Stuart, Optima, 2020
"""

# Import scientific python
import pandas as pd
import numpy as np

# Import IDM/Optima code
import covasim as cv
import sciris as sc


def make_sim(whattorun, julybetas=None, load_pop=True, popfile='qldppl.pop', datafile=None, agedatafile=None):

    layers = ['H', 'S', 'W', 'C', 
              'church', 
              'pSport', 
              'cSport', 
              'entertainment', 
              'cafe_restaurant', 
              'pub_bar', 
              'transport', 
              'public_parks', 
              'large_events', 
              'social']

    if whattorun == 'calibration':
        end_day = '2020-08-15'
    elif whattorun == 'scenarios':
        end_day = '2020-10-31'
        julybetas = julybetas

    pars = {'pop_size': 200e3,
            'pop_infected': 30,
            'pop_scale': 1,
            'rescale': False,
            'rand_seed': 42,
            'rel_death_prob': 0.6,
            'beta': 0.03, # Overall beta to use for calibration
                                    # H     S       W       C       church  psport  csport  ent     cafe    pub     trans   park    event   soc
            'contacts':    pd.Series([4.,    21,     5,      1,      20,     40,     30,     25,     19,     30,     25,     10,     50,     6], index=layers).to_dict(),
            'beta_layer':  pd.Series([1,    0.3,    0.2,    0.1,    0.04,   0.2,    0.1,    0.01,   0.04,   0.06,   0.16,   0.03,   0.01,   0.3], index=layers).to_dict(),
            'iso_factor':  pd.Series([0.2,  0,      0,      0.1,    0,      0,      0,      0,      0,      0,      0,      0,      0,      0], index=layers).to_dict(),
            'quar_factor': pd.Series([1,    0.1,    0.1,    0.2,    0.01,   0,      0,      0,      0,      0,      0.1 ,   0,      0,      0], index=layers).to_dict(),
            'n_imports': 0.02, # Number of new cases to import per day -- varied over time as part of the interventions
            'start_day': '2020-03-01',
            'end_day': end_day,
            'analyzers': cv.age_histogram(datafile=agedatafile, edges=np.linspace(0, 75, 16), days=[8, 54]), # These days correspond to dates 9 March and 24 April, which is the date window in which qld has published age-disaggregated case counts
            'verbose': .1}

    sim = cv.Sim(pars=pars,
                 datafile=datafile,
                 popfile=popfile,
                 load_pop=load_pop)

    # Create beta policies
    # Important dates -- lockdown start dates
    response00 = '2020-03-15' # Physical distancing, handwashing -- ongoing
    response01 = '2020-03-19' # Outdoors restricted to < 200 ppl
    response02 = '2020-03-21' # Enahnced screening and distancing within age care facilities
    lockdown00 = '2020-03-23' # Lockdown starts, churches close, restaurants/pubs close
                              # cSports cancelled, entratianment, large-events, pSports
    lockdown01 = '2020-03-25' # noncovid health services close - C-layer
    lockdown02 = '2020-03-26' # retail close - C layer
    parks00   = '2020-04-03' # National parks close - public parks
    borders00 = '2020-04-03'  # Borders shut to all state
    beach00   = '2020-04-07'  # Beaches closes
    
    # relaxation dates 
    outdoors00 = '2020-03-30'   # Outdoors ok < 2 ppl
    beach01    = '2020-04-20'   # Beaches ok <2 ppl
    parks01    = '2020-05-01'   # national parks open
    church00   = '2020-05-16'   # Church 4sqm rule, 
    outdoors01 = '2020-05-16'   # outdoor ok <10 ppl
    beach02    = '2020-05-16'   # Beaches ok <10 ppl
    # reopening dates
    reopen01  = '2020-06-01' # reopen cSports, cinemas, social, beach, psport, shopping 
    reopen02  = '2020-06-15' # noncovid health services open
    reopen03  = '2020-07-03' # large events open
    borders01 = '2020-07-10' # regional travel open,
    schools   = ['2020-03-30', '2020-05-25']
    # shut borders again
    borders02 ='2020-08-05'  # effective border closure NSW, VIC, ACT

    beta_ints = [cv.clip_edges(days=[response00, response01]+schools, 
                               changes=[0.75, 0.7, 0.05, 0.9], 
                               layers=['S'], do_plot=False),
                 
                 cv.clip_edges(days=[response00, response01, lockdown00, lockdown01, lockdown02, reopen01], 
                               changes=[0.9, 0.7, 0.4, 0.3, 0.2, 0.5], 
                               layers=['W'], do_plot=False),
                 
                 cv.clip_edges(days=[lockdown00, reopen01], 
                               changes=[0.0, 0.5], 
                               layers=['pSport'], do_plot=False),
                 
                 cv.clip_edges(days=[lockdown00, reopen01],
                               changes=[0.0, 0.8], 
                               layers=['cSport'], do_plot=False),

                 # Reduce overall beta to account for distancing, handwashing, etc
                 cv.change_beta([reopen01], [0.7], do_plot=False), 
                 
                 cv.change_beta(days=[lockdown00, reopen01, reopen02], 
                                changes=[1.2, 1.1, 1.], 
                                layers=['H'], do_plot=True),
                 
                 cv.change_beta(days=[lockdown00, church00], 
                                changes=[0.0, 0.6], 
                                layers=['church'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen01, reopen02, reopen03], 
                                changes=[0.0, 0.3, 0.4, 0.5], 
                                layers=['social'], do_plot=False),
                 # Dynamic layers ['C', 'entertainment', 'cafe_restaurant', 
                 # 'pub_bar', 'transport', 'public_parks', 'large_events']
                 
                 cv.change_beta(days=[response01, lockdown01, lockdown02, reopen01, reopen02, borders02], 
                                changes=[0.7, 0.67, 0.6, 0.7, 0.8, 0.6], 
                                layers=['C'], do_plot=True),
                 
                 cv.change_beta(days=[lockdown00, reopen01], 
                                changes=[0.0, 0.8], 
                                layers=['entertainment'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen01], 
                                changes=[0.0, 0.5], 
                                layers=['cafe_restaurant'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen01], 
                                changes=[0.0, 0.5], 
                                layers=['pub_bar'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, borders00, borders01, borders02], 
                                changes=[0.7, 0.4, 0.5, 0.2], 
                                layers=['transport'], do_plot=False),
                 
                 cv.change_beta(days=[outdoors00, parks00, parks01], 
                                changes=[0.4, 0.1, 0.5], 
                                layers=['public_parks'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen03], 
                                changes=[0.0, 0.6], 
                                layers=['large_events'], do_plot=False),
                 ]

    if whattorun == 'scenarios':
        # Approximate a mask intervention by changing beta in all layers where people would wear masks - assuming not in schools, sport, social gatherings, or home
        beta_ints += [cv.change_beta(days=['2020-08-21']*10, changes=[julybetas]*10,
                                     layers=['W', 
                                             'C', 
                                             'church',
                                             'entertainment',
                                             'cafe_restaurant',
                                             'pub_bar',
                                             'transport',
                                             'public_parks',
                                             'large_events'])
                     ]

    sim.pars['interventions'].extend(beta_ints)

    # Testing
    symp_prob_prelockdown = 0.05   # Limited testing pre lockdown
    symp_prob_lockdown = 0.3       # Increased testing during lockdown
    symp_prob_postlockdown = 0.5   # Testing since lockdown
    sim.pars['interventions'].append(cv.test_prob(start_day=0, 
                                                  end_day=lockdown00, 
                                                  symp_prob=symp_prob_prelockdown, 
                                                  asymp_quar_prob=0.001, do_plot=False))
    sim.pars['interventions'].append(cv.test_prob(start_day=lockdown00, 
                                                  end_day=reopen01, 
                                                  symp_prob=symp_prob_lockdown, 
                                                  asymp_quar_prob=0.001,do_plot=False))
    sim.pars['interventions'].append(cv.test_prob(start_day=reopen01, 
                                                  symp_prob=symp_prob_postlockdown, 
                                                  asymp_quar_prob=0.001,do_plot=True))

    # Tracing
    trace_probs = {'H': 1, 'S': 0.95, 
                   'W': 0.9, 'C': 0.05, 
                   'church': 0.5, 
                   'pSport': 0.8, 
                   'cSport': 0.5,
                   'entertainment': 0.1, 
                   'cafe_restaurant': 0.8, 
                   'pub_bar': 0.8, 
                   'transport': 0.8, 
                   'public_parks': 0.01, 
                   'large_events': 0.01, 
                   'social': 0.9}
    trace_time = {'H': 0, 'S': 2, 
                  'W': 2, 'C': 7, 
                  'church': 5, 
                  'pSport': 3, 
                  'cSport': 3, 
                  'entertainment': 7,
                  'cafe_restaurant': 4, 
                  'pub_bar': 4, 
                  'transport': 2, 
                  'public_parks': 14, 
                  'large_events': 14,
                  'social': 3}
    sim.pars['interventions'].append(cv.contact_tracing(trace_probs=trace_probs, 
                                                        trace_time=trace_time, 
                                                        start_day=0, do_plot=False))

    # Close borders, then open them again to account for Victorian imports and leaky quarantine
    sim.pars['interventions'].append(cv.dynamic_pars({'n_imports': {'days': [14, 150, 164], 'vals': [10, 2, 2]}}, do_plot=False))
    sim.initialize()

    return sim

# Start setting up to run
# NB, this file assumes that you've already generated a population file saved in the same folder as this script, called qldpop.pop

if __name__ == '__main__':
    
    T = sc.tic()
    # Settings
    whattorun = ['calibration', 'scenarios'][1]
    domulti = True
    doplot = False
    dosave = True
    number_of_runs = 10

    # Filepaths
    inputsfolder = 'inputs'
    resultsfolder = 'results'
    datafile = f'{inputsfolder}/qld_epi_data_wave_01_basic_stats.csv'
    agedatafile = f'{inputsfolder}/qld_epi_data_wave_01_age_cumulative.csv'

    # Plot settings
    to_plot = sc.objdict({
        'Cumulative diagnoses': ['cum_diagnoses'],
        'Cumulative deaths': ['cum_deaths'],
        'Cumulative infections': ['cum_infections'],
        'New infections': ['new_infections'],
        'Daily diagnoses': ['new_diagnoses'],
        'Active infections': ['n_exposed']
        })

    # Run and plot
    if domulti:
        if whattorun == 'calibration':
            sim  = make_sim(whattorun, load_pop=True, 
                            popfile='qldppl.pop', 
                            datafile=datafile, 
                            agedatafile=agedatafile)
            msim = cv.MultiSim(base_sim=sim)
            msim.run(n_runs=number_of_runs, reseed=True, noise=0)
            if dosave: 
              msim.save(f'{resultsfolder}/qld_{whattorun}.obj')
            if doplot:
                msim.plot(to_plot=to_plot, do_save=True, do_show=False, 
                          fig_path=f'qld_{whattorun}.png',
                          legend_args={'loc': 'upper left'}, 
                          axis_args={'hspace': 0.4}, 
                          interval=21)
        elif whattorun == 'scenarios':
            julybetas = [0.05, 0.1, 0.15]
            for jb in julybetas:
                sim = make_sim(whattorun, julybetas=jb, load_pop=True, popfile='qldppl.pop', datafile=datafile, agedatafile=agedatafile)
                msim = cv.MultiSim(base_sim=sim)
                msim.run(n_runs=number_of_runs, reseed=True, noise=0)
                if dosave: 
                  msim.save(f'{resultsfolder}/qld_{whattorun}_{int(jb*100)}.obj')
                if doplot:
                    msim.plot(to_plot=to_plot, do_save=True, do_show=False, 
                              fig_path=f'qld_{whattorun}_{int(jb*100)}.png',
                              legend_args={'loc': 'upper left'}, 
                              axis_args={'hspace': 0.4}, 
                              interval=21)
    else:
        sim = make_sim(whattorun, load_pop=True, popfile='qldppl.pop', datafile=datafile, agedatafile=agedatafile)
        sim.run()
        if dosave: sim.save(f'{resultsfolder}/qld_{whattorun}.obj')
        if doplot:
            sim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'qld_{whattorun}.png',
                     legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4}, interval=21)


    sc.toc(T)