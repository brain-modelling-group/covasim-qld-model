import covasim as cv
import covasim.utils as cvu
import covasim_australia as cva
import pandas as pd
import sciris as sc
from scipy import stats


import numpy as np

# Calibrated parameters
start_day = '2020-06-01' # Simulation start day (at the start of the second wave)
improve_day = '2020-09-14'  # The day on which app based tracing turns on and contact tracing performance is improved
pop_infected = 10  #: Number of seed infections on day 0
symp_test = 160  # People with symptoms are this many times more likely to be tested
scale_tests = 8  # Multiplicative factor for scaling tests by population proportion
tracing_capacity = 250  # People per day that can be traced. Household contacts are always all immediately notified

calibration_n_days = 110
projection_n_days = 200


def get_victoria_params(pop_size):

    location = 'Victoria'
    db_name = 'input_data_Australia'  # the name of the databook
    epi_name = None

    all_lkeys = ['H', 'S', 'low_risk_work','high_risk_work', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events', 'child_care', 'social','aged_care']
    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']

    user_pars = {
        location: {'pop_size': int(pop_size),
                   'pop_infected': pop_infected,
                   'pop_scale': 1,
                   'rescale': 1,
                   'beta': 0,  # This should be set in get_victoria_sim()
                   'n_days': 30,  # This would normally
                   'calibration_end': None,
                   'verbose': 0
                   }
    }

    metapars = {'noise': 0.0,
                'verbose': 0}

    user_pars, calibration_end = cva.clean_pars(user_pars, [location])

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
    params = cva.setup_params(location=location,
                                     loc_data=loc_data,
                                     metapars=metapars,
                                     sim_pars=loc_pars)

    params.pars["n_imports"] = 0 # Number of imports per day
    params.pars['start_day'] = start_day
    params.pars['verbose'] = 0

    params.extrapars['symp_test'] = symp_test

    # Uncomment section below to use population scaling
    params.pars['pop_scale'] = int(4.9e6 / params.pars['pop_size'])
    params.pars['rescale'] = True
    params.pars['rescale_threshold'] = 0.05
    params.pars['rescale_factor'] = 1.1

    return params


def get_victoria_sim(params, beta, seed, people, layer_members, release_day=None):
    # If the release_day is None, then we are doing a short calibration run

    params = sc.dcp(params)
    params.pars['beta'] = beta
    params.pars['rand_seed'] = seed

    if release_day is None:
        params.pars['n_days'] = calibration_n_days
    else:
        params.pars['n_days'] = projection_n_days

    # Make the base sim
    sim = cv.Sim(pars=params.pars,
                 datafile=None,
                 popfile=people,
                 load_pop=True,
                 save_pop=False
                 )

    # 3 - ASSEMBLE INTERVENTIONS

    interventions = []

    # Add dynamic layers intervention
    interventions.append(cva.UpdateNetworks(layers=params.dynamic_lkeys,
                                                       contact_numbers=params.pars['contacts'],
                                                       layer_members=layer_members,
                                                       dispersion=params.layerchars['dispersion']
                                                       ))

    # Set beta policies
    beta_schedule = cva.PolicySchedule(params.pars["beta_layer"], params.policies['beta_policies'])

    # Policies before Stage 3
    beta_schedule.add('church_4sqm', start_day=0)
    beta_schedule.add('cafe_restaurant_4sqm', start_day=0)
    beta_schedule.add('pub_bar_4sqm', start_day=0)
    beta_schedule.add('outdoor10', start_day=0)
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

    beta_schedule.add('stage3_10PC', jul2, jul4)
    beta_schedule.add('stage3_12PC_towers', jul4, jul9)
    beta_schedule.add('stage3_melb', jul9, aug6)
    beta_schedule.add('stage4', aug6)

    beta_schedule.add('masks', jul23)

    if release_day is not None:
        day = sim.day(release_day)
        beta_schedule.end('stage4', day)
        beta_schedule.end('entertainment', day)
        beta_schedule.end('outdoor10', day)
        beta_schedule.add('outdoor200', start_day=day)

    interventions.append(beta_schedule)

    # ADD CONTACT TRACING
    # - A household intervention with no capacity limit
    # - A lower-performance contact tracing intervention for Jun-Sept
    # - A high-performance intervention for Sept onwards

    trace_probs = params.extrapars['trace_probs']
    trace_time = params.extrapars['trace_time']

    # Add household tracing
    interventions.append(cva.limited_contact_tracing(trace_probs={'H': trace_probs['H']},
                                                       trace_time={'H': trace_time['H']},
                                                       capacity=np.inf,
                                                       ))

    # Remove the household layer from the other tracing interventions
    del trace_probs['H']
    del trace_time['H']
    original_tracing = cva.limited_contact_tracing(trace_probs=sc.dcp(trace_probs),
                                                     trace_time=sc.dcp(trace_time),
                                                     capacity=tracing_capacity,
                                                     )

    # Improve performance in terms of trace time and proportion reached in some layers, particularly
    # where ID checks will be more widely used
    for k in trace_probs:
        trace_time[k] = 1
    trace_probs['cSport'] = 0.5
    trace_probs['entertainment'] = 0.5
    trace_probs['cafe_restaurant'] = 0.5
    trace_probs['pub_bar'] = 0.5

    improved_tracing = cva.limited_contact_tracing(trace_probs=sc.dcp(trace_probs),
                                                     trace_time=sc.dcp(trace_time),
                                                     capacity=tracing_capacity,
                                                     )

    # Switch from the original tracing to improved tracing on the improve day (regardless of when release is)
    interventions.append(cv.sequence([0,improve_day], [original_tracing, improved_tracing]))


    # Add COVIDSafe app based tracing on the improve day (regardless of when release is)
    app_layers = ['H', 'S', 'low_risk_work', 'high_risk_work', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar', 'transport', 'public_parks', 'large_events', 'child_care', 'social']
    interventions.append(cva.AppBasedTracing(name='tracing_app',start_day=sim.day(improve_day),days=[sim.day(improve_day)],coverage=[0.25],layers=app_layers, trace_time=1))


    # ADD TESTING INTERVENTIONS
    tests = pd.read_csv(cva.datadir / 'victoria' / 'new_tests.csv')
    tests['day'] = tests['Date'].map(sim.day)
    tests.set_index('day', inplace=True)
    tests = tests.loc[(tests.index >= 0)  & (tests['vic'] > 0)]['vic'].dropna().astype(int)
    # Remove outliers more than 3 SD from the mean. These are likely data entry irregularities e.g. 3x as many tests reported on one isolated day
    zscore = np.abs(stats.zscore(tests))
    tests = tests.loc[zscore<=3]

    # Scale tests
    tests = tests * scale_tests * (sim.n / 4.9e6)  # Approximately scale to number of simulation agents - this might need to be changed!

    def moving_average(x, npts):
        window = np.ones(npts)/npts
        avg = np.convolve(np.pad(x,npts,'edge'), window, 'same')
        return avg[npts:-npts]

    smoothed_tests = moving_average(tests.values,7)
    daily_tests = np.interp(np.arange(params.pars["n_days"]+1), tests.index, smoothed_tests, left=smoothed_tests[0], right=smoothed_tests[-1])
    # Note how the extrapolation `right` argument above preserves the number of tests for the duration of the simulation

    # plt.figure()
    # plt.plot(tests.values)
    # plt.plot(daily_tests)

    interventions.append(cv.test_num(daily_tests=daily_tests,
                                     symp_test=params.extrapars['symp_test'],
                                     quar_test=params.extrapars['quar_test'],
                                     sensitivity=params.extrapars['sensitivity'],
                                     test_delay=params.extrapars['test_delay'],
                                     loss_prob=params.extrapars['loss_prob']))


    sim.pars['interventions'] = interventions # Add the interventions to the scenario
    return sim