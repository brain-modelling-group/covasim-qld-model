import covasim as cv
import sciris as sc

def make_sim():

    pars = {'pop_size': 250e3,
            'pop_infected': 150,
            'pop_scale': 10,
            'pop_type': 'hybrid',
            'location': 'australia',
            'rescale': True,
            'rand_seed': 1,
            'rel_death_prob': 1.,
            'beta': 0.019, # Overall beta to use for calibration
            'n_imports': 2, # Number of new cases to import per day -- varied over time as part of the interventions
            'start_day': '2020-03-01',
            'end_day': '2020-08-31',
            'verbose': .1}

    # Create beta policies
    # Important dates
    initresponse = '2020-03-15'
    lockdown = '2020-03-23'
    reopen1  = '2020-05-01'
    reopen2  = '2020-05-15'
    reopen3  = '2020-06-01'
    reopen4  = '2020-07-01'
    school_dates = ['2020-05-11', '2020-05-18', ]

    beta_ints = [cv.change_beta(days=[lockdown, reopen2, reopen4], changes=[1.2, 1.1, 1.0], layers=['h'], do_plot=True),
                 cv.clip_edges(days=[initresponse, lockdown]+school_dates, changes=[0.75, 0.05, 0.8, 1], layers=['s'], do_plot=False),
                 cv.change_beta(days=[lockdown, school_dates[0], reopen3, reopen4], changes=[0.2, 0.3, 0.4, 0.5], layers=['w'], do_plot=False),
                 cv.change_beta(days=[lockdown], changes=[0.7], layers=['c'], do_plot=False), # Plot lockdown
                 ]

    pars['interventions'] = beta_ints

    # Testing
    symp_prob_prelockdown = 0.1 # Limited testing pre lockdown
    symp_prob_lockdown = 0.3 # Increased testing during lockdown
    symp_prob_postlockdown = 0.15 # Testing since lockdown
    pars['interventions'].append(cv.test_prob(start_day=0, end_day=lockdown, symp_prob=symp_prob_prelockdown, asymp_quar_prob=0.001))
    pars['interventions'].append(cv.test_prob(start_day=lockdown, end_day=reopen1, symp_prob=symp_prob_lockdown, asymp_quar_prob=0.001))
    pars['interventions'].append(cv.test_prob(start_day=reopen1, symp_prob=symp_prob_postlockdown, asymp_quar_prob=0.001))

    # Tracing
    trace_probs = {'h': 1, 's': 0.95, 'w': 0.8, 'c': 0.05}
    trace_time = {'h': 0, 's': 2, 'w': 2, 'c': 14}
    pars['interventions'].append(cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0))

    # Close borders, then open them again to account for Victorian imports and leaky quarantine
    pars['interventions'].append(cv.dynamic_pars({'n_imports': {'days': [14, 115, 122], 'vals': [0, 5, 0]}}))

    # Actually make the sim
    sim = cv.Sim(pars=pars, datafile='nsw_epi_data.csv')

    return sim


T = sc.tic()

# Settings
domultisim=True

# Plot settings
to_plot = sc.objdict({
    'Diagnoses': ['cum_diagnoses'],
    'Deaths': ['cum_deaths'],
    'Total infections': ['cum_infections'],
    'New infections per day': ['new_infections'],
    })

# Run and plot
if domultisim:
    sim = make_sim()
    msim = cv.MultiSim(base_sim=sim)
    msim.run(n_runs=3, reseed=True, noise=0)
    msim.save()
    sim = msim.base_sim
    msim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'nsw_calibration.png',
             legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4}, interval=21)

else:
    sim = make_sim()
    sim.run()
    sim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'nsw_calibration.png',
             legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4}, interval=21)





sc.toc(T)