import covasim as cv
import pandas as pd
import contacts as co
import data
import parameters
import policy_updates
import sciris as sc
import utils
import functools
import numpy as np
import sys


def make_people(seed=None, pop_size=100e3, pop_infected=150, savepeople=True, popfile='nswppl.pop', savepopdict=False, popdictfile='nswpopdict.pop'):
    """
    Produce popdict and People
    """

    db_name = 'input_data_Australia'
    epi_name = 'epi_data_Australia' # Not sure why epi datafile needs to be passed in here, but difficult to remove this dependency

    all_lkeys = ['H', 'S', 'W', 'C', 'church', 'pSport', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events', 'social']
    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']

    sim_pars = {'pop_size': int(pop_size),
                'pop_infected': pop_infected,
                'pop_scale': 1,
                'rescale': 1} # Pass in a minimal set of sim pars

    # return data relevant to each specified location in "locations"
    loc_data = data.read_data(locations=['NSW'],
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys,
                              calibration_end={'NSW':'2020-07-13'})

    # setup parameters object for this simulation
    params = parameters.setup_params(location='NSW',
                                     loc_data=loc_data,
                                     sim_pars=sim_pars)


    utils.set_rand_seed({'seed': seed})
    params.pars['rand_seed'] = seed

    people, popdict = co.make_people(params)
    if savepeople: sc.saveobj(popfile, people)
    if savepopdict: sc.saveobj(popdictfile, popdict)
    return people, popdict


def make_sim(load_pop=True, popfile='nswppl.pop', datafile='nsw_epi_data.csv'):

    layers = ['H', 'S', 'W', 'C', 'church', 'pSport', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar', 'transport', 'public_parks', 'large_events', 'social']
    pars = {'pop_size': 100e3,
            'pop_infected': 150,
            'pop_scale': 1,
            'rescale': 0,
            'rand_seed': 1,
            'beta': 0.032, # Overall beta to use for calibration
                                    # H     S       W       C       church  psport  csport  ent     cafe    pub     trans   park    event   soc
            'contacts':    pd.Series([4,    21,     5,      1,      20,     40,     30,     25,     19,     30,     25,     10,     50,     6], index=layers).to_dict(),
            'beta_layer':  pd.Series([1,    0.25,   0.3,    0.1,    0.04,   0.2,    0.1,    0.01,   0.04,   0.06,   0.16,   0.03,   0.01,   0.1], index=layers).to_dict(),
            'iso_factor':  pd.Series([0.2,  0.20,   0.2,    0.2,    0.20,   0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.2], index=layers).to_dict(),
            'quar_factor': pd.Series([1,    0.01,   0.1,    0.2,    0.01,   0,      0,      0,      0,      0,      0.01,   0,      0,      0], index=layers).to_dict(),
            'n_imports': 2, # Number of new cases to import per day -- varied over time as part of the interventions
            'start_day': '2020-03-01',
            'end_day': '2020-07-13',
            'verbose': .1}

    sim = cv.Sim(pars=pars,
                 datafile=datafile,
                 popfile=popfile,
                 load_pop=load_pop)

    # Create beta policies
    # Important dates
    lockdown = '2020-03-23'
    reopen1  = '2020-05-01'
    reopen2  = '2020-05-15'
    reopen3  = '2020-06-01'
    reopen4  = '2020-07-01'
    school_dates = ['2020-05-11', '2020-05-18', '2020-05-25', '2020-06-01', '2020-06-08', '2020-06-15']

    beta_ints = [cv.change_beta('2020-03-15', 0.8, do_plot=False), # Reduce overall beta to account for distancing, handwashing, etc
                 cv.change_beta(days=[lockdown, reopen2, reopen4], changes=[1.2, 1.1, 1.05], layers=['H'], do_plot=True),
                 cv.change_beta(days=[lockdown]+school_dates, changes=[0.1, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], layers=['S'], do_plot=False),
                 cv.change_beta(days=[lockdown, school_dates[0], reopen3, reopen4], changes=[0.2, 0.3, 0.4, 0.5], layers=['W'], do_plot=False),
                 cv.change_beta(days=[lockdown], changes=[0.7], layers=['C'], do_plot=False), # Plot lockdown
                 cv.change_beta(days=[lockdown, reopen2], changes=[0, 0.7], layers=['church'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen2, reopen4], changes=[0, 0.5, 0.8], layers=['pSport'], do_plot=False),
                 cv.change_beta(days=[lockdown, '2020-06-22'], changes=[0, 0.5], layers=['cSport'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen4], changes=[0, 0.5], layers=['entertainment'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen2], changes=[0, 0.8], layers=['cafe_restaurant'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen3, reopen4], changes=[0, 0.3, 0.5], layers=['pub_bar'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen2, reopen4], changes=[0.2, 0.3, 0.5], layers=['transport'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen2, reopen4], changes=[0.4, 0.5, 0.7], layers=['public_parks'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen4], changes=[0.0, 0.5], layers=['large_events'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen1, reopen2, reopen3, reopen4], changes=[0.0, 0.3, 0.4, 0.5, 0.6], layers=['social'], do_plot=False),
                 ]

    sim.pars['interventions'].extend(beta_ints)

    # Testing
    symp_prob_prelockdown = 0.025 # Limited testing pre lockdown - 22%
    symp_prob_lockdown = 0.4 # Increased testing during lockdown - almost 100%!
    symp_prob_postlockdown = 0.5 # Much higher testing since lockdown - almost 100%!
    sim.pars['interventions'].append(cv.test_prob(start_day=0, end_day=lockdown, symp_prob=symp_prob_prelockdown, asymp_quar_prob=0.001))
    sim.pars['interventions'].append(cv.test_prob(start_day=lockdown, end_day=reopen1, symp_prob=symp_prob_lockdown, asymp_quar_prob=0.001))
    sim.pars['interventions'].append(cv.test_prob(start_day=reopen1, symp_prob=symp_prob_postlockdown, asymp_quar_prob=0.001))

    # Tracing
    trace_probs = {'H': 1, 'S': 0.95, 'W': 0.8, 'C': 0.05, 'church': 0.5, 'pSport': 0.8, 'cSport': 0.5,
                     'entertainment': 0.01, 'cafe_restaurant': 0.01, 'pub_bar': 0.01, 'transport': 0.01,
                     'public_parks': 0.01, 'large_events': 0.01, 'social': 0.9}
    trace_time = {'H': 0, 'S': 2, 'W': 2, 'C': 14, 'church': 5, 'pSport': 3, 'cSport': 3, 'entertainment': 14,
                    'cafe_restaurant': 14, 'pub_bar': 14, 'transport': 14, 'public_parks': 14, 'large_events': 14,
                    'social': 3}
    sim.pars['interventions'].append(cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0))

    # Close borders, then open them again in June to account for Victorian imports
    sim.pars['interventions'].append(cv.dynamic_pars({'n_imports': {'days': [14, 90], 'vals': [0, 1]}}))
    sim.initialize()

    return sim


def run_sim(load_pop=True, popfile='nswppl.pop', datafile='nsw_epi_data.csv'):
    """
    Run a single outbreak simulation
    """

    sim = make_sim(load_pop=load_pop, popfile=popfile, datafile=datafile)
    sim.run()
    return sim


T = sc.tic()
remakeppl=False
if remakeppl:
    people, popdict = make_people(seed=1, pop_size=100e3, pop_infected=150, savepeople=True, popfile='nswppl.pop', savepopdict=True, popdictfile='nswpopdict.pop')
sim = run_sim(load_pop=True, popfile='nswppl.pop')

# Plotting
to_plot = sc.objdict({
    'Diagnoses': ['cum_diagnoses'],
    'Deaths': ['cum_deaths'],
    'Total infections': ['cum_infections'],
    'New infections per day': ['new_infections'],
    })


sim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'nsw_calibration.png',
         legend_args={'loc': 'upper left'}, axis_args={'hspace':0.4}, interval=14)


sc.toc(T)