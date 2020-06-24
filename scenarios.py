import contacts as co
import covasim as cv
import data
import numpy as np
import parameters
import policy_updates
import sciris as sc
import utils
import warnings


def set_baseline(params, popdict, trace_policies):

    # unpack
    policies = params.policies
    i_cases = params.imported_cases
    daily_tests = params.daily_tests
    pars = params.pars
    n_days = pars['n_days']
    extrapars = params.extrapars
    dynamic_lkeys = params.dynamic_lkeys

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

    base_scenario = {}  # create baseline scenario according to policies from databook

    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(extrapars['relax_day'], extrapars['restart_imports_length'])),
                        vals=np.append(i_cases, [0] * (extrapars['restart_imports_length'] - extrapars['relax_day'])))

    base_scenario = create_scen(scenarios=base_scenario,
                                name='baseline',
                                popdict=popdict,
                                contacts=pars['contacts'],
                                beta_policies=baseline_policies,
                                imports_dict=imports_dict,
                                trace_policies=trace_policies,
                                clip_policies=policies['clip_policies'],
                                daily_tests=daily_tests,
                                dynamic_lkeys=dynamic_lkeys,
                                extrapars=extrapars)

    return base_scenario, baseline_policies


def create_scen(scenarios,
                name,
                popdict,
                contacts,
                beta_policies,
                imports_dict,
                trace_policies,
                clip_policies,
                daily_tests,
                dynamic_lkeys,
                extrapars):

    interventions = [beta_policies,
                     cv.dynamic_pars({'n_imports': imports_dict}),
                     cv.test_num(daily_tests=daily_tests,
                                 symp_test=extrapars['symp_test'],
                                 quar_test=extrapars['quar_test'],
                                 sensitivity=extrapars['sensitivity'],
                                 test_delay=extrapars['test_delay'],
                                 loss_prob=extrapars['loss_prob']),
                     cv.contact_tracing(trace_probs=extrapars['trace_probs'],
                                        trace_time=extrapars['trace_time'],
                                        start_day=0),
                     policy_updates.UpdateNetworks(layers=dynamic_lkeys,
                                                   contact_numbers=contacts,
                                                   popdict=popdict)]

    # add in tracing policies
    tracing_app, id_checks = policy_updates.make_tracing(trace_policies=trace_policies)
    if tracing_app is not None:
        interventions.append(tracing_app)
    if id_checks is not None:
        interventions.append(id_checks)

    # add edge clipping policies to relax scenario
    for policy in clip_policies:
        if len(clip_policies[policy]) >= 3:
            details = clip_policies[policy]
            interventions.append(cv.clip_edges(days=details['dates'],
                                               layers=details['layers'],
                                               changes=details['change']))

    scenarios[name] = {'name': name,
                       'pars': {'interventions': interventions}
                       }

    return scenarios


def create_scens(scen_opts,
                 altered_pols,
                 baseline_policies,
                 base_scenarios,
                 popdict,
                 params):

    scenarios = base_scenarios

    contacts = params.pars['contacts']
    extrapars = params.extrapars
    imported_cases = params.imported_cases
    daily_tests = params.daily_tests
    n_days = params.pars['n_days']
    dynamic_lkeys = params.dynamic_lkeys

    # create necessary params for covasim interventions
    imports_dict = {'days': np.append(range(len(imported_cases)), np.arange(extrapars['relax_day'], extrapars['restart_imports_length'])),
                    'vals': np.append(imported_cases, [extrapars['restart_imports']] * (extrapars['restart_imports_length'] - extrapars['relax_day']))}

    for name, scen in scen_opts.items():
        pols = altered_pols[name]
        beta_schedule = sc.dcp(baseline_policies)
        adapt_clip_pols = sc.dcp(pols['clip_policies'])
        adapt_beta_pols = sc.dcp(pols['beta_policies'])
        policy_dates = sc.dcp(pols['policy_dates'])
        import_pols = sc.dcp(pols['import_policies'])
        adapt_trace_pols = sc.dcp(pols['tracing_policies'])

        for change in scen.keys():
            if change == 'turn_off':
                beta_schedule, imports_dict, clip_schedule, trace_schedule, policy_dates = \
                    sc.dcp(policy_updates.turn_off_policies(scen=scen,
                                                            baseline_schedule=beta_schedule,
                                                            beta_policies=adapt_beta_pols,
                                                            import_policies=import_pols,
                                                            clip_policies=adapt_clip_pols,
                                                            trace_policies=adapt_trace_pols,
                                                            i_cases=imported_cases,
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
                                                           i_cases=imported_cases,
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
                                                           i_cases=imported_cases,
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
                                    daily_tests=daily_tests,
                                    dynamic_lkeys=dynamic_lkeys,
                                    extrapars=extrapars)

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

    # unpack
    policies = params.policies
    all_lkeys = params.all_lkeys

    # create baseline
    base_scenarios, base_policies = set_baseline(params, popdict, policies['tracing_policies'])

    if loc_opts is None:
        return base_scenarios

    # create scenarios from replacing, turning off/on policies
    scen_opts = {}
    altered_pols = {}
    for name, scen in loc_opts.items():
        scen_opts[name] = {}

        loc_pols = sc.dcp(policies)

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
        kind = 'policies'
        if scen.get(kind) is not None:
            new_vals = scen[kind]
            for pol_name, newval in new_vals.items():

                # beta must be specified
                if newval.get('beta') is not None:
                    beta = newval['beta']
                else:
                    raise Exception(f'Please provide a beta value for scenario "{name}"')

                # update all the requested layers by key
                for lkey in all_lkeys:
                    if newval.get(lkey) is not None:
                        l_rr = newval[lkey]
                        loc_pols['beta_policies'][pol_name][lkey] = beta * l_rr

        # tracing policies
        kind = 'tracing_policies'
        if scen.get(kind) is not None:
            keys = ['coverage', 'days']
            new_vals = scen[kind]
            for pol_name, newval in new_vals.items():
                for key, val in newval.items():
                    if key not in keys:
                        warnings.warn(f'"{key}" is not a valid key. Must be one of {keys}')
                    else:
                        loc_pols['tracing_policies'][pol_name][key] = val

        altered_pols[name] = loc_pols

    # create the scenarios
    scenarios = create_scens(scen_opts=scen_opts,
                             altered_pols=altered_pols,
                             baseline_policies=base_policies,
                             base_scenarios=base_scenarios,
                             popdict=popdict,
                             params=params)

    return scenarios


def setup_scens(locations,
                db_name,
                epi_name,
                scen_opts,
                user_pars,
                metapars,
                all_lkeys,
                dynamic_lkeys):

    # for reproducible results
    utils.set_rand_seed(metapars)

    # return data relevant to each specified location in "locations"
    all_data = data.read_data(locations=locations,
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys)

    all_scens = {}
    for location in locations:

        print(f'\nCreating scenarios for "{location}"...')

        loc_data = all_data[location]
        loc_epidata = all_data[location]['epidata']
        loc_pars = user_pars[location]
        loc_opts = scen_opts[location]

        # setup parameters object for this simulation
        params = parameters.setup_params(location=location,
                                         loc_data=loc_data,
                                         metapars=metapars,
                                         user_pars=loc_pars)

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