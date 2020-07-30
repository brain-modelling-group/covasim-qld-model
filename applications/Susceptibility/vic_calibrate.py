import outbreak
import contacts as co
import covasim as cv
import policy_updates
import utils
import sciris as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':

    start_day_relative_to_jul_9 = -40  # Start this many days beforehand
    n_days = 5*7-start_day_relative_to_jul_9 # Total simulation duration (days)
    n_imports = 0  # Number of daily imported cases
    seeded_cases = {2: 20}  # Seed cases {seed_day: number_seeded} e.g. {2:100} means infect 100 people on day 2
    beta = 0.04 # Overall beta
    extra_tests = 4000  # Add this many tests per day on top of the linear fit
    symp_test = 20  # People with symptoms are this many times more likely to be tested
    n_runs = 4  # Number of simulations to run

    use_stage3_lockdown = True # If True, apply Stage 3 policies on Jul 9
    use_masks = False # If True, start Masks policy on 22nd Jul. Note masks will only be used if the lockdown duration is at least 2 weeks (so it reaches Jul 22)
    lockdown_duration = 4*7  # Lockdown duration in days (after Jul 9)

    # Set up parameters
    params = outbreak.load_australian_parameters('Victoria', pop_size=2e5, pop_infected=0, n_days=n_days)
    params.pars["n_imports"] = n_imports # Number of imports per day
    params.pars['beta'] = beta

    params.extrapars['symp_test'] = symp_test

    params.pars['pop_scale'] = int(4.9e6 / params.pars['pop_size'])
    params.pars['rescale'] = True
    params.pars['rescale_threshold'] = 0.1

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
    # beta_schedule.start('lockdown_relax', 0) # Lockdown-relax currently has no effect
    beta_schedule.add('church_4sqm', start_day=0)
    beta_schedule.add('cafe_restaurant_4sqm', start_day=0)
    beta_schedule.add('pub_bar_4sqm', start_day=0)
    beta_schedule.add('outdoor200', start_day=0)
    beta_schedule.add('large_events', start_day=0)
    beta_schedule.add('entertainment', start_day=0)
    beta_schedule.add('NE_work', start_day=0)

    if use_stage3_lockdown:
        # Add these on 9th July
        jul9 = -start_day_relative_to_jul_9
        jul22 = jul9+(22-9)
        lift_day = lockdown_duration+jul9 # Lift lockdown on this day. The 2*7 is 2 weeks after Jul 9.

        # Replace these policies and add them back afterwards
        beta_schedule.end('cafe_restaurant_4sqm', jul9)
        beta_schedule.end('pub_bar_4sqm', jul9)
        beta_schedule.end('outdoor200', jul9)
        beta_schedule.add('cafe_restaurant0', start_day=jul9, end_day=lift_day)
        beta_schedule.add('pub_bar0', start_day=jul9, end_day=lift_day)
        beta_schedule.add('outdoor2', start_day=jul9, end_day=lift_day)
        beta_schedule.add('cSports', start_day=jul9, end_day=lift_day)
        beta_schedule.add('cafe_restaurant_4sqm', lift_day)
        beta_schedule.add('pub_bar_4sqm', lift_day)
        beta_schedule.add('outdoor200', lift_day)

        if use_masks and lift_day > jul22:
            beta_schedule.add('masks', start_day=jul22, end_day=lift_day)




    interventions.append(beta_schedule)

    # ADD CLIPPING POLICIES - Only NE_work policy is active
    # The other edge clipping policies e.g. schools, are not part of this lockdown and not really under consideration
    # (except maybe for a Stage 4 scenario?)
    interventions.append(cv.clip_edges(days=0, layers=params.policies['clip_policies']['NE_work']['layers'], changes=params.policies['clip_policies']['NE_work']['change']))

    # ADD TRACING INTERVENTION
    interventions.append(cv.contact_tracing(trace_probs=params.extrapars['trace_probs'],
                                            trace_time=params.extrapars['trace_time'],
                                            start_day=0))

    # nb. These probably don't do anything because the coverages are all tied to a different simulation start dates
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
    tests['day'] = (tests['Date']-pd.to_datetime('2020-07-09')).dt.days # Get day index relative to start day of 9th July
    tests.set_index('day',inplace=True)
    tests = tests.loc[tests.index>=start_day_relative_to_jul_9]['vic'].dropna().astype(int)
    tests = tests*(sim.n/4.9e6)  # Approximately scale to number of simulation agents - this might need to be changed!
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
    s = cv.MultiSim(sc.dcp(sim), n_runs=n_runs, keep_people=True, par_args={'ncpus':4})
    s.run()
    results = [x.results for x in s.sims]


    ####### ANALYZE RESULTS

    def plot_cum_diagnosed(ax):
        for result in results:
            ax.plot(result['t'], result['cum_diagnoses'], color='b', alpha=0.05)

        cases = pd.read_csv('new_cases.csv', parse_dates=['Date'])
        cases['day'] = (cases['Date'] - pd.to_datetime('2020-07-09')).dt.days  # Get day index relative to start day of 18th June
        cases.set_index('day', inplace=True)
        cases = cases.loc[cases.index >= start_day_relative_to_jul_9]['vic'].astype(int).cumsum()
        ax.scatter(cases.index - start_day_relative_to_jul_9, cases.values, s=5, color='k')
        after_lockdown = cases.index.values>0
        ax.scatter(cases.index.values[after_lockdown] - start_day_relative_to_jul_9, cases.values[after_lockdown], s=5, color='r')

        if use_stage3_lockdown:
            ax.axvspan(-start_day_relative_to_jul_9, lockdown_duration-start_day_relative_to_jul_9, alpha=0.05, color='red')

        if use_masks:
            ax.axvspan(jul22, lockdown_duration-start_day_relative_to_jul_9, alpha=0.05, color='red')


        ax.set_title('Cumulative diagnosed cases')

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
        n_window = (y > 50) & (y < 2000)
        coeffs = np.polyfit(x[n_window], np.log(y[n_window]), 1, w=np.sqrt(y[n_window]))
        ax.plot(np.exp(coeffs[1])*np.exp(coeffs[0]*x),'k--', linewidth=1)

        ax.text(0.05,0.9,f'Data exponent = {coeffs[0]:.4f}', transform=ax.transAxes)
        ax.text(0.05,0.80,f'Average model exponent = {np.mean(exponent):.4f}', transform=ax.transAxes)

    def plot_cum_infections(ax):
        for result in results:
            ax.plot(result['t'], result['cum_infections'], color='b', alpha=0.05)
        ax.set_title('Cumulative infections')
        ax.hlines(params.pars['pop_size'], 0, result['t'][-1])

    def plot_new_diagnoses(ax):
        for result in results:
            ax.plot(result['t'], result['new_diagnoses'], color='b', alpha=0.05)
        ax.set_title('New diagnoses')

        cases = pd.read_csv('new_cases.csv', parse_dates=['Date'])
        cases['day'] = (cases['Date'] - pd.to_datetime('2020-07-09')).dt.days  # Get day index relative to start day of 18th June
        cases.set_index('day', inplace=True)
        cases = cases.loc[cases.index >= start_day_relative_to_jul_9]['vic'].astype(int)
        ax.scatter(cases.index - start_day_relative_to_jul_9, cases.values, color='k')

        if use_stage3_lockdown:
            ax.axvspan(-start_day_relative_to_jul_9, lockdown_duration-start_day_relative_to_jul_9, alpha=0.05, color='red')

        if use_masks:
            ax.axvspan(jul22, lockdown_duration-start_day_relative_to_jul_9, alpha=0.05, color='red')


    def plot_daily_tests(ax):
        for result in results:
            ax.plot(result['t'], result['new_tests'], color='r', alpha=0.05)

        tests = pd.read_csv('new_tests.csv', parse_dates=['Date'])
        tests['day'] = (tests['Date'] - pd.to_datetime('2020-07-09')).dt.days  # Get day index relative to start day of 18th June
        tests.set_index('day', inplace=True)
        tests = tests.loc[tests.index >= start_day_relative_to_jul_9]['vic'].astype(float)
        tests = tests * (sim.n / 4.9e6)  # Approximately scale to number of simulation agents
        ax.scatter(tests.index - start_day_relative_to_jul_9, tests.values, color='k')
        ax.set_title('Daily tests')

    def plot_test_yield(ax):
        for result in results:
            ax.plot(result['t'], result['test_yield'], color='r', alpha=0.05)
        ax.set_title('Test yield*')

    def plot_active_infections(ax):
        for result in results:
            ax.plot(result['t'], result['n_infectious'], color='b', alpha=0.05)
        ax.set_title('Active infections')

    def plot_severe_infections(ax):
        for result in results:
            ax.plot(result['t'], result['n_severe'], color='b', alpha=0.05)
        ax.set_title('Severe infections')

        hosp = pd.read_csv('hospitalised.csv', parse_dates=['Date'])
        hosp['day'] = (hosp['Date'] - pd.to_datetime('2020-07-09')).dt.days  # Get day index relative to start day of 18th June
        hosp.set_index('day', inplace=True)

        hosp = hosp.loc[hosp.index >= start_day_relative_to_jul_9]['vic'].astype(int)
        ax.scatter(hosp.index - start_day_relative_to_jul_9, hosp.values, color='k')


    fig, ax = plt.subplots(2,3)
    fig.set_size_inches(20, 8)

    titlestr = f'{n_imports} imported cases per day, seeded {seeded_cases}'
    if use_stage3_lockdown:
        titlestr += f' - Stage 3 applied for {lockdown_duration} days'
    else:
        titlestr += f' - No Stage 3'

    if use_masks:
        titlestr += f' + masks'

    fig.suptitle(titlestr)

    plot_new_diagnoses(ax[0][0])
    plot_cum_diagnosed(ax[0][1])
    plot_cum_infections(ax[0][2])

    plot_daily_tests(ax[1][0])
    plot_active_infections(ax[1][1])
    plot_severe_infections(ax[1][2])


