import contacts as co
import covasim as cv
import data
import numpy as np
import parameters
import policy_updates
import sciris as sc
import utils


def set_baseline(params, popdict):

    # unpack
    policies = params.policies
    i_cases = params.imported_cases
    daily_tests = params.daily_tests
    pars = params.pars
    n_days = pars['n_days']
    extra_pars = params.extrapars
    trace_probs = extra_pars['trace_probs']  # TODO: check this only leaves the baseline values
    trace_time = extra_pars['trace_time']
    restart_imports_length = extra_pars['restart_imports_length']
    relax_day = extra_pars['relax_day']
    dynam_layers = params.dynamic_lkeys

    baseline_policies = policy_updates.PolicySchedule(pars['beta_layer'], policies['beta_policies'])  # create policy schedule with beta layer adjustments
    for d, dates in enumerate(policies['policy_dates']):  # add start and end dates to beta layer, import and edge clipping policies
        if len(policies['policy_dates'][dates]) == 2: # meaning the policy starts and finishes in baseline period
            if dates in policies['beta_policies']:
                baseline_policies.add(dates, policies['policy_dates'][dates][0], policies['policy_dates'][dates][1])
            if dates in policies['import_policies']:
                policies['import_policies'][dates]['dates'] = np.arange(policies['policy_dates'][dates][0], policies['policy_dates'][dates][1])
            if dates in policies['clip_policies']:
                policies['clip_policies'][dates]['dates'] = [policies['policy_dates'][dates][0], policies['policy_dates'][dates][1]]
        elif len(policies['policy_dates'][dates]) == 1: # meaning the policy only starts in baseline period
            if dates in policies['beta_policies']:
                baseline_policies.add(dates, policies['policy_dates'][dates][0])
            if dates in policies['import_policies']:
                policies['import_policies'][dates]['dates'] = np.arange(policies['policy_dates'][dates][0], n_days)
            if dates in policies['clip_policies']:
                policies['clip_policies'][dates]['dates'] = [policies['policy_dates'][dates][0], n_days]

    base_scenarios = {}  # create baseline scenario according to policies from databook
    base_scenarios['baseline'] = {
        'name': 'Baseline',
        'pars': {'interventions': [baseline_policies,
                cv.dynamic_pars({  # jump start with imported infections
                    'n_imports': dict(days=np.append(range(len(i_cases)),  np.arange(relax_day, restart_imports_length)),
                                      vals=np.append(i_cases, [0] * (restart_imports_length - relax_day)))
                }),
                cv.test_num(daily_tests=(daily_tests), symp_test=5.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0),
                policy_updates.UpdateNetworks(layers=dynam_layers, contact_numbers=pars['contacts'], popdict=popdict)
            ]
        }
    }

    # add edge clipping policies to baseline scenario
    for policy in policies['clip_policies']:
        details = policies['clip_policies'][policy]
        base_scenarios['baseline']['pars']['interventions'].append(
            cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1],
                          change={layer: details['change'] for layer in details['layers']}))

    return base_scenarios, baseline_policies


def create_scen(scenarios,
                name,
                popdict,
                contacts,
                beta_policies,
                imports_dict,
                trace_policies,
                clip_policies,
                n_days,
                daily_tests,
                trace_probs,
                trace_time,
                future_tests,
                dynamic_lkeys):

    scenarios[name] = {'name': name,
                      'pars': {
                      'interventions': [
                        beta_policies,
                        cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                            'n_imports': imports_dict
                        }),
                        cv.test_num(daily_tests=np.append(daily_tests, [future_tests] * (n_days - len(daily_tests))), symp_test=5.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0),
                        policy_updates.UpdateNetworks(layers=dynamic_lkeys, contact_numbers=contacts, popdict=popdict)
                            ]
                        }
                     }

    # add edge clipping policies to relax scenario
    for policy in clip_policies:
        if len(clip_policies[policy]) >= 3:
            details = clip_policies[policy]
            scenarios[name]['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1], change={layer: details['change'] for layer in details['layers']}))
    return scenarios


def create_scens(scen_opts,
                 altered_pols,
                 baseline_policies,
                 base_scenarios,
                 popdict,
                 contacts,
                 i_cases,
                 daily_tests,
                 altered_time,
                 altered_probs,
                 future_tests,
                 n_days,
                 relax_day,
                 restart_imports_length,
                 restart_imports,
                 dynamic_lkeys):

    scenarios = base_scenarios

    imports_dict = {'days': np.append(range(len(i_cases)), np.arange(relax_day, restart_imports_length)),
                    'vals': np.append(i_cases, [restart_imports] * (restart_imports_length - relax_day))}

    for name, scen in scen_opts.items():
        pols = altered_pols[name]
        trace_time = altered_time[name]
        trace_probs = altered_probs[name]
        beta_schedule = sc.dcp(baseline_policies)
        adapt_clip_pols = sc.dcp(pols['clip_policies'])
        adapt_beta_pols = sc.dcp(pols['beta_policies'])
        policy_dates = sc.dcp(pols['policy_dates'])
        import_pols = sc.dcp(pols['import_policies'])
        # temp solution for not having trace policies currently
        if pols.get('trace_policies') is not None:
            adapt_trace_pols = sc.dcp(pols['trace_policies'])
        else:
            adapt_trace_pols = []

        for change in scen.keys():
            if change == 'turn_off':
                beta_schedule, imports_dict, clip_schedule, trace_schedule, policy_dates = \
                    sc.dcp(policy_updates.turn_off_policies(scen=scen,
                                                            baseline_schedule=beta_schedule,
                                                            beta_policies=adapt_beta_pols,
                                                            import_policies=import_pols,
                                                            clip_policies=adapt_clip_pols,
                                                            trace_policies=adapt_trace_pols,
                                                            i_cases=i_cases,
                                                            n_days=n_days,
                                                            policy_dates=policy_dates,
                                                            imports_dict=imports_dict))
            elif change == 'turn_on':
                beta_schedule, imports_dict, clip_schedule, trace_schedule, policy_dates = \
                    sc.dcp(policy_updates.turn_on_policies(scen=scen,
                                                           baseline_schedule=beta_schedule,
                                                           beta_policies=adapt_beta_pols,
                                                           import_policies=import_pols,
                                                           clip_policies=adapt_clip_pols,
                                                           trace_policies=adapt_trace_pols,
                                                           i_cases=i_cases,
                                                           n_days=n_days,
                                                           policy_dates=policy_dates,
                                                           imports_dict=imports_dict))
            elif change == 'replace':
                beta_schedule, imports_dict, clip_schedule, trace_schedule, policy_dates = \
                    sc.dcp(policy_updates.replace_policies(scen=scen,
                                                           baseline_schedule=beta_schedule,
                                                           beta_policies=adapt_beta_pols,
                                                           import_policies=import_pols,
                                                           clip_policies=adapt_clip_pols,
                                                           trace_policies=adapt_trace_pols,
                                                           i_cases=i_cases,
                                                           n_days=n_days,
                                                           policy_dates=policy_dates,
                                                           imports_dict=imports_dict))
            else:
                print(
                    'Invalid policy change type %s added to to_run dict, types should be turn_off, turn_on or replace.' % change)

            scenarios = create_scen(scenarios=scenarios,
                                    name=name,
                                    popdict=popdict,
                                    contacts=contacts,
                                    beta_policies=beta_schedule,
                                    imports_dict=imports_dict,
                                    trace_policies=trace_schedule,
                                    clip_policies=clip_schedule,
                                    n_days=n_days,
                                    daily_tests=daily_tests,
                                    trace_probs=trace_probs,
                                    trace_time=trace_time,
                                    future_tests=future_tests,
                                    dynamic_lkeys=dynamic_lkeys)

    return scenarios


def define_scenarios(loc_opts, params, popdict):
    """

    :param scen_opts: Dict with the following structure
                            {'name_of_scen': {
                                            'replace': ([to_replace1, to_replace2,...], [[replacements1], [replacements2]], [[start_date1, end_date1], [start_date2, end_date2]]),
                                            'turn_off': ([pol1, pol2,...], [date1, date2,...]),
                                            'turn_on' : ([pol1, pol2,...], [date1, date,...]),
                                            'app_cov': float,
                                            'school_risk': float
                                            }
                            }`
    Note that 'replace' & 'turn_on' types can have end dates appended to the end of their date lists.
    :return:
    """

    # create baseline
    base_scenarios, base_policies = set_baseline(params, popdict)

    if loc_opts is None:
        return base_scenarios

    # unpack
    pars = params.pars
    contacts = pars['contacts']
    policies = params.policies
    extra_pars = params.extrapars
    i_cases = params.imported_cases
    n_days = pars['n_days']
    daily_tests = params.daily_tests
    trace_probs = extra_pars['trace_probs']
    trace_time = extra_pars['trace_time']
    restart_imports = extra_pars['restart_imports']
    restart_imports_length = extra_pars['restart_imports_length']
    relax_day = extra_pars['relax_day']
    future_tests = extra_pars['future_daily_tests']
    all_lkeys = params.all_lkeys
    dynamic_lkeys = params.dynamic_lkeys

    # create scenarios from replacing, turning off/on policies
    scen_opts = {}
    altered_pols = {}
    altered_pars = {}
    altered_time = {}
    altered_probs = {}
    for name, scen in loc_opts.items():
        scen_opts[name] = {}

        loc_pols = sc.dcp(policies)
        loc_time = sc.dcp(trace_time)
        loc_probs = sc.dcp(trace_probs)

        # replace policies
        kind = 'replace'
        if scen.get(kind) is not None:
            scen_opts[name][kind] = {}
            rep_scen = scen[kind]
            to_replace = rep_scen[0]
            replacements = rep_scen[1]
            dates = rep_scen[2]
            for i, pol_name in enumerate(to_replace):
                rep_dates = dates[i]
                rep_pols = replacements[i]
                # this line assumes correspondence by index
                scen_opts[name][kind][pol_name] = {'replacements': rep_pols,
                                                   'dates': rep_dates}

        # turn off policies
        kind = 'turn_off'
        if scen.get(kind) is not None:
            scen_opts[name][kind] = {}
            scen_opts[name][kind]['off_pols'] = {}
            off_scen = scen[kind]
            to_turnoff = off_scen[0]
            dates = off_scen[1]
            scen_opts[name][kind] = {'off_pols': to_turnoff,
                                     'dates': dates}

        # turn on policies
        kind = 'turn_on'
        if scen.get(kind) is not None:
            scen_opts[name][kind] = {}
            on_scen = scen[kind]
            to_turnon = on_scen[0]
            dates = on_scen[1]
            for i, pol_name in enumerate(to_turnon):
                start_date = [dates[i]]
                if len(dates) == len(to_turnon) + 1:  # has end date
                    end_date = dates[-1]
                    start_date.append(end_date)
                scen_opts[name][kind][pol_name] = start_date

        # validate & correct
        scen_opts[name] = policy_updates.check_policy_changes(scen_opts[name])

        # check if layer_rr needs to be updated
        kind = 'beta_change'
        if scen.get(kind) is not None:
            new_vals = scen[kind]
            for pol_name, newval in new_vals.items():

                # beta_rr must be specified
                if newval.get('beta_rr') is not None:
                    beta_rr = newval['beta_rr']
                else:
                    Exception(f'Please provide a beta_rr value for scenario "{name}"')

                # update all the requested layers by key
                for lkey in all_lkeys:
                    if newval.get(lkey) is not None:
                        l_rr = newval[lkey]
                        loc_pols['beta_policies'][pol_name][lkey] = beta_rr * l_rr

        # check if layer values need to be updated
        kind = 'layer_change'
        if scen.get(kind) is not None:
            new_vals = scen[kind]
            for val_type, newval in new_vals.items():
                for key, val in newval.items():
                    if val_type == 'trace_time':
                        loc_time[key] = val
                    elif val_type == 'trace_probs':
                        loc_probs[key] = val
                    else:
                        print(f'Layer change of type {val_type} is not valid')

        altered_pols[name] = loc_pols
        altered_time[name] = loc_time
        altered_probs[name] = loc_probs


        # # handle change in app coverage
        # kind = 'app_cov'
        # if scen.get(kind) is not None:
        #     pols = sc.dcp(policies)  # avoid changing for other scenarios
        #     new_cov = scen[kind]
        #     pols['trace_policies']['tracing_app']['coverage'] = [new_cov]
        # else:
        #     pols = policies
        # altered_pols[name] = pols
        #
        # # school transmission risk, relative to household
        # kind = 'school_risk'
        # if scen.get(kind) is not None:
        #     parsc = sc.dcp(pars)
        #     new_risk = scen[kind]
        #     parsc['beta_layer']['S'] = parsc['beta_layer']['H'] * new_risk
        # else:
        #     parsc = pars
        # altered_pars[name] = parsc
        #
        # # school transmission risk, relative to household
        # kind = 'pub_risk'
        # if scen.get(kind) is not None:
        #     pols = sc.dcp(policies)  # avoid changing for other scenarios
        #     new_risk = scen[kind]
        #     pols['beta_policies']['pub_bar_4sqm']['pub_bar'] = new_risk
        # else:
        #     pols = policies
        # altered_pols[name] = pols

    # create the scenarios
    scenarios = create_scens(scen_opts=scen_opts,
                             altered_pols=altered_pols,
                             baseline_policies=base_policies,
                             base_scenarios=base_scenarios,
                             popdict=popdict,
                             contacts=contacts,
                             i_cases=i_cases,
                             daily_tests=daily_tests,
                             altered_time=altered_time,
                             altered_probs=altered_probs,
                             future_tests=future_tests,
                             n_days=n_days,
                             relax_day=relax_day,
                             restart_imports_length=restart_imports_length,
                             restart_imports=restart_imports,
                             dynamic_lkeys=dynamic_lkeys)

    return scenarios


def setup_scens(locations,
                db_name,
                epi_name,
                scen_opts,
                user_pars,
                metapars):

    # for reproducible results
    utils.set_rand_seed(metapars)

    # return data relevant to each specified location in "locations"
    all_data = data.read_data(locations=locations,
                              db_name=db_name,
                              epi_name=epi_name)

    all_scens = {}
    for location in locations:

        print(f'\nCreating scenarios for "{location}"...')

        loc_data = all_data[location]
        loc_epidata = all_data[location]['epidata']
        keys = all_data[location]
        loc_pars = user_pars[location]
        loc_opts = scen_opts[location]

        # setup parameters object for this simulation
        params = parameters.setup_params(location=location,
                                         loc_data=loc_data,
                                         metapars=metapars,
                                         user_pars=loc_pars,
                                         keys=keys)

        people, popdict = co.make_people(params)


        # setup simulation for this location
        sim = cv.Sim(pars=params.pars,
                     datafile=loc_epidata,
                     popfile=people,
                     pop_size=params.pars['pop_size'],
                     load_pop=True,
                     save_pop=False)
        sim.initialize()

        # setup scenarios for this location
        scens = define_scenarios(loc_opts=loc_opts,
                                 params=params,
                                 popdict=popdict)
        scens = cv.Scenarios(sim=sim,
                             metapars=metapars,
                             scenarios=scens)
        all_scens[location] = scens

    return all_scens


def run_scens(scens):
    """Runs scenarios for each country in scens"""

    for location, scen in scens.items():
        scen.run()

    return scens