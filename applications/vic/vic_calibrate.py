# Main script to run Victoria calibration

import contacts as co
import covasim as cv
import policy_updates
import utils
import sciris as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import parameters
import data
import matplotlib.ticker as ticker

# Overall strategy
# 1. Set key parameters for simulation and calibration
# 2. Load data and construct a Sim object
# 3. Add interventions to the Sim
# 4. Run the Sim, optionally with multiple seeds
# 5. Make plots


if __name__ == '__main__':

    # 1 - KEY PARAMETERS
    start_day = '2020-06-01'
    n_days = 100 # Total simulation duration (days)
    n_imports = 5  # Number of daily imported cases. This would influence the early growth rate of the outbreak. Ideally would set to 0 and use seeded infections only?
    seeded_cases = {3:0}  # Seed cases {seed_day: number_seeded} e.g. {2:100} means infect 100 people on day 2. Could be used to kick off an outbreak at a particular time
    beta = 0.038 # Overall beta
    extra_tests = 100  # Add this many tests per day on top of the linear fit. Alternatively, modify test intervention directly further down
    symp_test = 100  # People with symptoms are this many times more likely to be tested
    n_runs = 8  # Number of simulations to run
    pop_size = 1e5  # Number of agents
    tracing_capacity = 200  # People per day that can be traced. Household contacts are always all immediately notified
    location = 'Victoria' # Location to use when reading input spreadsheets
    scale_tests = 8 # Multiplicative factor for scaling tests by population proportion


    # 2 - LOAD DATA AND CREATE SIM
    db_name = 'input_data_Australia2'  # the name of the databook
    epi_name = 'epi_data_Australia'

    all_lkeys = ['H', 'S', 'W', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events', 'child_care', 'social','aged_care']
    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']

    user_pars = {location: {'pop_size': int(pop_size),
                            'pop_infected': 0, # Start with zero infections
                            'pop_scale': 1,
                            'rescale': 1,
                            'beta': beta,
                            'n_days': n_days,
                            'calibration_end': None,
                            'verbose': 0}}

    metapars = {'noise': 0.0,
                'verbose': 0}

    user_pars, calibration_end = utils.clean_pars(user_pars, [location])

    # return data relevant to each specified location in "locations"
    all_data = data.read_data(locations=[location],
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys,
                              calibration_end=calibration_end)

    loc_data = all_data
    loc_pars = user_pars[location]

    # setup parameters object for this simulation
    params = parameters.setup_params(location=location,
                                     loc_data=loc_data,
                                     metapars=metapars,
                                     sim_pars=loc_pars)

    params.pars["n_imports"] = n_imports # Number of imports per day
    params.pars['beta'] = beta
    params.pars['start_day'] = start_day
    params.pars['verbose'] = 0
    params.pars['rand_seed'] = 1

    params.extrapars['symp_test'] = symp_test

    # Uncomment section below to use population scaling
    params.pars['pop_scale'] = int(4.9e6 / params.pars['pop_size'])
    params.pars['rescale'] = True
    params.pars['rescale_threshold'] = 0.05

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

    # 3 - ASSEMBLE INTERVENTIONS

    interventions = []

    # Add dynamic layers intervention
    interventions.append(policy_updates.UpdateNetworks(layers=params.dynamic_lkeys,
                                                       contact_numbers=params.pars['contacts'],
                                                       popdict=popdict,
                                                       dispersion=params.layerchars['dispersion']
                                                       ))

    # Set beta policies
    beta_schedule = policy_updates.PolicySchedule(params.pars["beta_layer"], params.policies['beta_policies'])

    # Policies before Stage 3
    beta_schedule.add('church_4sqm', start_day=0)
    beta_schedule.add('cafe_restaurant_4sqm', start_day=0)
    beta_schedule.add('pub_bar_4sqm', start_day=0)
    beta_schedule.add('outdoor200', start_day=0)
    beta_schedule.add('large_events', start_day=0)
    beta_schedule.add('entertainment', start_day=0)
    beta_schedule.add('NE_work', start_day=0)

    # Stage 3 from 9th July
    jul2 = sim.day('20200702')
    jul9 = sim.day('20200709')
    jul23 = sim.day('20200723')
    aug6 = sim.day('20200806')

    beta_schedule.end('cafe_restaurant_4sqm', jul2)
    beta_schedule.end('pub_bar_4sqm', jul2)
    beta_schedule.end('outdoor200', jul2)
    #beta_schedule.add('cafe_restaurant0', jul2)
    #beta_schedule.add('pub_bar0', jul2)
    #beta_schedule.add('church0', jul2)
    #beta_schedule.add('outdoor2', jul2)
    #beta_schedule.add('cSports', jul2)

    beta_schedule.add('masks', jul23)

    beta_schedule.add('stage4', aug6)

    interventions.append(beta_schedule)

    # Add clipping policies

    # NE work, switch to stage 4 on aug6
    interventions.append(cv.clip_edges(days=[0,aug6], changes=[0.8,0.2], layers='W'))

    # Social layer, clipped by stages 3 and 4
    #interventions.append(cv.clip_edges(days=[jul2,aug6], changes=[0.5,0.2], layers='social'))

    # Other layers clipped by stage 3 on jul9
    #interventions.append(cv.clip_edges(days=[jul2], changes=[0.5], layers=['church', 'pub_bar', 'cafe_restaurant', 'cSports', 'S']))


    # Add tracing intervention for households
    interventions.append(utils.limited_contact_tracing(trace_probs={'H': 1},
                                                       trace_time={'H': 0},
                                                       start_day=0,
                                                       capacity=np.inf,
                                                       ))

    # Add tracing intervention for other layers
    # Remove the household layer from trace_probs because they will be traced separately
    del params.extrapars['trace_probs']['H']
    del params.extrapars['trace_time']['H']
    interventions.append(utils.limited_contact_tracing(trace_probs=params.extrapars['trace_probs'],
                                                       trace_time=params.extrapars['trace_time'],
                                                       start_day=0,
                                                       capacity=tracing_capacity,
                                                       dynamic_layers=params.dynamic_lkeys,
                                                       ))

    # Add COVIDSafe app based tracing
    interventions.append(policy_updates.AppBasedTracing(name='tracing_app',**params.policies["tracing_policies"]["tracing_app"]))


    # Now when we run the model, the major free parameters are the overall beta
    # And the date of the seed infection

    interventions.append(utils.SeedInfection(seeded_cases))

    # Add probability-based testing interventions
    '''
    interventions.append(cv.test_prob(
        symp_prob=0.1,
        asymp_prob=0.01,
        symp_quar_prob=0.2,
        asymp_quar_prob=0.01,
        start_day=0,
        end_day=20,
    ))
    interventions.append(cv.test_prob(
        symp_prob=0.1,
        asymp_prob=0.01,
        symp_quar_prob=0.2,
        asymp_quar_prob=0.01,
        start_day=21,
    ))
    '''


    # Add number-based testing interventions
    tests = pd.read_csv('new_tests.csv')
    tests['day'] = tests['Date'].map(sim.day)
    tests.set_index('day',inplace=True)
    tests = tests.loc[tests.index >= 0]['vic'].dropna().astype(int)
    tests = tests*scale_tests*(sim.n/4.9e6)  # Approximately scale to number of simulation agents - this might need to be changed!
    coeffs = np.polyfit(tests.index, tests.values, 1)
    tests_per_day = np.arange(params.pars["n_days"]+1)*coeffs[0]+coeffs[1]
    #tests_per_day = tests.values

    interventions.append(cv.test_num(daily_tests=extra_tests+tests_per_day,
                                                 symp_test=params.extrapars['symp_test'],
                                                 quar_test=params.extrapars['quar_test'],
                                                 sensitivity=params.extrapars['sensitivity'],
                                                 test_delay=params.extrapars['test_delay'],
                                                 loss_prob=params.extrapars['loss_prob'])
                                     )

    sim.pars['interventions'] = interventions # Add the interventions to the scenario

    # Run using Celery
    # def analyzer(s):
    #     return s.results
    # from outbreak.celery import run_multi_sim
    # results = run_multi_sim(sim,n_runs, analyzer=analyzer, celery=True)

    # Run using MultiSim
    if n_runs == 1:
        sim.run()
        s = sim
        results = [sim.results]
    else:
        s = cv.MultiSim(sc.dcp(sim), n_runs=n_runs, keep_people=True, par_args={'ncpus': 4})
        s.run()
        s.reduce()


    ####### ANALYZE RESULTS

    def plot_cum_diagnosed(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['cum_diagnoses'].low, s.results['cum_diagnoses'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['cum_diagnoses'].values[:], color='b', alpha=0.1)

        cases = pd.read_csv('new_cases.csv')
        cases['day'] = cases['Date'].map(sim.day)
        cases.set_index('day', inplace=True)
        cases = cases.loc[cases.index >= 0]['vic'].astype(int).cumsum()
        ax.scatter(cases.index, cases.values, s=5, color='k')
        after_lockdown = cases.index.values > 0
        ax.scatter(cases.index.values[after_lockdown], cases.values[after_lockdown], s=5, color='r')
        ax.axvline(x=jul2, color='grey', linestyle='--')
        ax.axvline(x=jul23, color='grey', linestyle='--')
        ax.axvline(x=aug6, color='grey', linestyle='--')

        ax.set_title('Cumulative diagnosed cases')

        exponent = []
        for res in s.sims:
            diagnoses = res.results['cum_diagnoses'].values[:]
            n_window = (diagnoses > 50) & (diagnoses < 2000)
            if sum(n_window) > 4:
                # Need enough data points to be able to produce a reasonable curve fit
                x = s.base_sim.tvec[n_window]
                y = diagnoses[n_window]
                coeffs = np.polyfit(x, np.log(y), 1, w=np.sqrt(y))
                exponent.append(coeffs[0])
            else:
                exponent.append(0)  # Because it never reached 50 diagnoses

        # Fit exponential to data
        x = cases.index
        y = cases.values
        n_window = (y > 50) & (y < 2000)
        coeffs = np.polyfit(x[n_window], np.log(y[n_window]), 1, w=np.sqrt(y[n_window]))
        # ax.plot(np.exp(coeffs[1])*np.exp(coeffs[0]*x),'k--', linewidth=1)

        ax.text(0.05, 0.9, f'Data exponent = {coeffs[0]:.4f}', transform=ax.transAxes)
        ax.text(0.05, 0.80, f'Average model exponent = {np.mean(exponent):.4f}', transform=ax.transAxes)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: sim.date(x)))
        ax.locator_params('x', nbins=3)


    def plot_cum_infections(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['cum_infections'].low, s.results['cum_infections'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['cum_infections'].values[:], color='b', alpha=0.1)
        ax.set_title('Cumulative infections')
        #ax.hlines(params.pars['pop_size'], 0, s.base_sim.tvec[-1])
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: sim.date(x)))
        ax.locator_params('x', nbins=3)


    def plot_new_diagnoses(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['new_diagnoses'].low, s.results['new_diagnoses'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['new_diagnoses'].values[:], color='b', alpha=0.1)
        ax.set_title('New diagnoses')

        cases = pd.read_csv('new_cases.csv')
        cases['day'] = cases['Date'].map(sim.day)
        cases.set_index('day', inplace=True)
        cases = cases.loc[cases.index >= 0]['vic'].astype(int)
        ax.scatter(cases.index, cases.values, color='k')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: sim.date(x)))
        ax.locator_params('x', nbins=3)
        ax.axvline(x=jul2, color='grey', linestyle='--')
        ax.axvline(x=jul23, color='grey', linestyle='--')
        ax.axvline(x=aug6, color='grey', linestyle='--')


    def plot_daily_tests(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['new_tests'].low, s.results['new_tests'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['new_tests'].values[:], color='b', alpha=0.1)

        tests = pd.read_csv('new_tests.csv')
        tests['day'] = tests['Date'].map(sim.day)
        tests.set_index('day', inplace=True)
        tests = tests.loc[tests.index >= 0]['vic'].astype(float)
        tests = tests * scale_tests * (sim.n / 4.9e6)  # Approximately scale to number of simulation agents
        ax.scatter(tests.index, tests.values, color='k')
        ax.set_title('Daily tests')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: sim.date(x)))
        ax.locator_params('x', nbins=3)


    def plot_test_yield(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['test_yield'].low, s.results['test_yield'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['test_yield'].values[:], color='b', alpha=0.1)
        ax.set_title('Test yield*')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: sim.date(x)))
        ax.locator_params('x', nbins=3)


    def plot_active_cases(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['n_infectious'].low, s.results['n_infectious'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['n_infectious'].values[:], color='b', alpha=0.1)
        ax.set_title('Active cases')
        cases = pd.read_csv('active_cases.csv')
        cases['day'] = cases['Date'].map(sim.day)
        cases.set_index('day', inplace=True)
        cases = cases.loc[cases.index >= 0]['vic'].astype(int)
        ax.scatter(cases.index, cases.values, color='k')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: sim.date(x)))
        ax.locator_params('x', nbins=3)


    def plot_severe_infections(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['n_severe'].low, s.results['n_severe'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['n_severe'].values[:], color='b', alpha=0.1)
        ax.set_title('Severe infections')

        hosp = pd.read_csv('hospitalised.csv')
        hosp['day'] = hosp['Date'].map(sim.day)
        hosp.set_index('day', inplace=True)

        hosp = hosp.loc[hosp.index >= 0]['vic'].astype(int)
        ax.scatter(hosp.index, hosp.values, color='k')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: sim.date(x)))
        ax.locator_params('x', nbins=3)


    fig, ax = plt.subplots(3, 2)
    fig.set_size_inches(8, 11)

    titlestr = f'{n_imports} imported cases per day, seeded {seeded_cases}'

    fig.suptitle(titlestr)

    plot_new_diagnoses(ax[0][0])
    plot_cum_diagnosed(ax[0][1])
    plot_cum_infections(ax[2][0])

    plot_daily_tests(ax[1][0])
    plot_active_cases(ax[1][1])
    plot_severe_infections(ax[2][1])

    plt.savefig('vic_calibrate_2008.png')
    plt.show()



