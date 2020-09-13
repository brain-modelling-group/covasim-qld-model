# Main script to run Victoria calibration

import covasim_australia as cva
import covasim_australia.contacts as co
import covasim as cv
import covasim_australia.policy_updates as policy_updates
import covasim_australia.utils as utils
import sciris as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import covasim_australia.parameters as parameters
import matplotlib.ticker as ticker
from pathlib import Path

# Overall strategy
# 1. Set key parameters for simulation and calibration
# 2. Load data and construct a Sim object
# 3. Add interventions to the Sim
# 4. Run the Sim, optionally with multiple seeds
# 5. Make plots

if __name__ == '__main__':

    run_mode = 'calibrate' # 'calibrate' or 'projection'
    release_day = '2020-09-14'

    # 1 - KEY PARAMETERS
    start_day = '2020-06-01'

    if run_mode == 'calibrate':
        n_days = 100 # Total simulation duration (days)
    elif run_mode == 'projection':
        n_days = 200
    else:
        raise Exception('Run mode must be "calibrate" or "projection"')

    n_imports = 0  # Number of daily imported cases. This would influence the early growth rate of the outbreak. Ideally would set to 0 and use seeded infections only?
    seeded_cases = {3:10}  # Seed cases {seed_day: number_seeded} e.g. {2:100} means infect 100 people on day 2. Could be used to kick off an outbreak at a particular time
    beta = 0.0525 # Overall beta
    extra_tests = 200  # Add this many tests per day on top of the linear fit. Alternatively, modify test intervention directly further down
    symp_test = 160  # People with symptoms are this many times more likely to be tested
    n_runs = 8  # Number of simulations to run
    pop_size = 1e5  # Number of agents
    tracing_capacity = 250  # People per day that can be traced. Household contacts are always all immediately notified
    location = 'Victoria' # Location to use when reading input spreadsheets
    scale_tests = 8 # Multiplicative factor for scaling tests by population proportion


    # 2 - LOAD DATA AND CREATE SIM
    db_name = 'input_data_Australia'  # the name of the databook
    epi_name = 'epi_data_Australia'

    all_lkeys = ['H', 'S', 'low_risk_work','high_risk_work', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
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
                            'verbose': 1}}

    metapars = {'noise': 0.0,
                'verbose': 1}

    user_pars, calibration_end = utils.clean_pars(user_pars, [location])

    # return data relevant to each specified location in "locations"
    all_data = cva.read_data(locations=[location],
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
    params.pars['verbose'] = 1
    params.pars['rand_seed'] = 3

    params.extrapars['symp_test'] = symp_test

    # Uncomment section below to use population scaling
    params.pars['pop_scale'] = int(4.9e6 / params.pars['pop_size'])
    params.pars['rescale'] = True
    params.pars['rescale_threshold'] = 0.05
    params.pars['rescale_factor'] = 1.1

    # Make people
    cv.set_seed(1) # Seed for population generation
    people, layer_members = co.make_people(params)

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
    interventions.append(policy_updates.UpdateNetworks(
                                                       layers=params.dynamic_lkeys,
                                                       contact_numbers=params.pars['contacts'],
                                                       layer_members=layer_members,
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
    jul4 = sim.day('20200704')
    jul9 = sim.day('20200709')
    jul23 = sim.day('20200723')
    aug6 = sim.day('20200806')
    sep14 = sim.day('20200914')
    sep28 = sim.day('20200928')

    #beta_schedule.end('cafe_restaurant_4sqm', jul2)
    #beta_schedule.end('pub_bar_4sqm', jul2)
    #beta_schedule.end('outdoor200', jul2)
    #beta_schedule.add('cafe_restaurant0', jul2)
    #beta_schedule.add('pub_bar0', jul2)
    #beta_schedule.add('church0', jul2)
    #beta_schedule.add('outdoor2', jul2)
    #beta_schedule.add('cSports', jul2)

    beta_schedule.add('stage3_10PC', jul2, jul4)
    beta_schedule.add('stage3_12PC_towers', jul4, jul9)
    beta_schedule.add('stage3_melb', jul9, aug6)
    beta_schedule.add('masks', jul23)

    beta_schedule.add('stage4', aug6)

    interventions.append(beta_schedule)

    # Add clipping policies

    # NE work, switch to stage 4 on aug6
    interventions.append(cv.clip_edges(days=[0,aug6], changes=[0.8,0.1], layers='low_risk_work'))
    # interventions.append(cv.clip_edges(days=[0,aug6], changes=[0.8,0.1], layers='high_risk_work'))

    # Social layer, clipped by stages 3 and 4
    interventions.append(cv.clip_edges(days=[jul2, jul4, jul9, aug6], changes=[0.9, 0.85, 0.3, 0.05], layers='social'))

    # church and pub/bar layer, clipped by stages 3 and 4
    interventions.append(cv.clip_edges(days=[jul2, jul4, jul9], changes=[0.9, 0.85, 0], layers=['church', 'pub_bar']))

    # cafe/restaurant, community sport and school layer, clipped by stages 3 and 4
    interventions.append(cv.clip_edges(days=[jul2, jul4, jul9], changes=[0.9, 0.85, 0.15], layers=['cafe_restaurant', 'cSport', 'S']))



    # Add tracing intervention for households
    interventions.append(utils.limited_contact_tracing(trace_probs={'H': params.extrapars['trace_probs']['H']},
                                                       trace_time={'H': params.extrapars['trace_time']['H']},
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
                                                       ))

    # Add COVIDSafe app based tracing
    # app_layers = ['H', 'S', 'low_risk_work', 'high_risk_work', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar', 'transport', 'public_parks', 'large_events', 'child_care', 'social']
    # interventions.append(policy_updates.AppBasedTracing(name='tracing_app',start_day='2020-09-13',days=['2020-09-13'],coverage=[0.2],layers=app_layers, trace_time=1))

    # Now when we run the model, the major free parameters are the overall beta
    # And the date of the seed infection

    interventions.append(utils.SeedInfection(seeded_cases))


    # Add testing interventions
    tests = pd.read_csv(cva.datadir / 'victoria' / 'new_tests.csv')
    tests['day'] = tests['Date'].map(sim.day)
    tests.set_index('day', inplace=True)
    tests = tests.loc[(tests.index >= 0)  & (tests['vic'] > 0)]['vic'].dropna().astype(int)
    tests = tests * scale_tests * (sim.n / 4.9e6)  # Approximately scale to number of simulation agents - this might need to be changed!

    def moving_average(x, npts):
        window = np.ones(npts)/npts
        avg = np.convolve(np.pad(x,npts,'edge'), window, 'same')
        return avg[npts:-npts]

    smoothed_tests = moving_average(tests.values,7)
    tests_per_day = np.interp(np.arange(params.pars["n_days"]+1), tests.index, smoothed_tests, left=smoothed_tests[0], right=smoothed_tests[-1])

    # plt.figure()
    # plt.plot(tests.values)
    # plt.plot(tests_per_day)

    interventions.append(cv.test_num(daily_tests=extra_tests + tests_per_day,
                                       symp_test=params.extrapars['symp_test'],
                                       quar_test=params.extrapars['quar_test'],
                                       sensitivity=params.extrapars['sensitivity'],
                                       test_delay=params.extrapars['test_delay'],
                                       loss_prob=params.extrapars['loss_prob']))

    # Try switching from test_num to test_prob for projections
    # projection_test_prob = cva.test_prob_with_quarantine(
    #     symp_prob = 0.5,
    #     symp_quar_prob = 0.9,
    #     test_delay=1,
    #     swab_delay=2,
    #     test_isolation_compliance=0.75,
    #     leaving_quar_prob=0.0
    # )
    # interventions.append(cv.sequence([0,50], [calibration_test_num, projection_test_prob]))

    sim.pars['interventions'] = interventions # Add the interventions to the scenario

    # Run using MultiSim
    if n_runs > 1:
        s = cv.MultiSim(sc.dcp(sim), n_runs=n_runs, keep_people=False, par_args={'ncpus': 3})
        s.run()
    else:
        sim.run()
        raise Exception('Must use a MultiSim for analysis')

    for i, x in enumerate(s.sims):
        fname = Path('.')/'results'/f'{run_mode}_{i}.csv'
        fname.parent.mkdir(parents=True, exist_ok=True)  # Make folder if it doesn't exist
        cva.save_csv(x,fname)

    # sc.saveobj('multisim_test.obj',s)
    # s = sc.loadobj('multisim_test.obj')
    s.reduce(quantiles={'low': 0.25, 'high': 0.75})


    ####### ANALYZE RESULTS

    def common_format(ax):
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: sim.date(x)))
        ax.locator_params('x', nbins=5, prune='both')
        ax.set_xlim(0,100)
        plt.setp(ax.get_xticklabels(), ha="right", rotation=30)
        ax.axvline(x=jul9, color='grey', linestyle='--')
        ax.axvline(x=jul23, color='grey', linestyle='--')
        ax.axvline(x=aug6, color='grey', linestyle='--')

        # ax.text(jul9+0.1, 875, 'Stage 3', fontsize=9, horizontalalignment='left')
        # ax.text(jul23+0.1, 875, 'Masks', fontsize=9, horizontalalignment='left')
        # ax.text(aug6+0.1, 875, 'Stage 4', fontsize=9, horizontalalignment='left')

    def plot_cum_diagnosed(ax):

        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['cum_diagnoses'].low, s.results['cum_diagnoses'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['cum_diagnoses'].values[:], color='b', alpha=0.1)

        cases = pd.read_csv(cva.datadir/'victoria'/'new_cases.csv')
        cases['day'] = cases['Date'].map(sim.day)
        cases.set_index('day', inplace=True)
        cases.sort_index(inplace=True)
        cases = cases.loc[cases.index >= 0]['vic'].astype(int).cumsum()
        ax.scatter(cases.index, cases.values, s=10, color='k', alpha=1.0)
        # after_lockdown = cases.index.values > 0
        # ax.scatter(cases.index.values[after_lockdown], cases.values[after_lockdown], s=5, color='r', alpha=1.0)
        # ax.axvline(x=jul2, color='grey', linestyle='--')
        # ax.axvline(x=jul23, color='grey', linestyle='--')
        # ax.axvline(x=aug6, color='grey', linestyle='--')

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

        # ax.text(0.05, 0.9, f'Data exponent = {coeffs[0]:.4f}', transform=ax.transAxes)
        # ax.text(0.05, 0.80, f'Average model exponent = {np.mean(exponent):.4f}', transform=ax.transAxes)
        common_format(ax)



    def plot_cum_infections(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['cum_infections'].low, s.results['cum_infections'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['cum_infections'].values[:], color='b', alpha=0.1)
        ax.set_title('Cumulative infections')
        #ax.hlines(params.pars['pop_size'], 0, s.base_sim.tvec[-1])
        common_format(ax)




    def plot_new_diagnoses(ax):
        # fig, ax = plt.subplots()

        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['new_diagnoses'].low, s.results['new_diagnoses'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['new_diagnoses'].values[:], color='b', alpha=0.1)
        ax.set_title('New diagnoses')

        cases = pd.read_csv(cva.datadir/'victoria'/'new_cases.csv')
        cases['day'] = cases['Date'].map(s.base_sim.day)
        cases.set_index('day', inplace=True)
        cases = cases.loc[cases.index >= 0]['vic'].astype(int)
        ax.scatter(cases.index, cases.values, color='k', s=10, alpha=1.0)
        common_format(ax)
        ax.set_ylabel('Number of cases')

    def plot_daily_tests(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['new_tests'].low, s.results['new_tests'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['new_tests'].values[:], color='b', alpha=0.1)

        tests = pd.read_csv(cva.datadir/'victoria'/'new_tests.csv')
        tests['day'] = tests['Date'].map(sim.day)
        tests.set_index('day', inplace=True)
        tests = tests.loc[tests.index >= 0]['vic'].astype(float)
        tests = tests * scale_tests * (sim.n / 4.9e6)  # Approximately scale to number of simulation agents
        ax.scatter(tests.index, tests.values, color='k', alpha=1.0)
        ax.set_title('Daily tests')
        common_format(ax)




    def plot_test_yield(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['test_yield'].low, s.results['test_yield'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['test_yield'].values[:], color='b', alpha=0.1)
        ax.set_title('Test yield*')
        common_format(ax)




    def plot_active_cases(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['n_infectious'].low, s.results['n_infectious'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['n_infectious'].values[:], color='b', alpha=0.1)
        ax.set_title('Active cases')
        common_format(ax)




    def plot_severe_infections(ax):
        fill_args = {'alpha': 0.3}
        ax.fill_between(s.base_sim.tvec, s.results['n_severe'].low, s.results['n_severe'].high, **fill_args)
        ax.plot(s.base_sim.tvec, s.results['n_severe'].values[:], color='b', alpha=0.1)
        ax.set_title('Severe infections')

        hosp = pd.read_csv(cva.datadir/'victoria'/'hospitalised.csv')
        hosp['day'] = hosp['Date'].map(sim.day)
        hosp.set_index('day', inplace=True)

        hosp = hosp.loc[hosp.index >= 0]['vic'].astype(int)
        ax.scatter(hosp.index, hosp.values, color='k', s=10, alpha=1.0)
        common_format(ax)



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



    fig, ax = plt.subplots(1,3)
    fig.set_size_inches(12, 4)
    plot_new_diagnoses(ax[0])
    plot_cum_diagnosed(ax[1])
    plot_severe_infections(ax[2])
    fig.tight_layout()
    plt.savefig('../Susceptibility/fig1.png', bbox_inches='tight', dpi=300, transparent=False)
    plt.show()



