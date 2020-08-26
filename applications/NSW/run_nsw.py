import covasim as cv
import pandas as pd
import sciris as sc
import numpy as np


def make_sim(whattorun, mask_beta_change=None, load_pop=True, popfile='nswppl.pop', datafile=None, agedatafile=None):

    layers = ['H', 'S', 'W', 'C', 'church', 'pSport', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar', 'transport', 'public_parks', 'large_events', 'social']

    if whattorun == 'calibration':
        end_day = '2020-08-25'
    elif whattorun == 'scenarios':
        end_day = '2020-09-30'
        mask_beta_change = mask_beta_change

    pars = {'pop_size': 100e3,
            'pop_infected': 110,
            'pop_scale': 75,
            'rescale': True,
            'rand_seed': 1,
#            'rel_death_prob': 0.8,
            'beta': 0.0275, # Overall beta to use for calibration
                                    # H     S       W       C       church  psport  csport  ent     cafe    pub     trans   park    event   soc
            'contacts':    pd.Series([4,    21,     5,      1,      20,     40,     30,     25,     19,     30,     25,     10,     50,     6], index=layers).to_dict(),
            'beta_layer':  pd.Series([1,    0.25,   0.3,    0.1,    0.04,   0.2,    0.1,    0.01,   0.04,   0.06,   0.16,   0.03,   0.01,   0.3], index=layers).to_dict(),
            'iso_factor':  pd.Series([0.2,  0,      0,      0.1,    0,      0,      0,      0,      0,      0,      0,      0,      0,      0], index=layers).to_dict(),
            'quar_factor': pd.Series([1,    0.1,    0.1,    0.2,    0.01,   0,      0,      0,      0,      0,      0.1 ,   0,      0,      0], index=layers).to_dict(),
            'n_imports': 2, # Number of new cases to import per day -- varied over time as part of the interventions
            'start_day': '2020-03-01',
            'end_day': end_day,
            'analyzers': cv.age_histogram(datafile=agedatafile, edges=np.linspace(0,75,16), days=[8, 54]), # These days correspond to dates 9 March and 24 April, which is the date window in which NSW has published age-disaggregated case counts
            'verbose': .1}

    sim = cv.Sim(pars=pars,
                 datafile=datafile,
                 popfile=popfile,
                 load_pop=load_pop)

    # Create beta policies
    # Important dates
    initresponse = '2020-03-15'
    lockdown = '2020-03-23'
    reopen1  = '2020-05-01' # Two adults allowed to visit a house
    reopen2  = '2020-05-15' # Up to 5 adults can visit a house; food service and non-essential retail start to resume
    reopen3  = '2020-06-01' # Pubs and regional travel open, plus more social activities
    reopen4  = '2020-07-01' # large events, cinemas, museums, open; fewer restrictions on cafes/pubs/etc,
    school_dates = ['2020-05-11', '2020-05-18', '2020-05-25']

    beta_ints = [cv.clip_edges(days=[initresponse,lockdown]+school_dates, changes=[0.75, 0.05, 0.8, 0.9, 1.0], layers=['S'], do_plot=False),
                 cv.clip_edges(days=[lockdown, reopen2, reopen3, reopen4], changes=[0.5, 0.65, 0.75, 0.85], layers=['W'], do_plot=False),
                 cv.clip_edges(days=[lockdown, reopen2, reopen4], changes=[0, 0.5, 1.0], layers=['pSport'], do_plot=False),
                 cv.clip_edges(days=[lockdown, '2020-06-22'], changes=[0, 1.0], layers=['cSport'], do_plot=False),

#                 cv.change_beta([initresponse, '2020-07-01'], [0.8, 0.85], do_plot=False), # Reduce overall beta to account for distancing, handwashing, etc
                 cv.change_beta([initresponse], [0.8], do_plot=False), # Reduce overall beta to account for distancing, handwashing, etc
                 cv.change_beta(days=[lockdown, reopen2, reopen4], changes=[1.2, 1.1, 1.], layers=['H'], do_plot=True),

                 cv.change_beta(days=[lockdown, reopen2], changes=[0, 0.7], layers=['church'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen1, reopen2, reopen3, reopen4], changes=[0.0, 0.3, 0.4, 0.5, 0.7], layers=['social'], do_plot=False),

                 # Dynamic layers ['C', 'entertainment', 'cafe_restaurant', 'pub_bar', 'transport', 'public_parks', 'large_events']
                 cv.change_beta(days=[lockdown], changes=[0.7], layers=['C'], do_plot=True),
                 cv.change_beta(days=[lockdown, reopen4], changes=[0, 0.7], layers=['entertainment'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen2], changes=[0, 0.7], layers=['cafe_restaurant'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen3, reopen4], changes=[0, 0.5, 0.7], layers=['pub_bar'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen2, reopen4], changes=[0.2, 0.3, 0.7], layers=['transport'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen2, reopen4], changes=[0.4, 0.5, 0.7], layers=['public_parks'], do_plot=False),
                 cv.change_beta(days=[lockdown, reopen4], changes=[0.0, 0.7], layers=['large_events'], do_plot=False),
                 ]

    if whattorun == 'scenarios':
        # Approximate a mask intervention by changing beta in all layers where people would wear masks - assuming not in schools, sport, social gatherings, or home
        beta_ints += [cv.change_beta(days=['2020-08-15']*10, changes=[mask_beta_change]*10,
                                     layers=['W', 'church','C','entertainment','cafe_restaurant','pub_bar','transport','public_parks','large_events'])
                     ]

    sim.pars['interventions'].extend(beta_ints)

    # Testing
    symp_prob_prelockdown = 0.04  # Limited testing pre lockdown
    symp_prob_lockdown = 0.06  # Increased testing during lockdown
    symp_prob_postlockdown = 0.18  # Testing since lockdown
    sim.pars['interventions'].append(cv.test_prob(start_day=0, end_day=lockdown, symp_prob=symp_prob_prelockdown, asymp_quar_prob=0.01, do_plot=False))
    sim.pars['interventions'].append(cv.test_prob(start_day=lockdown, end_day=reopen2, symp_prob=symp_prob_lockdown, asymp_quar_prob=0.01,do_plot=False))
    sim.pars['interventions'].append(cv.test_prob(start_day=reopen2, symp_prob=symp_prob_postlockdown, asymp_quar_prob=0.02,do_plot=True))

    # Tracing
    trace_probs_1 = {'H': 1, 'S': 0.95, 'W': 0.8, 'C': 0.05, 'church': 0.5, 'pSport': 0.8, 'cSport': 0.5,
                     'entertainment': 0.01, 'cafe_restaurant': 0.01, 'pub_bar': 0.01, 'transport': 0.01,
                     'public_parks': 0.01, 'large_events': 0.01, 'social': 0.9}
    trace_probs_2 = {'H': 1, 'S': 0.95, 'W': 0.8, 'C': 0.01, 'church': 0.5, 'pSport': 0.8, 'cSport': 0.5,
                 'entertainment': 0.3, 'cafe_restaurant': 0.3, 'pub_bar': 0.3, 'transport': 0.01,
                 'public_parks': 0.01, 'large_events': 0.3, 'social': 0.9}
#    trace_probs = {'H': 1, 'S': 0.95, 'W': 0.8, 'C': 0.3, 'church': 0.3, 'pSport': 0.8, 'cSport': 0.5,
#                     'entertainment': 0.3, 'cafe_restaurant': 0.3, 'pub_bar': 0.3, 'transport': 0.01,
#                     'public_parks': 0.01, 'large_events': 0.01, 'social': 0.8}
    trace_time = {'H': 0, 'S': 2, 'W': 2, 'C': 14, 'church': 5, 'pSport': 3, 'cSport': 3, 'entertainment': 14,
                    'cafe_restaurant': 14, 'pub_bar': 14, 'transport': 14, 'public_parks': 14, 'large_events': 14,
                    'social': 3}
#    sim.pars['interventions'].append(cv.contact_tracing(trace_probs=trace_probs_1, trace_time=trace_time, start_day=0, do_plot=False))
    sim.pars['interventions'].append(cv.contact_tracing(trace_probs=trace_probs_1, trace_time=trace_time, start_day=0, end_day=reopen4, do_plot=False))
    sim.pars['interventions'].append(cv.contact_tracing(trace_probs=trace_probs_2, trace_time=trace_time, start_day=123, do_plot=False))

    # Close borders, then open them again to account for Victorian imports and leaky quarantine
    sim.pars['interventions'].append(cv.dynamic_pars({'n_imports': {'days': [14, 110, 115], 'vals': [0, 5, 0]}}, do_plot=False))

    sim.initialize()

    return sim


# Start setting up to run
# NB, this file assumes that you've already generated a population file saved in the same folder as this script, called nswpop.pop

T = sc.tic()

# Settings
whattorun = ['calibration', 'scenarios'][0]
domulti = True
doplot = False
dosave = True
n_runs = 100

# Filepaths
inputsfolder = 'inputs'
resultsfolder = 'results'
datafile = f'{inputsfolder}/nsw_epi_data_os_removed.csv'
agedatafile = f'{inputsfolder}/nsw_age_data.csv'

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
        sim = make_sim(whattorun, load_pop=True, popfile='nswppl.pop', datafile=datafile, agedatafile=agedatafile)
        msim = cv.MultiSim(base_sim=sim)
        msim.run(n_runs=n_runs, reseed=True, noise=0)
        if dosave: msim.save(f'{resultsfolder}/nsw_{whattorun}.obj')
        if doplot:
            msim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'nsw_{whattorun}.png',
                  legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4}, interval=21)


    elif whattorun == 'scenarios':

        # Calculation of the mask_beta_change is (1-maskuptake)*0.7 + maskuptake*0.7*maskeff
        # Using values of maskuptake in [0, 0.5, 0.7] and maskeff in [0.05, 0.1, 0.2], this gives values in the range [0.6, 0.7]
        # Calculation of the mask_beta_change is (1-maskuptake)*0.7 + maskuptake*0.7*(1-maskeff)
        # Using values of maskuptake in [0, 0.5, 0.7] and maskeff = 0.23, this gives values in the range [0.59, 0.62, 0.7]
        # Using values of maskuptake in [0, 0.5, 0.7] and maskeff = 0.3, this gives values in the range [0.55, 0.6, 0.7]
        mask_beta_change = [0.55, 0.59, 0.6, 0.62, 0.7]
        all_layer_counts = {}
        layer_remap = {'H': 0, 'S': 1, 'W': 2, 'church': 3, 'pSport': 3, 'cSport': 3, 'social': 3, 'C': 4,
                       'entertainment': 4,
                       'cafe_restaurant': 4, 'pub_bar': 4, 'transport': 4, 'public_parks': 4, 'large_events': 4,
                       'importation': 4, 'seed_infection': 4}
        n_new_layers = 5  # H, S, W, DC, SC

        for jb in mask_beta_change:
            sim = make_sim(whattorun, mask_beta_change=jb, load_pop=True, popfile='nswppl.pop', datafile=datafile, agedatafile=agedatafile)
            msim = cv.MultiSim(base_sim=sim)
            msim.run(n_runs=n_runs, reseed=True, noise=0, keep_people=True)

            all_layer_counts[jb] = np.zeros((n_runs, sim.npts, n_new_layers))

            for sn, sim in enumerate(msim.sims):
                tt = sim.make_transtree()
                for source_ind, target_ind in tt.transmissions:
                    dd = tt.detailed[target_ind]
                    date = dd['date']
                    layer_num = layer_remap[dd['layer']]
                    all_layer_counts[jb][sn, date, layer_num] += sim.rescale_vec[date]

            if dosave: msim.save(f'{resultsfolder}/nsw_{whattorun}_{int(jb*100)}.obj')

            if doplot:
                msim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'nsw_{whattorun}_{int(jb*100)}.png',
                      legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4}, interval=21)

        if dosave: sc.saveobj(f'{resultsfolder}/nsw_layer_counts.obj', all_layer_counts)

else:

    if whattorun == 'calibration':
        sim = make_sim(whattorun, load_pop=True, popfile='nswppl.pop', datafile=datafile, agedatafile=agedatafile)
        sim.run(keep_people=True)
        if dosave: sim.save(f'{resultsfolder}/nsw_{whattorun}_single.obj',keep_people=True)
        if doplot:
            sim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'nsw_{whattorun}.png',
                  legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4}, interval=28)
    elif whattorun == 'scenarios':
        # Calculation of the mask_beta_change is (1-maskuptake)*0.7 + maskuptake*0.7*(1-maskeff)
        # Using values of maskuptake in [0, 0.5, 0.7] and maskeff = 0.23, this gives values in the range [0.59, 0.62, 0.7]
        # Using values of maskuptake in [0, 0.5, 0.7] and maskeff = 0.3, this gives values in the range [0.55, 0.6, 0.7]
        mask_beta_change = [0.55, 0.59, 0.6, 0.62, 0.7]
        for jb in mask_beta_change:
            sim = make_sim(whattorun, mask_beta_change=jb, load_pop=True, popfile='nswppl.pop', datafile=datafile, agedatafile=agedatafile)
            sim.run(keep_people=True)
            if dosave: sim.save(f'{resultsfolder}/nsw_{whattorun}_{int(jb*100)}_single.obj',keep_people=True)
            if doplot:
                sim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'nsw_{whattorun}_{int(jb*100)}.png',
                      legend_args={'loc': 'upper left'}, axis_args={'hspace': 0.4}, interval=28)

sc.toc(T)