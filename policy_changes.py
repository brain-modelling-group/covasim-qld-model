def load_pols(databook_path, layers, start_day):
    import pandas as pd
    import sciris as sc
    import numpy as np

    pols = pd.read_excel(databook_path, sheet_name='policies')

    policies = {}
    policies['beta_policies'], policies['import_policies'], policies['clip_policies'], policies['policy_dates'] = {}, {}, {}, {}

    for p, policy in enumerate(pols.iloc[1:,0].tolist()):
        beta_change = np.prod(pols.iloc[p+1, 2:2+len(layers)])
        imports = pols.iloc[p+1, 3+len(layers)]
        to_clip = [str(pols.iloc[p+1, 4+len(layers)]), pols.iloc[p + 1, 5 + len(layers)]]
        if not pd.isnull(pols.iloc[p+1, 6+len(layers)]):
            pol_start = sc.readdate(str(pols.iloc[p+1, 6+len(layers)]))
            n_days = (pol_start-start_day).days
            policies['policy_dates'][policy] = [n_days]
            if not pd.isnull(pols.iloc[p+1, 7+len(layers)]):
                pol_start = sc.readdate(str(pols.iloc[p + 1, 7+len(layers)]))
                n_days = (pol_start - start_day).days
                policies['policy_dates'][policy].append(n_days)
        if beta_change != 1:
            policies['beta_policies'][policy] = {}
            for l, layer in enumerate(layers):
                policies['beta_policies'][policy][layer] = pols.iloc[p+1, 2] * pols.iloc[p+1, l+3]
        if imports > 0:
            policies['import_policies'][policy] = {'n_imports': imports}
        if not pd.isnull(to_clip[1]):
            policies['clip_policies'][policy] = {}
            policies['clip_policies'][policy]['change'] = to_clip[1]
            if not pd.isnull(to_clip[0]):
                policies['clip_policies'][policy]['layers'] = [layer for layer in layers if layer in to_clip[0]]
            else:
                policies['clip_policies'][policy]['layers'] = layers

    return policies

def set_baseline(policies, pars, i_cases, daily_tests, n_days, trace_probs, trace_time):
    import utils
    import numpy as np
    import covasim as cv

    baseline_policies = utils.PolicySchedule(pars['beta_layer'],
                                             policies['beta_policies'])  # create policy schedule with beta layer adjustments
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
        'pars': {
            'interventions': [
                baseline_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=range(len(i_cases)), vals=i_cases)
                }),
                cv.test_num(daily_tests=(daily_tests), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3,
                            loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
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


def relax_policies(torun, policies, base_scenarios, baseline_policies, i_cases, daily_tests, n_days, relax_day, trace_probs, trace_time, restart_imports):
    import numpy as np
    import covasim as cv
    import sciris as sc

    relax_scenarios = {}

    # Relax all policies
    relax_all_policies = sc.dcp(baseline_policies)
    for dates in policies['policy_dates']:
        if len(policies['policy_dates'][dates]) == 1 and dates in policies['beta_policies']:
            relax_all_policies.end(dates, 60)

    relax_scenarios['Full relaxation'] = {
        'name': 'Full relaxation',
        'pars': {
            'interventions': [
                relax_all_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)),
                                      vals=np.append(i_cases, [restart_imports] * (n_days - 60)))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [1000] * (n_days - len(daily_tests))), sympt_test=100.0,
                            quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    for policy in policies['clip_policies']:  # Add relaxed clip edges policies
        details = policies['clip_policies'][policy]
        relax_scenarios['Full relaxation']['pars']['interventions'].append(
            cv.clip_edges(start_day=details['dates'][0], end_day=60,
                          change={layer: details['change'] for layer in details['layers']}))

    scen_names = []
    for policy in policies['policy_dates']:
        if len(policies['policy_dates'][policy]) == 1:  # create list of ongoing policies
            scen_names.append(policy)
    non_beta_policies = {**policies['import_policies'], **policies['clip_policies']}
    for policy in non_beta_policies:
        if policy not in scen_names and policies['policy_dates'][policy][1] > 60:
            scen_names.append(policy)

    for n, name in enumerate(scen_names):
        scen_policies = sc.dcp(baseline_policies)
        if name in policies['beta_policies']:
            scen_policies.end(name, 60)  # add end day if policy is relaxed
        if name in policies['import_policies']:  # add imports if border scenario is relaxed
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, policies['import_policies'][name]['dates'][-1])),
                                vals=np.append(i_cases, [policies['import_policies'][name]['n_imports']] * (
                                            policies['import_policies'][name]['dates'][-1] - 60)))
        else:
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)),
                                vals=np.append(i_cases, [restart_imports] * (n_days - 60)))

        relax_scenarios[scen_names[n]] = {
            'name': scen_names[n],
            'pars': {
                'interventions': [
                    scen_policies,
                    cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                        'n_imports': imports_dict
                    }),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000] * (n_days - len(daily_tests))),
                                sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                ]
            }
        }
        # add edge clipping policies to relax scenario
        for policy in policies['clip_policies']:
            details = policies['clip_policies'][policy]
            if name == policy:
                end_day = 60  # change end day if policy is relaxed
            else:
                end_day = details['dates'][1]
            relax_scenarios[scen_names[n]]['pars']['interventions'].append(
                cv.clip_edges(start_day=details['dates'][0], end_day=end_day,
                              change={layer: details['change'] for layer in details['layers']}))

        scenarios = {}
        # torun = scen_names
        for run in torun:
            trigger = False
            if torun[run] == ['baseline']:
                scenarios[torun[run][0]] = base_scenarios[torun[run][0]]
            elif len(torun[run]) == 1:
                try:
                    scenarios[torun[run][0]] = relax_scenarios[torun[run][0]]
                except KeyError:
                    print("%s was not found as a policy to relax" % torun[run][0])
            elif len(torun[run]) > 1:
                adapt_beta_policies = sc.dcp(baseline_policies)
                adapt_clip_policies = sc.dcp(policies['clip_policies'])
                for policy in torun[run]:
                    if policy in policies['beta_policies']:
                        adapt_beta_policies.end(policy, relax_day)
                    if policy in policies['import_policies']:
                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(relax_day, n_days)),
                                            vals=np.append(i_cases, [policies['import_policies'][policy]['n_imports']] * (
                                                        n_days - relax_day)))
                        trigger = True
                    elif not trigger:
                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)),
                                            vals=np.append(i_cases, [restart_imports] * (n_days - relax_day)))
                    if policy in policies['clip_policies']:
                        adapt_clip_policies[policy]['dates'] = [policies['policy_dates'][policy][0], relax_day]
                scenarios[run] = {
                    'name': run,
                    'pars': {
                        'interventions': [
                            adapt_beta_policies,
                            cv.dynamic_pars(
                                {  # what we actually did but re-introduce imported infections to test robustness
                                    'n_imports': imports_dict
                                }),
                            cv.test_num(daily_tests=np.append(daily_tests, [1000] * (n_days - len(daily_tests))),
                                        sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                            cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                        ]
                    }
                }
                # add edge clipping policies to relax scenario
                for policy in adapt_clip_policies:
                    details = adapt_clip_policies[policy]
                    scenarios[run]['pars']['interventions'].append(
                        cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1],
                                      change={layer: details['change'] for layer in details['layers']}))

    return scenarios, relax_scenarios

def create_scens(torun, policies, baseline_policies, base_scenarios, i_cases, n_days, restart_imports, daily_tests, trace_probs, trace_time):

    import sciris as sc
    import covasim as cv
    import numpy as np
    import utils

    policy_dates = policies['policy_dates']
    beta_policies = policies['beta_policies']
    clip_policies = policies['clip_policies']
    import_policies = policies['import_policies']

    relax_scenarios = {}

    # Relax all policies
    relax_all_policies = sc.dcp(baseline_policies)
    for dates in policy_dates:
        if len(policy_dates[dates]) == 1 and dates in beta_policies:
            relax_all_policies.end(dates, 60)

    relax_scenarios['Full relaxation'] = {
        'name': 'Full relaxation',
        'pars': {
            'interventions': [
                relax_all_policies,
                cv.dynamic_pars({  # jump start with imported infections
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, n_days)),
                                      vals=np.append(i_cases, [restart_imports] * (n_days - 60)))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [10] * (n_days - len(daily_tests))), sympt_test=100.0, quar_test=1.0,
                            sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    for policy in clip_policies:  # Add relaxed clip edges policies
        if policy in policy_dates:
            details = clip_policies[policy]
            relax_scenarios['Full relaxation']['pars']['interventions'].append(
                cv.clip_edges(start_day=details['dates'][0], end_day=60,
                              change={layer: details['change'] for layer in details['layers']}))

    scenarios = sc.dcp(base_scenarios)  # Always add baseline scenario
    beta_schedule, adapt_clip_policies, adapt_beta_policies = sc.dcp(baseline_policies), sc.dcp(clip_policies), sc.dcp(
        beta_policies)
    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                        vals=np.append(i_cases, [restart_imports] * 30))
    for run_pols in torun:
        if run_pols == 'Full relaxation' or run_pols == 'Full relax':
            scenarios['Full relaxation'] = sc.dcp(relax_scenarios['Full relaxation'])
        else:

            torun[run_pols] = sc.dcp(utils.check_policy_changes(torun[run_pols]))  # runs check on consistency across input off/on/replace policies and dates and remove inconsistencies
            for off_on in torun[run_pols]:
                if off_on == 'turn_off':
                    beta_schedule, imports_dict, clip_schedule, policy_dates = sc.dcp(utils.turn_off_policies(torun[run_pols],
                                                                                                       beta_schedule,
                                                                                                       adapt_beta_policies,
                                                                                                       import_policies,
                                                                                                       adapt_clip_policies,
                                                                                                       i_cases, n_days,
                                                                                                       policy_dates,
                                                                                                       imports_dict))
                    # for each policy, check if it's already off at specified date, if it's on then turn off at specified date. Update beta, import and clip.
                elif off_on == 'turn_on':
                    beta_schedule, imports_dict, clip_schedule, policy_dates = sc.dcp(utils.turn_on_policies(torun[run_pols],
                                                                                                      beta_schedule,
                                                                                                      adapt_beta_policies,
                                                                                                      import_policies,
                                                                                                      adapt_clip_policies,
                                                                                                      i_cases, n_days,
                                                                                                      policy_dates,
                                                                                                      imports_dict))
                    # for each policy, check if it's already on at specified date, if it's off then turn on at specified date and off at
                    # specified date (if input). Update beta, import and clip.
                elif off_on == 'replace':
                    beta_schedule, imports_dict, clip_schedule, policy_dates = sc.dcp(utils.replace_policies(torun[run_pols],
                                                                                                      beta_schedule,
                                                                                                      adapt_beta_policies,
                                                                                                      import_policies,
                                                                                                      adapt_clip_policies,
                                                                                                      i_cases, n_days,
                                                                                                      policy_dates,
                                                                                                      imports_dict))
                    # for each policy, check if it's already off at specified date, if it's on then check if first replacement policy is
                    # already on at specified date, if replacement is off then turn on and iterate with following replacements. Update beta, import and clip.
                else:
                    print(
                        'Invalid policy change type %s added to to_run dict, types should be turn_off, turn_on or replace.' % off_on)
            scenarios = sc.dcp(utils.create_scen(scenarios, run_pols, beta_schedule, imports_dict, daily_tests, trace_probs,
                                          trace_time, clip_schedule))

    return scenarios