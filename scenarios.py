import utils
import numpy as np
import covasim as cv
import sciris as sc

def set_baseline(params, popdict):

    #unpack
    policies = params.policies
    i_cases = params.imported_cases
    daily_tests = params.daily_tests
    pars = params.pars
    n_days = pars['n_days']
    extra_pars = params.extrapars
    trace_probs = extra_pars['trace_probs']
    trace_time = extra_pars['trace_time']
    restart_imports_length = extra_pars['restart_imports_length']
    relax_day = extra_pars['relax_day']
    dynam_layers = params.dynamic_lkeys

    baseline_policies = utils.PolicySchedule(pars['beta_layer'], policies['beta_policies'])  # create policy schedule with beta layer adjustments
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

    app_layers = policies['trace_policies']['tracing_app']['layers']
    app_cov = policies['trace_policies']['tracing_app']['coverage']
    app_dates = policies['trace_policies']['tracing_app']['dates']
    app_start = policies['trace_policies']['tracing_app']['start_day']
    app_end = policies['trace_policies']['tracing_app']['end_day']
    app_trace_time = policies['trace_policies']['tracing_app']['trace_time']

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
                utils.AppBasedTracing(layers=app_layers, coverage=app_cov, days=app_dates, start_day=app_start, end_day=app_end, trace_time=app_trace_time), # Adding tracing app to baseline, remove if not the right idea
                utils.UpdateNetworks(layers=dynam_layers, contact_numbers=pars['contacts'], popdict=popdict)
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


def create_scens(torun, policies, baseline_policies, base_scenarios, pars, extra_pars, popdict):

    policy_dates = policies['policy_dates']
    beta_policies = policies['beta_policies']
    clip_policies = policies['clip_policies']
    import_policies = policies['import_policies']
    trace_policies = policies['trace_policies']
    i_cases = extra_pars['i_cases']
    daily_tests = extra_pars['daily_tests']
    n_days = pars['n_days']
    trace_probs = extra_pars['trace_probs']
    trace_time = extra_pars['trace_time']
    restart_imports = extra_pars['restart_imports']
    restart_imports_length = extra_pars['restart_imports_length']
    relax_day = extra_pars['relax_day']
    future_tests = extra_pars['future_daily_tests']
    dynam_layers = extra_pars['dynam_layer']  # note this is in a different dictionary to pars, to avoid conflicts

    relax_scenarios = {}
    scenario_policies = {}
    scenario_policies['baseline'] = sc.dcp(baseline_policies)

    # Relax all policies
    relax_all_policies = sc.dcp(baseline_policies)
    for dates in policy_dates:
        if len(policy_dates[dates]) == 1 and dates in beta_policies:
            relax_all_policies.end(dates, relax_day)

    relax_scenarios['Full relaxation'] = {
        'name': 'Full relaxation',
        'pars': {
            'interventions': [
                relax_all_policies,
                cv.dynamic_pars({  # jump start with imported infections
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(relax_day, min(n_days,restart_imports_length))),
                                      vals=np.append(i_cases, [restart_imports] * (min(n_days,restart_imports_length) - relax_day)))
                }),
                cv.test_num(daily_tests=np.append(daily_tests, [future_tests] * (n_days - len(daily_tests))), symp_test=10.0, quar_test=1.0,
                            sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0), # Don't add tracing app, either it's not in baseline and shouldn't be here or it is in baseline and is relaxed here
                utils.UpdateNetworks(layers=dynam_layers, contact_numbers=pars['contacts'], popdict=popdict)
            ]
        }
    }
    for policy in clip_policies:  # Add relaxed clip edges policies
        if policy in policy_dates:
            details = clip_policies[policy]
            relax_scenarios['Full relaxation']['pars']['interventions'].append(
                cv.clip_edges(start_day=details['dates'][0], end_day=relax_day,
                              change={layer: details['change'] for layer in details['layers']}))

    scenario_policies['Full relax'] = relax_all_policies
    scenarios = sc.dcp(base_scenarios)  # Always add baseline scenario

    for run_pols in torun:
        if run_pols == 'Full relaxation' or run_pols == 'Full relax':
            scenarios['Full relaxation'] = sc.dcp(relax_scenarios['Full relaxation'])
        else:
            torun[run_pols] = sc.dcp(utils.check_policy_changes(torun[run_pols]))  # runs check on consistency across input off/on/replace policies and dates and remove inconsistencies
            beta_schedule, adapt_clip_policies, adapt_beta_policies, policy_dates, import_policies, adapt_trace_policies = sc.dcp(baseline_policies), sc.dcp(policies['clip_policies']), \
                                                                                                     sc.dcp(policies['beta_policies']), sc.dcp(policies['policy_dates']), \
                                                                                                     sc.dcp(policies['import_policies']), sc.dcp(policies['trace_policies'])
            imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(relax_day, restart_imports_length)),
                                vals=np.append(i_cases, [restart_imports] * (restart_imports_length - relax_day)))
            for off_on in torun[run_pols]:
                if off_on == 'turn_off':
                    beta_schedule, imports_dict, clip_schedule, trace_schedule, policy_dates = sc.dcp(utils.turn_off_policies(torun[run_pols], beta_schedule, adapt_beta_policies,
                                                                                                              import_policies, adapt_clip_policies, adapt_trace_policies, i_cases, n_days, policy_dates, imports_dict))
                    # for each policy, check if it's already off at specified date, if it's on then turn off at specified date. Update beta, import and clip.
                elif off_on == 'turn_on':
                    beta_schedule, imports_dict, clip_schedule, trace_schedule, policy_dates = sc.dcp(utils.turn_on_policies(torun[run_pols], beta_schedule, adapt_beta_policies,
                                                                                                              import_policies, adapt_clip_policies, adapt_trace_policies, i_cases, n_days, policy_dates, imports_dict))
                    # for each policy, check if it's already on at specified date, if it's off then turn on at specified date and off at
                    # specified date (if input). Update beta, import and clip.
                elif off_on == 'replace':
                    beta_schedule, imports_dict, clip_schedule, trace_schedule, policy_dates = sc.dcp(utils.replace_policies(torun[run_pols], beta_schedule, adapt_beta_policies,
                                                                                                              import_policies, adapt_clip_policies, adapt_trace_policies, i_cases, n_days, policy_dates, imports_dict))
                    # for each policy, check if it's already off at specified date, if it's on then check if first replacement policy is
                    # already on at specified date, if replacement is off then turn on and iterate with following replacements. Update beta, import and clip.
                else:
                    print(
                        'Invalid policy change type %s added to to_run dict, types should be turn_off, turn_on or replace.' % off_on)
            scenarios = sc.dcp(utils.create_scen(scenarios, run_pols, beta_schedule, imports_dict, trace_schedule, clip_schedule, pars, extra_pars, popdict))
            del clip_schedule, trace_schedule
            scenario_policies[run_pols] = beta_schedule

    return scenarios, scenario_policies


#### UNFINISHED SECOND VERSION ####
# def get_baseline_scen(params):
#     # unpack
#     policies = params.policies
#     imported_cases = params.imported_cases
#     daily_tests = params.daily_tests
#     extra_pars = params.extra_pars
#     trace_probs = extra_pars['trace_probs']
#     trace_time = extra_pars['trace_time']
#     restart_imports = extra_pars['restart_imports']
#     restart_imports_length = extra_pars['restart_imports_length']
#     relax_day = extra_pars['relax_day']
#     dynam_layers = extra_pars['dynam_layer']
#
#     # create dynamic interventions # TODO: need to specify day and value lists
#     # par_list = ['n_imports']
#     # day_list =
#     # val_list =
#     # dynamic_intervention = interventions.get_dynamic_intervention(par_list=par_list,
#     #                                                           day_list=day_list,
#     #                                                           val_list=val_list)
#
#     # numbers to test
#     tests = interventions.get_num_tests(daily_tests=daily_tests,
#                                     symp_test=5.0,
#                                     quar_test=1.0,
#                                     sensitivity=0.7,
#                                     loss_prob=0.0,
#                                     test_delay=3)
#
#     # contact tracing
#
#     # edge clipping policies
#     for pol_name in policies['clip_policies']:
#
#
#     # baseline scenario
#     base_scens = {'baseline': {'name': 'Baseline', 'pars': {'interventions': [tests]}}}
#
#     return base_scens