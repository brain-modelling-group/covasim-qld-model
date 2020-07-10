
import matplotlib
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop, policy_changes, os, plot_scenarios
dirname = os.path.dirname(os.path.abspath(__file__))
import load_parameters_int, load_pop_int
import tqdm
import pandas as pd

if __name__ == '__main__': # need this to run in parallel on windows
    # What to do
    todo = ['loaddata',
            'gen_pop',
            # 'gen_results', # Re-run the simulations, otherwise load pre-existing results
            ]

    for_powerpoint = False
    verbose    = 1
    seed       = 1

    # load parameters
    pars, metapars, extra_pars, population_subsets = load_parameters.load_pars()

    # Process and read in data
    if 'loaddata' in todo:
        sd, extra_pars['i_cases'], extra_pars['daily_tests'] = load_parameters.load_data(databook_path=extra_pars['databook_path'],
                                                                                         start_day=pars['start_day'],
                                                                                         end_day=extra_pars['end_day'],
                                                                                         data_path=extra_pars['data_path'],
                                                                                         setting=extra_pars['setting'])

    pars['pop_infected'] = 0
    pars['n_days'] = 90
    extra_pars['i_cases'][:] = 0
    extra_pars['restart_imports'] = 0,
    extra_pars['restart_imports_length'] = 0
    pars['rescale'] = 0
    pars['pop_scale'] = 1
    metapars['n_runs'] = 1000
    ncpus = 32

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'],
                                                  contact_numbers=pars['contacts'],
                                                  population_subsets = population_subsets,
                                                  setting=extra_pars['setting'])
        sc.saveobj(extra_pars['popfile'], popdict)
    else:
        popdict = sc.loadobj(extra_pars['popfile'])

    sim = cv.Sim(pars, popfile=extra_pars['popfile'], datafile=extra_pars['data_path'], pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=extra_pars['popfile'])

    # Read a variety of policies from databook sheet 'policies', and set up the baseline according to their start and end dates
    policies = policy_changes.load_pols(databook_path=extra_pars['databook_path'], layers=pars['contacts'].keys(),
                                        start_day=pars['start_day'])
    # ToDO: Tracing app policies need to be added to policies sheet and to policy read in function, also add start day (and end day?) to policies['policy_dates']
    policies['trace_policies'] = {'tracing_app': {'layers': ['H', 'S', 'C', 'Church', 'pSport', 'cSport', 'entertainment', 'cafe_restaurant',
                                                             'pub_bar', 'transport', 'national_parks', 'public_parks', 'large_events',
                                                             'social'], # Layers which the app can target, excluding beach, child_care and aged_care
                                                  'coverage': [0.05, 0.05], # app coverage at time in days
                                                  'dates': [60, 90], # days when app coverage changes
                                                  'trace_time': 0,
                                                  'start_day': 60,
                                                  'end_day': None}}
    policies['policy_dates']['tracing_app'] = [policies['trace_policies']['tracing_app']['start_day']]

    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, extra_pars, popdict)
    torun = plot_scenarios.plot_scenarios('1',extra_pars)
    scenarios, scenario_policies = policy_changes.create_scens(torun, policies, baseline_policies, base_scenarios, pars, extra_pars, popdict)

    # scenarios = {k:v for k,v in scenarios.items() if k == 'Full relaxation'}

    for scenario in scenarios.values():
        scenario['pars']['interventions'].append(utils.SeedInfection({61:1}))


    if 'gen_results' in todo:
        for i, (scen_name, scen) in enumerate(scenarios.items()):
            scens = cv.Scenarios(sim=sim, basepars=pars, metapars=metapars, scenarios={scen_name:scen})
            scens.run(verbose=verbose, debug=False, par_args={'ncpus':ncpus})
            scens.save(f'susceptibility_{i}.scen')
        raise Exception('Results complete')
    else:
        sims = {}
        for i, (scen_name, scen) in enumerate(tqdm.tqdm(scenarios.items())):
            scens = cv.Scenarios.load(f'susceptibility_{i}.scen')
            sims[scen_name] = scens.sims[scen_name]

    # Susceptibility distribution plots
    import matplotlib.pyplot as plt
    import numpy as np
    import scipy.stats as stats
    import textwrap

    def positive_kde(vals,npts=100):
        value_range = (vals.min(), vals.max())
        kernel = stats.gaussian_kde(np.concatenate([vals.ravel(),-vals.ravel()]))
        x = np.linspace(*value_range, npts)
        y = 2*kernel(x)
        return x,y



    del scenarios['Full relaxation']

    p_less_than_50 = []
    p_less_than_100 = []
    labels = []


    for scen_name in scenarios.keys():
        vals = np.array([x.results['cum_infections'][-1] for x in sims[scen_name]])
        p_less_than_50.append(sum(vals<50)/len(vals))
        p_less_than_100.append(sum(vals<100)/len(vals))

    idx = np.argsort(p_less_than_100)[::-1]
    p_gt_50 = 1-np.array(p_less_than_50)
    p_gt_100 = 1-np.array(p_less_than_100)
    ind = np.arange(len(idx))  # the x locations for the groups
    width = 0.5  # the width of the bars: can also be len(x) sequence
    plt.style.use('default')
    fig, ax = plt.subplots()
    p1 = plt.bar(ind, p_gt_50[idx]-p_gt_100[idx],width, bottom=p_gt_100[idx], label='> 50', color='b')
    p2 = plt.bar(ind, p_gt_100[idx], width, label='> 100', color='r')
    plt.ylabel('Probability')
    plt.title('Probability of outbreak size')
    wrapped_labels = np.array(['\n'.join(textwrap.wrap(x.capitalize(),20)) for x in scenarios.keys()])
    plt.xticks(ind, wrapped_labels[idx],rotation=0)
    plt.legend()
    plt.show()
    fig.set_size_inches(16, 7)
    fig.savefig('probability_bars.png', bbox_inches='tight', dpi=300, transparent=False)

    # Boxplot of infection size
    records = []
    for scen_name in scenarios.keys():
        for sim in sims[scen_name]:
            infections = sim.results['cum_infections'][-1]
            doubling_time = sim.results['doubling_time'][-21:-7].mean()
            records.append((scen_name,infections, doubling_time))
    df = pd.DataFrame.from_records(records, columns=['Scenario','Infections','Doubling time'],index='Scenario')

    data = []
    for scen in scenarios.keys():
        data.append(df.loc[scen,'Infections'].values)
    fig, ax = plt.subplots()
    ax.boxplot(data, showfliers=False)
    wrapped_labels = np.array(['\n'.join(textwrap.wrap(x.capitalize(),20)) for x in scenarios.keys()])

    plt.xticks(1+np.arange(len(scenarios)), wrapped_labels)
    plt.title('Infection size after 30 days')
    fig.set_size_inches(16, 7)
    fig.savefig('infection_size.png', bbox_inches='tight', dpi=300, transparent=False)