import user_interface as ui
from utils import policy_plot2
import os
import outbreak
import contacts as co
import covasim as cv
import policy_updates
import utils
import sciris as sc
import pandas as pd
import numpy as np

if __name__ == '__main__':

    start_day_relative_to_jul_9 = -40 # Start this many days beforehand
    n_days = 12-start_day_relative_to_jul_9
    n_imports = 0  # Number of daily imported cases
    seeded_cases = {2: 100}  # Seed cases {seed_day: number_seeded} e.g. {2:100} means infect 100 people on day 2
    beta = 0.03 # Overall beta
    extra_tests = 0  # Add this many tests per day on top of the linear fit
    symp_test = 5  # People with symptoms are this many times more likely to be tested
    n_runs = 10 # Number of simulations to run


    # Set up parameters
    params = outbreak.load_australian_parameters('Victoria', pop_size=5e4, pop_infected=0, n_days=n_days)
    params.pars["n_imports"] = n_imports # Number of imports per day
    params.pars['beta'] = beta

    params.extrapars['symp_test'] = symp_test

    # Make people
    cv.set_seed(1) # Seed for population generation
    people, popdict = co.make_people(params)

    # Make the base sim
    sim = cv.Sim(pars=params.pars,
                 datafile=None,
                 popfile=people,
                 pop_size=params.pars['pop_size'],
                 load_pop=True,
                 save_pop=False
                 )

    # Assemble interventions
    interventions = []

    # ADD DYNAMIC LAYERS INTERVENTION
    interventions.append(policy_updates.UpdateNetworks(layers=params.dynamic_lkeys, contact_numbers=params.pars['contacts'], popdict=popdict))

    # SET BETA POLICIES
    beta_schedule = policy_updates.PolicySchedule(params.pars["beta_layer"], params.policies['beta_policies'])
    # Policies before 9th July
    # beta_schedule.start('lockdown_relax', 0) # Lockdown-relax currently has no
    beta_schedule.start('church_4sqm', 0)
    beta_schedule.start('cafe_restaurant_4sqm', 0)
    beta_schedule.start('pub_bar_4sqm', 0)
    beta_schedule.start('outdoor200', 0)
    beta_schedule.start('large_events', 0)

    # Add these on 9th July
    # beta_schedule.start('cSports', -start_day_relative_to_jul_9)
    # beta_schedule.start('entertainment', -start_day_relative_to_jul_9)

    # Replace these on 9th July
    # For calibration, we can avoid turning these on if we also avoid running the simulation for
    # more than ~7 days after 9th July
    # beta_schedule.end('cafe_restaurant_4sqm', -start_day_relative_to_jul_9)
    # beta_schedule.start('cafe_restaurant0', -start_day_relative_to_jul_9)
    # beta_schedule.end('pub_bar_4sqm', -start_day_relative_to_jul_9)
    # beta_schedule.start('pub_bar0', -start_day_relative_to_jul_9)
    # beta_schedule.end('outdoor200', -start_day_relative_to_jul_9)
    # beta_schedule.start('outdoor2', -start_day_relative_to_jul_9)

    interventions.append(beta_schedule)

    # ADD CLIPPING POLICIES - Only NE_work is active
    interventions.append(cv.clip_edges(days=0, layers=params.policies['clip_policies']['NE_work']['layers'], changes=params.policies['clip_policies']['NE_work']['change']))

    # ADD TRACING INTERVENTION
    interventions.append(cv.contact_tracing(trace_probs=params.extrapars['trace_probs'],
                                            trace_time=params.extrapars['trace_time'],
                                            start_day=0))
    tracing_app, id_checks = policy_updates.make_tracing(trace_policies=params.policies["tracing_policies"])
    if tracing_app is not None:
        interventions.append(tracing_app)
    if id_checks is not None:
        interventions.append(id_checks)

    sim.pars['interventions'] = interventions

    # Now when we run the model, the major free parameters are the overall beta
    # And the date of the seed infection
    sim.pars['verbose'] = 0
    sim.pars['rand_seed'] = 1

    sim.pars['interventions'].append(utils.SeedInfection(seeded_cases))

    # Add probability-based testing interventions
    # sim.pars['interventions'].append(cv.test_prob(
    #     symp_prob=0.1,
    #     asymp_prob=0.01,
    #     symp_quar_prob=0.2,
    #     asymp_quar_prob=0.01,
    #     start_day=0,
    #     end_day=20,
    # ))
    # sim.pars['interventions'].append(cv.test_prob(
    #     symp_prob=0.1,
    #     asymp_prob=0.01,
    #     symp_quar_prob=0.2,
    #     asymp_quar_prob=0.01,
    #     start_day=21,
    # ))


    # Add number-based testing interventions
    tests = pd.read_csv('new_tests.csv',parse_dates=['Date'])
    tests['day'] = (tests['Date']-pd.to_datetime('2020-07-09')).dt.days # Get day index relative to start day of 18th June
    tests.set_index('day',inplace=True)
    tests = tests.loc[tests.index>=start_day_relative_to_jul_9]['vic'].replace('-', None, regex=True).astype(int)
    tests = tests*sim.n/4.9e6  # Approximately scale to number of simulation agents - this might need to be changed!
    coeffs = np.polyfit(tests.index-start_day_relative_to_jul_9, tests.values, 1)
    tests_per_day = np.arange(params.pars["n_days"]+1)*coeffs[0]+coeffs[1]

    sim.pars['interventions'].append(cv.test_num(daily_tests=extra_tests+tests_per_day,
                                                 symp_test=params.extrapars['symp_test'],
                                                 quar_test=params.extrapars['quar_test'],
                                                 sensitivity=params.extrapars['sensitivity'],
                                                 test_delay=params.extrapars['test_delay'],
                                                 loss_prob=params.extrapars['loss_prob'])
                                     )


    # Run using Celery
    # def analyzer(s):
    #     return s.results
    # from outbreak.celery import run_multi_sim
    # results = run_multi_sim(sim,n_runs, analyzer=analyzer, celery=True)

    # Run using MultiSim
    s = cv.MultiSim(sc.dcp(sim), n_runs=n_runs, keep_people=True)
    s.run()
    results = [x.results for x in s.sims]


    ####### ANALYZE RESULTS

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2,2)
    fig.set_size_inches(10, 7)

    fig.suptitle(f'{n_imports} imported cases per day, seeded {seeded_cases}')

    # DIAGNOSES
    for result in results:
        ax[0][0].plot(result['t'], result['cum_diagnoses'], color='b', alpha=0.05)

    cases = pd.read_csv('new_cases.csv',parse_dates=['Date'])
    cases['day'] = (cases['Date']-pd.to_datetime('2020-07-09')).dt.days # Get day index relative to start day of 18th June
    cases.set_index('day',inplace=True)
    cases = cases.loc[cases.index>=start_day_relative_to_jul_9]['vic'].astype(int).cumsum()
    ax[0][0].scatter(cases.index-start_day_relative_to_jul_9,cases.values,color='k')
    ax[0][0].set_title('Cumulative diagnosed cases')

    # INFECTIONS
    for result in results:
        ax[0][1].plot(result['t'], result['cum_infections'], color='b', alpha=0.05)
    ax[0][1].set_title('Cumulative infections')
    ax[0][1].hlines(params.pars['pop_size'],0,result['t'][-1])

    # TESTS
    for result in results:
        ax[1][0].plot(result['t'], result['new_tests'], color='r', alpha=0.05)

    tests = pd.read_csv('new_tests.csv',parse_dates=['Date'])
    tests['day'] = (tests['Date']-pd.to_datetime('2020-07-09')).dt.days # Get day index relative to start day of 18th June
    tests.set_index('day',inplace=True)
    tests = tests.loc[tests.index>=start_day_relative_to_jul_9]['vic'].replace('-', None, regex=True).astype(int)
    tests = tests*sim.n/4.9e6  # Approximately scale to number of simulation agents
    ax[1][0].scatter(tests.index-start_day_relative_to_jul_9,tests.values,color='k')
    ax[1][0].set_title('Daily tests')

    for result in results:
        ax[1][1].plot(result['t'], result['test_yield'], color='r', alpha=0.05)
    ax[1][1].set_title('Test yield*')

    import numpy as np

    # ### Fit an exponential
    exponent = []
    for res in results:
        diagnoses = res['cum_diagnoses'].values
        n_window = (diagnoses>50) & (diagnoses < 2000)
        if sum(n_window)>4:
            # Need enough data points to be able to produce a reasonable curve fit
            x = res['t'][n_window]
            y = diagnoses[n_window]
            coeffs = np.polyfit(x, np.log(y), 1, w=np.sqrt(y))
            exponent.append(coeffs[0])
        else:
            exponent.append(0) # Because it never reached 50 diagnoses

    # Fit exponential to data
    x = cases.index-start_day_relative_to_jul_9
    y = cases.values
    coeffs = np.polyfit(x, np.log(y), 1, w=np.sqrt(y))
    # plt.figure()
    # plt.scatter(x,y,color='k')
    # plt.plot(np.exp(coeffs[1])*np.exp(coeffs[0]*x))
    # plt.title('Cumulative diagnosed cases')

    ax[0][0].text(0.05,0.9,f'Data exponent = {coeffs[0]:.4f}', transform=ax[0][0].transAxes)
    ax[0][0].text(0.05,0.80,f'Average model exponent = {np.mean(exponent):.4f}', transform=ax[0][0].transAxes)


    # Linear fit to testing rate
    # x = tests.index-start_day_relative_to_jul_9
    # y = tests.values
    # coeffs = np.polyfit(x, y, 1)
    # plt.figure()
    # plt.scatter(x,y,color='k')
    # plt.plot(coeffs[1]+coeffs[0]*x)
    # plt.title('Daily tests')

