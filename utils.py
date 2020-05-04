import sciris as sc
import covasim as cv
import numpy as np
import matplotlib.pyplot as plt


class PolicySchedule(cv.Intervention):
    def __init__(self, baseline: dict, policies: dict):
        """
        Create policy schedule

        The policies passed in represent all of the possible policies that a user
        can subsequently schedule using the methods of this class

        Example usage:

            baseline = {'H':1, 'S':0.75}
            policies = {}
            policies['Close schools'] = {'S':0}
            schedule = PolicySchedule(baseline, policies)
            schedule.add('Close schools', 10) # Close schools on day 10
            schedule.end('Close schools', 20) # Reopen schools on day 20
            schedule.remove('Close schools')  # Don't use the policy at all

        Args:
            baseline: Baseline (relative) beta layer values e.g. {'H':1, 'S':0.75}
            policies: Dict of policies containing the policy name and relative betas for each policy e.g. {policy_name: {'H':1, 'S':0.75}}

        """
        super().__init__()
        self._baseline = baseline  #: Store baseline relative betas for each layer
        self.policies = sc.dcp(policies)  #: Store available policy interventions (name and effect)
        for policy, layer_values in self.policies.items():
            assert set(layer_values.keys()).issubset(self._baseline.keys()), f'Policy "{policy}" has effects on layers not included in the baseline'
        self.policy_schedule = []  #: Store the scheduling of policies [(start_day, end_day, policy_name)]
        self.days = {}  #: Internal cache for when the beta_layer values need to be recalculated during simulation. Updated using `_update_days`

    def start(self, policy_name: str, start_day: int) -> None:
        """
        Change policy start date

        If the policy is not already present, then it will be added with no end date

        Args:
            policy_name: Name of the policy to change start date for
            start_day: Day number to start policy

        Returns: None

        """
        n_entries = len([x for x in self.policy_schedule if x[2] == policy_name])
        if n_entries < 1:
            self.add(policy_name, start_day)
            return
        elif n_entries > 1:
            raise Exception('start_policy() cannot be used to start a policy that appears more than once - need to manually add an end day to the desired instance')

        for entry in self.policy_schedule:
            if entry[2] == policy_name:
                entry[0] = start_day

        self._update_days()

    def end(self, policy_name: str, end_day: int) -> None:
        """
        Change policy end date

        This only works if the policy only appears once in the schedule. If a policy gets used multiple times,
        either add the end days upfront, or insert them directly into the policy schedule. The policy should
        already appear in the schedule

        Args:
            policy_name: Name of the policy to end
            end_day: Day number to end policy (policy will have no effect on this day)

        Returns: None

        """

        n_entries = len([x for x in self.policy_schedule if x[2] == policy_name])
        if n_entries < 1:
            raise Exception('Cannot end a policy that is not already scheduled')
        elif n_entries > 1:
            raise Exception('end_policy() cannot be used to end a policy that appears more than once - need to manually add an end day to the desired instance')

        for entry in self.policy_schedule:
            if entry[2] == policy_name:
                if end_day <= entry[0]:
                    raise Exception(f"Policy '{policy_name}' starts on day {entry[0]} so the end day must be at least {entry[0]+1} (requested {end_day})")
                entry[1] = end_day

        self._update_days()

    def add(self, policy_name: str, start_day: int, end_day: int = np.inf) -> None:
        """
        Add a policy to the schedule

        Args:
            policy_name: Name of policy to add
            start_day: Day number to start policy
            end_day: Day number to end policy (policy will have no effect on this day)

        Returns: None

        """
        assert policy_name in self.policies, 'Unrecognized policy'
        self.policy_schedule.append([start_day, end_day, policy_name])
        self._update_days()

    def remove(self, policy_name: str) -> None:
        """
        Remove a policy from the schedule

        All instances of the named policy will be removed from the schedule

        Args:
            policy_name: Name of policy to remove

        Returns: None

        """

        self.policy_schedule = [x for x in self.policy_schedule if x[2] != policy_name]
        self._update_days()

    def _update_days(self) -> None:
        # This helper function updates the list of days on which policies start or stop
        # The apply() function only gets run on those days
        self.days = {x[0] for x in self.policy_schedule}.union({x[1] for x in self.policy_schedule if np.isfinite(x[1])})

    def _compute_beta_layer(self, t: int) -> dict:
        # Compute beta_layer at a given point in time
        # The computation is done from scratch each time
        beta_layer = self._baseline.copy()
        for start_day, end_day, policy_name in self.policy_schedule:
            rel_betas = self.policies[policy_name]
            if t >= start_day and t < end_day:
                for layer in beta_layer:
                    if layer in rel_betas:
                        beta_layer[layer] *= rel_betas[layer]
        return beta_layer

    def apply(self, sim: cv.BaseSim):
        if sim.t in self.days:
            sim['beta_layer'] = self._compute_beta_layer(sim.t)
            if sim['verbose']:
                print(f"PolicySchedule: Changing beta_layer values to {sim['beta_layer']}")


    def plot_gantt(self):
        """
        Plot policy schedule as Gantt chart

        Returns: A matplotlib figure with a Gantt chart

        """
        fig, ax = plt.subplots()
        max_time = np.nanmax(np.array([x[0] for x in self.policy_schedule] + [x[1] for x in self.policy_schedule if np.isfinite(x[1])]))
        ax.set_yticks(np.arange(len(self.policies)))
        ax.set_yticklabels(list(self.policies.keys()))
        ax.set_ylim(0 - 0.5, len(self.policies) - 0.5)
        ax.set_xlim(0, max_time + 5)  # Extend a few days so the ends of policies can be seen
        ax.set_xlabel('Days')

        policy_index = {x: i for i, x in enumerate(self.policies.keys())}

        colors = sc.gridcolors(len(self.policies))
        for start_day, end_day, policy_name in self.policy_schedule:
            if not np.isfinite(end_day):
                end_day = 1e6  # Arbitrarily large end day
            ax.broken_barh([(start_day, end_day - start_day)], (policy_index[policy_name] - 0.5, 1), color=colors[policy_index[policy_name]])

        return fig

def create_scen(scenarios, run, beta_policies, imports_dict, clip_policies, pars, extra_pars):

    daily_tests = extra_pars['daily_tests']
    n_days = pars['n_days']
    trace_probs = extra_pars['trace_probs']
    trace_time = extra_pars['trace_time']
    future_tests = extra_pars['future_daily_tests']

    scenarios[run] = {'name': run,
                      'pars': {
                      'interventions': [
                        beta_policies,
                        cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                            'n_imports': imports_dict
                        }),
                        cv.test_num(daily_tests=np.append(daily_tests, [future_tests] * (n_days - len(daily_tests))), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
                            ]
                        }
                     }
    # add edge clipping policies to relax scenario
    for policy in clip_policies:
        if len(clip_policies[policy]) >= 3:
            details = clip_policies[policy]
            scenarios[run]['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1], change={layer: details['change'] for layer in details['layers']}))
    return scenarios

def check_policy_changes(scenario: dict):
    if scenario['turn_off'] and scenario['replace']:
        clash_off_replace_pols = {policy: p for p, policy in enumerate(scenario['turn_off']['off_pols']) if policy in scenario['replace'].keys()}
        if clash_off_replace_pols:
            off_dates = [scenario['turn_off']['dates'][p] for p in list(clash_off_replace_pols.values())]
            replace_dates = [scenario['replace'][policy]['dates'][0] for policy in clash_off_replace_pols]
            for o_date in off_dates:
                for r_date in replace_dates:
                    if o_date <= r_date:
                        date_index = scenario['turn_off']['dates'].index(o_date)
                        print('The torun dict had a clash between turning off and replacing policy %s. Replacement has been prioritised.' % scenario['turn_off']['off_pols'][date_index])
                        del scenario['turn_off']['off_pols'][date_index]
                        del scenario['turn_off']['dates'][date_index]
    if scenario['turn_on'] and scenario['replace']:
        clash_on_replace_pols = {}
        for old_pol in scenario['replace']:
            clash_on_replace_pols[old_pol] = {policy: p for p, policy in enumerate(scenario['turn_on']) if policy in scenario['replace'][old_pol]['replacements']}
        for clash in clash_on_replace_pols:
            if clash_on_replace_pols[clash]:
                on_dates = [scenario['turn_on'][policy] for policy in clash_on_replace_pols[clash]]
                replace_dates = [scenario['replace'][clash]['dates'][p] for p in list(clash_on_replace_pols[clash].values())]
                for o_date in on_dates:
                    for r_date in replace_dates:
                        if len(o_date) > 1:
                            if o_date[0] <= r_date and o_date[1] > r_date:
                                for on_policy in scenario['turn_on']:
                                    if o_date == scenario['turn_on'][on_policy]:
                                        print('The torun dict had a clash between turning on and using policy %s as a replacement. Replacement has been prioritised.' % scenario['turn_on'][on_policy].key())
                                        del on_policy
                        elif len(o_date) == 1:
                            if o_date[0] <= r_date:
                                for on_policy in scenario['turn_on']:
                                    if o_date == scenario['turn_on'][on_policy]:
                                        print('The torun dict had a clash between turning on and using policy %s as a replacement. Replacement has been prioritised.' % scenario['turn_on'][on_policy].key())
                                        del on_policy
                        else:
                            for on_policy in scenario['turn_on']:
                                    if not o_date:
                                        print('The torun dict was not supplied with dates for policy %s, so it has been removed.' % scenario['turn_on'][on_policy].key())
                                        del on_policy
    return scenario

def turn_off_policies(scen, baseline_schedule, beta_policies, import_policies, clip_policies, i_cases, n_days, policy_dates, imports_dict):
    import sciris as sc

    adapt_beta_policies = beta_policies
    adapt_clip_policies = clip_policies
    if len(scen['turn_off'])>0:
        for p, policy in enumerate(scen['turn_off']['off_pols']):
            relax_day = sc.dcp(scen['turn_off']['dates'][p])
            if policy in policy_dates:
                if len(policy_dates[policy]) % 2 == 0:
                    print('Not turning off policy %s at day %s because it is already off.' % (policy, str(relax_day)))
                elif policy_dates[policy][-1] > relax_day:
                    print('Not turning off policy %s at day %s because it is already off. It will be turned on again on day %s' % (policy, str(relax_day), str(policy_dates[policy][-1])))
                else:
                    if policy in adapt_beta_policies:
                        baseline_schedule.end(policy, relax_day)
                    if policy in import_policies:
                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(relax_day, n_days)), vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (n_days-relax_day)))
                    if policy in clip_policies:
                        adapt_clip_policies[policy]['dates'] = sc.dcp([policy_dates[policy][-1], relax_day])
                    policy_dates[policy].append(relax_day)
            else:
                print('Not turning off policy %s at day %s because it was never on.' % (policy, str(relax_day)))
    return baseline_schedule, imports_dict, adapt_clip_policies, policy_dates

def turn_on_policies(scen, baseline_schedule, beta_policies, import_policies, clip_policies, i_cases, n_days, policy_dates, imports_dict):
    adapt_beta_policies = beta_policies
    adapt_clip_policies = clip_policies
    for policy in scen['turn_on']:
        new_pol_dates = scen['turn_on'][policy]
        date_trigger = False
        start_day = new_pol_dates[0]
        if policy in policy_dates:
            if len(policy_dates[policy]) % 2 != 0:
                print('Not turning on policy %s at day %s because it is already on.' % (policy, str(start_day)))
            elif policy_dates[policy][-1] > start_day:
                print('Not turning on policy %s at day %s because it is already on. It will be turned off again on day %s' % (policy, str(start_day), str(policy_dates[policy][-1])))
            else:
                if policy in adapt_beta_policies:
                    if len(new_pol_dates) > 1:
                        baseline_schedule.add(policy, new_pol_dates[0], new_pol_dates[1])
                        policy_dates[policy].extend(new_pol_dates)
                        date_trigger = True
                    else:
                        baseline_schedule.add(policy, new_pol_dates[0], n_days)
                        policy_dates[policy].extend([new_pol_dates[0], n_days])
                        date_trigger = True
                if policy in import_policies:
                    if len(new_pol_dates) > 1:
                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[policy][0], policy_dates[policy][1]) + np.arange(new_pol_dates[0], new_pol_dates[1])),
                                            vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (policy_dates[policy][1] - policy_dates[policy][0]) + [import_policies[policy]['n_imports']] * (new_pol_dates[1]-new_pol_dates[0])))
                        if not date_trigger:
                            policy_dates[policy].extend(new_pol_dates)
                            date_trigger = True
                    else:
                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[policy][0], policy_dates[policy][1]) + np.arange(new_pol_dates[0], n_days)),
                                            vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (policy_dates[policy][1] - policy_dates[policy][0]) + [import_policies[policy]['n_imports']] * (n_days-new_pol_dates[0])))
                        if not date_trigger:
                            policy_dates[policy].extend([new_pol_dates[0], n_days])
                            date_trigger = True
                if policy in clip_policies:
                    adapt_clip_policies[policy + 'v2'] = sc.dcp(adapt_clip_policies[policy])
                    if len(new_pol_dates) > 1:
                        adapt_clip_policies[policy + 'v2']['dates'] = new_pol_dates
                        if not date_trigger:
                            policy_dates[policy].extend(new_pol_dates)
                    else:
                        adapt_clip_policies[policy + 'v2']['dates'] = [new_pol_dates[0], n_days]
                        if not date_trigger:
                            policy_dates[policy].extend([new_pol_dates[0], n_days])
        else:
            if policy in adapt_beta_policies:
                if len(new_pol_dates) > 1:
                    baseline_schedule.add(policy, new_pol_dates[0], new_pol_dates[1])
                    policy_dates[policy] = new_pol_dates
                    date_trigger = True
                else:
                    baseline_schedule.add(policy, new_pol_dates[0], n_days)
                    policy_dates[policy] = [new_pol_dates[0], n_days]
                    date_trigger = True
            if policy in import_policies:
                if len(new_pol_dates) > 1:
                    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[policy][0], policy_dates[policy][1]) + np.arange(new_pol_dates[0], new_pol_dates[1])),
                                        vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (policy_dates[policy][1] - policy_dates[policy][0]) + [import_policies[policy]['n_imports']] * (new_pol_dates[1]-new_pol_dates[0])))
                    if not date_trigger:
                        policy_dates[policy] = new_pol_dates
                        date_trigger = True
                else:
                    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[policy][0], policy_dates[policy][1]) + np.arange(new_pol_dates[0], n_days)),
                                        vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (policy_dates[policy][1] - policy_dates[policy][0]) + [import_policies[policy]['n_imports']] * (n_days-new_pol_dates[0])))
                    if not date_trigger:
                        policy_dates[policy] = [new_pol_dates[0], n_days]
                        date_trigger = True
            if policy in clip_policies:
                adapt_clip_policies[policy + 'v2'] = sc.dcp(adapt_clip_policies[policy])
                if len(new_pol_dates) > 1:
                    adapt_clip_policies[policy + 'v2']['dates'] = new_pol_dates
                    if not date_trigger:
                        policy_dates[policy] = new_pol_dates
                else:
                    adapt_clip_policies[policy + 'v2']['dates'] = [new_pol_dates[0], n_days]
                    if not date_trigger:
                        policy_dates[policy] = [new_pol_dates[0], n_days]
    return baseline_schedule, imports_dict, adapt_clip_policies, policy_dates

def replace_policies(scen, baseline_schedule, beta_policies, import_policies, clip_policies, i_cases, n_days, policy_dates, imports_dict):
    adapt_beta_policies = beta_policies
    adapt_clip_policies = clip_policies
    for old_pol in scen['replace']:
        old_pol_dates = scen['replace'][old_pol]['dates']
        old_pol_reps = scen['replace'][old_pol]['replacements']
        old_date_trigger = False
        if old_pol in policy_dates:
            if len(policy_dates[old_pol]) % 2 == 0:
                print('Not replacing policy %s at day %s because it is already off.' % (old_pol, str(old_pol_dates[0])))
            elif policy_dates[old_pol][-1] > old_pol_dates[0]:
                print('Not replacing policy %s at day %s because it is already off. It will be turned on again on day %s' % (old_pol, str(old_pol_dates[0]), str(policy_dates[old_pol][-1])))
            else:
                if old_pol in beta_policies:
                    baseline_schedule.end(old_pol, old_pol_dates[0])
                    policy_dates[old_pol].append(old_pol_dates[0])
                    old_date_trigger = True
                if old_pol in import_policies:
                    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[old_pol][0], old_pol_dates[0]),
                                        vals=np.append(i_cases, [import_policies[old_pol]['n_imports']] * (old_pol_dates[0] - policy_dates[old_pol][0]))))
                    if not old_date_trigger:
                        policy_dates[old_pol].append(old_pol_dates[0])
                        old_date_trigger = True
                if old_pol in clip_policies:
                    adapt_clip_policies[old_pol]['dates'][1] = old_pol_dates[0]
                    if not old_date_trigger:
                        policy_dates[old_pol].append(old_pol_dates[0])
                for n, new_policy in enumerate(old_pol_reps):
                    date_trigger = False
                    if new_policy in policy_dates:
                        if len(policy_dates[new_policy]) % 2 != 0:
                            print('Not turning on policy %s as a replacement at day %s because it is already on.' % (new_policy, str(old_pol_dates[0])))
                        elif policy_dates[new_policy][-1] > old_pol_dates[0]:
                            print('Not turning on policy %s as a replacement at day %s because it is already on. It will be turned off again on day %s' % (new_policy, str(old_pol_dates[0]), str(policy_dates[new_policy][-1])))
                        else:
                            if new_policy in adapt_beta_policies:
                                if n == 0:
                                    if len(old_pol_reps) > 1:
                                        baseline_schedule.add(new_policy, old_pol_dates[n])
                                        policy_dates[new_policy].append(old_pol_dates[n])
                                        date_trigger = True
                                    elif n == len(old_pol_reps) - 1 and len(old_pol_reps) < len(old_pol_dates):
                                        baseline_schedule.add(new_policy, old_pol_dates[n], old_pol_dates[n+1])
                                        policy_dates[new_policy].extend([old_pol_dates[n], old_pol_dates[n+1]])
                                        date_trigger = True
                                    else:
                                        baseline_schedule.add(new_policy, old_pol_dates[n])
                                        policy_dates[new_policy].append(old_pol_dates[n])
                                        date_trigger = True
                                else:
                                    baseline_schedule.end(old_pol_reps[n - 1], old_pol_dates[n])
                                    policy_dates[old_pol_reps[n - 1]].append(old_pol_dates[n])
                                    if n == len(old_pol_reps) - 1 and len(old_pol_reps) < len(old_pol_dates):
                                        baseline_schedule.add(new_policy, old_pol_dates[n], old_pol_dates[n+1])
                                        policy_dates[new_policy].extend([old_pol_dates[n], old_pol_dates[n+1]])
                                        date_trigger = True
                                    else:
                                        baseline_schedule.add(new_policy, old_pol_dates[n])
                                        policy_dates[new_policy].append(old_pol_dates[n])
                                        date_trigger = True
                            if new_policy in import_policies:
                                if len(old_pol_dates[n:]) > 1:
                                    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[new_policy][0], policy_dates[new_policy][1]) + np.arange(old_pol_dates[n], old_pol_dates[n+1])),
                                                        vals=np.append(i_cases, [import_policies[new_policy]['n_imports']] * (policy_dates[new_policy][1] - policy_dates[new_policy][0]) + [import_policies[new_policy]['n_imports']] * (old_pol_dates[n+1]-old_pol_dates[n])))
                                    if not date_trigger:
                                        policy_dates[new_policy].extend([old_pol_dates[n], old_pol_dates[n+1]])
                                        date_trigger = True
                                else:
                                    imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[new_policy][0], policy_dates[new_policy][1]) + np.arange(old_pol_dates[n], n_days)),
                                                        vals=np.append(i_cases, [import_policies[new_policy]['n_imports']] * (policy_dates[new_policy][1] - policy_dates[new_policy][0]) + [import_policies[new_policy]['n_imports']] * (n_days-old_pol_dates[n])))
                                    if not date_trigger:
                                        policy_dates[new_policy].extend([old_pol_dates[n], n_days])
                                        date_trigger = True
                            if new_policy in adapt_clip_policies:
                                if n == 0:
                                    adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                                    if len(old_pol_dates) > 1:
                                        adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], old_pol_dates[n+1]]
                                        if not date_trigger:
                                            policy_dates[new_policy].extend([old_pol_dates[n], old_pol_dates[n+1]])
                                    else:
                                        adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], n_days]
                                        if not date_trigger:
                                            policy_dates[new_policy].extend([old_pol_dates[n], n_days])
                                else:
                                    adapt_clip_policies[old_pol_reps[n - 1] + 'v2'][1] = old_pol_dates[n]
                                    adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                                    if len(old_pol_dates) > n + 1:
                                        adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], old_pol_dates[n+1]]
                                        if not date_trigger:
                                            policy_dates[new_policy].extend([old_pol_dates[n], old_pol_dates[n+1]])
                                    else:
                                        adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], n_days]
                                        if not date_trigger:
                                            policy_dates[new_policy].extend([old_pol_dates[n], n_days])
                    else:
                        if new_policy in adapt_beta_policies:
                            if n == 0:
                                if len(old_pol_reps) > 1:
                                    baseline_schedule.add(new_policy, old_pol_dates[n])
                                    policy_dates[new_policy] = [old_pol_dates[n]]
                                    date_trigger = True
                                elif n == len(old_pol_reps) - 1 and len(old_pol_reps) < len(old_pol_dates):
                                    baseline_schedule.add(new_policy, old_pol_dates[n], old_pol_dates[n + 1])
                                    policy_dates[new_policy] = [old_pol_dates[n], old_pol_dates[n + 1]]
                                    date_trigger = True
                                else:
                                    baseline_schedule.add(new_policy, old_pol_dates[n])
                                    policy_dates[new_policy] = [old_pol_dates[n]]
                                    date_trigger = True
                            else:
                                baseline_schedule.end(old_pol_reps[n - 1], old_pol_dates[n])
                                policy_dates[old_pol_reps[n - 1]].append(old_pol_dates[n])
                                if n == len(old_pol_reps) - 1 and len(old_pol_reps) < len(old_pol_dates):
                                    baseline_schedule.add(new_policy, old_pol_dates[n], old_pol_dates[n + 1])
                                    policy_dates[new_policy] = [old_pol_dates[n], old_pol_dates[n + 1]]
                                    date_trigger = True
                                else:
                                    baseline_schedule.add(new_policy, old_pol_dates[n])
                                    policy_dates[new_policy] = [old_pol_dates[n]]
                                    date_trigger = True
                        if new_policy in import_policies:
                            if len(old_pol_dates[n:]) > 1:
                                imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[new_policy][0], policy_dates[new_policy][1]) + np.arange(old_pol_dates[n], old_pol_dates[n+1])),
                                                    vals=np.append(i_cases, [import_policies[new_policy]['n_imports']] * (policy_dates[new_policy][1] - policy_dates[new_policy][0]) + [import_policies[new_policy]['n_imports']] * (old_pol_dates[n+1]-old_pol_dates[n])))
                                if not date_trigger:
                                    policy_dates[new_policy] = [old_pol_dates[n], old_pol_dates[n+1]]
                                    date_trigger = True
                            else:
                                imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(policy_dates[new_policy][0], policy_dates[new_policy][1]) + np.arange(old_pol_dates[n], n_days)),
                                                    vals=np.append(i_cases, [import_policies[new_policy]['n_imports']] * (policy_dates[new_policy][1] - policy_dates[new_policy][0]) + [import_policies[new_policy]['n_imports']] * (n_days-old_pol_dates[n])))
                                if not date_trigger:
                                    policy_dates[new_policy] = [old_pol_dates[n], n_days]
                                    date_trigger = True
                        if new_policy in adapt_clip_policies:
                            if n == 0:
                                adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                                if len(old_pol_dates) > 1:
                                    adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], old_pol_dates[n+1]]
                                    if not date_trigger:
                                        policy_dates[new_policy] = [old_pol_dates[n], old_pol_dates[n+1]]
                                else:
                                    adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], n_days]
                                    if not date_trigger:
                                        policy_dates[new_policy] = [old_pol_dates[n], n_days]
                            else:
                                adapt_clip_policies[old_pol_reps[n - 1] + 'v2'][1] = old_pol_dates[n]
                                adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                                if len(old_pol_dates) > n + 1:
                                    adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], old_pol_dates[n+1]]
                                    if not date_trigger:
                                        policy_dates[new_policy] = [old_pol_dates[n], old_pol_dates[n+1]]
                                else:
                                    adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], n_days]
                                    if not date_trigger:
                                        policy_dates[new_policy] = [old_pol_dates[n], n_days]
        else:
            print('Policy %s could not be replaced because it is not running.' % old_pol)
    return baseline_schedule, imports_dict, adapt_clip_policies, policy_dates