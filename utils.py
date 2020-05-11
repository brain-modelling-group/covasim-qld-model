import sciris as sc
import covasim as cv
from covasim import utils as cvu
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime as dt
import pylab as pl
from covasim import defaults as cvd
import load_pop



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


    def plot_gantt(self, max_time=None, start_date=None, interval=None, pretty_labels=None):
        """
        Plot policy schedule as Gantt chart

        Returns: A matplotlib figure with a Gantt chart

        """
        fig, ax = plt.subplots()
        if max_time:
            max_time += 5
        else:
            max_time = np.nanmax(np.array([x[1] for x in self.policy_schedule if np.isfinite(x[1])]))

        #end_dates = [x[1] for x in self.policy_schedule if np.isfinite(x[1])]
        if interval:
            xmin, xmax = ax.get_xlim()
            ax.set_xticks(pl.arange(xmin, xmax + 1, interval))

        if start_date:
            @ticker.FuncFormatter
            def date_formatter(x, pos):
                return (start_date + dt.timedelta(days=x)).strftime('%b-%d')

            ax.xaxis.set_major_formatter(date_formatter)
            if not interval:
                ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax.set_xlabel('Dates')
            ax.set_xlim((0, max_time + 5))  # Extend a few days so the ends of policies can be seen

        else:
            ax.set_xlim(0, max_time + 5)  # Extend a few days so the ends of policies can be seen
            ax.set_xlabel('Days')
        schedule = sc.dcp(self.policy_schedule)
        if pretty_labels:
            policy_index = {pretty_labels[x]: i for i, x in enumerate(self.policies.keys())}
            for p, pol in enumerate(schedule):
               pol[2] = pretty_labels[pol[2]]
            colors = sc.gridcolors(len(pretty_labels))
        else:
            policy_index = {x: i for i, x in enumerate(self.policies.keys())}
            colors = sc.gridcolors(len(self.policies))
        ax.set_yticks(np.arange(len(policy_index.keys())))
        ax.set_yticklabels(list(policy_index.keys()))
        ax.set_ylim(0 - 0.5, len(policy_index.keys()) - 0.5)

        for start_day, end_day, policy_name in schedule:
            if not np.isfinite(end_day):
                end_day = 1e6 # Arbitrarily large end day
            ax.broken_barh([(start_day, end_day - start_day)], (policy_index[policy_name] - 0.5, 1), color=colors[policy_index[policy_name]])

        return fig

class AppBasedTracing(cv.Intervention):
    def __init__(self, days, coverage, layers, start_day=0, end_day=None, trace_time=0):
        """
        App based contact tracing parametrized by coverage
        Args:
            days: List/array of day indexes on which a coverage value takes effect e.g. [14, 28]
            coverage: List/array of coverage values corresponding to days e.g. [0.2,0.4]
            layers: List of layer names traceable by the app e.g. ['Household','Beach']
            start_day (int): intervention start day.
            end_day (int): intervention end day
            trace_time: Tracing time (default is 0 as contacts are automatically notified via the system)
        """
        super().__init__()
        assert len(days) == len(coverage), 'Must specify same number of days as coverage values'
        self.days = sc.promotetoarray(days)
        self.coverage = sc.promotetoarray(coverage)
        self.layers = layers
        assert self.days[0] <= start_day
        self.trace_time = dict.fromkeys(self.layers, trace_time)
        self.start_day = start_day
        self.end_day = end_day
        return
    def initialize(self, sim):
        super().initialize(sim)
        self.start_day = sim.day(self.start_day)
        self.end_day = sim.day(self.end_day)
        return
    def apply(self, sim):
        t = sim.t
        if t < self.start_day:
            return
        elif self.end_day is not None and t > self.end_day:
            return
        # Index to use for the current day
        idx = np.argmax(self.days > sim.t)-1 # nb. if sim.t<self.days[0] this will be wrong, hence the validation in __init__()
        trace_prob = dict.fromkeys(self.layers, self.coverage[idx] ** 2)  # Probability of both people having the app
        just_diagnosed_inds = cvu.true(sim.people.date_diagnosed == t)
        if len(just_diagnosed_inds):
            sim.people.trace(just_diagnosed_inds, trace_prob, self.trace_time)
        return


class UpdateNetworks(cv.Intervention):
    def __init__(self, layers, contact_numbers, popdict, start_day=0, end_day=None):
        """
        Update random networks at each time step
        Args:
            layers: List of layer names to resample
            start_day (int): intervention start day.
            end_day (int): intervention end day
            contact_numbers: dictionary of average contacts for each layer
        """
        super().__init__()
        self.layers = layers
        self.start_day = start_day
        self.end_day = end_day
        self.contact_numbers = contact_numbers
        self.popdict = popdict
        return

    def initialize(self, sim):
        super().initialize(sim)
        self.start_day = sim.day(self.start_day)
        self.end_day = sim.day(self.end_day)
        self._include = {} # For each layer, store a boolean array capturing whether that person is in the layer or not
        for lkey in self.layers: # get indices for people in each layer
            self._include[lkey] = [len(x[lkey])>0 for x in self.popdict['contacts']]
        return

    def apply(self, sim):
        t = sim.t
        if t < self.start_day:
            return
        elif self.end_day is not None and t > self.end_day:
            return

        # Loop over dynamic keys
        for lkey in self.layers:

            # Remove existing contacts
            del sim.people.contacts[lkey]

            # Sample new contacts
            new_contacts = {}
            new_contacts['p1'], new_contacts['p2'] = load_pop.random_contacts(self._include[lkey], self.contact_numbers[lkey], array_output=True)
            new_contacts['beta'] = np.ones(new_contacts['p1'].shape, dtype=cvd.default_float)

            # Add new contacts
            sim.people.add_contacts(new_contacts, lkey=lkey)
            sim.people.contacts[lkey].validate()

        return


def create_scen(scenarios, run, beta_policies, imports_dict, trace_policies, clip_policies, pars, extra_pars, popdict):

    daily_tests = extra_pars['daily_tests']
    n_days = pars['n_days']
    trace_probs = extra_pars['trace_probs']
    trace_time = extra_pars['trace_time']
    future_tests = extra_pars['future_daily_tests']
    dynam_layers = extra_pars['dynam_layer']  # note this is in a different dictionary to pars, to avoid conflicts

    scenarios[run] = {'name': run,
                      'pars': {
                      'interventions': [
                        beta_policies,
                        cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                            'n_imports': imports_dict
                        }),
                        cv.test_num(daily_tests=np.append(daily_tests, [future_tests] * (n_days - len(daily_tests))), symp_test=10.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                        cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0),
                        UpdateNetworks(layers=dynam_layers, contact_numbers=pars['contacts'], popdict=popdict)
                            ]
                        }
                     }
    for trace_pol in trace_policies:
        details = trace_policies[trace_pol]
        scenarios[run]['pars']['interventions'].append(AppBasedTracing(layers=details['layers'], coverage=details['coverage'], days=details['dates'], start_day=details['start_day'], end_day=details['end_day'], trace_time=details['trace_time']))
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

def turn_off_policies(scen, baseline_schedule, beta_policies, import_policies, clip_policies, trace_policies,  i_cases, n_days, policy_dates, imports_dict):
    import sciris as sc

    adapt_beta_policies = beta_policies
    adapt_clip_policies = clip_policies
    adapt_trace_policies = trace_policies
    if len(scen['turn_off'])>0:
        for p, policy in enumerate(scen['turn_off']['off_pols']):
            relax_day = sc.dcp(scen['turn_off']['dates'][p])
            if policy in policy_dates:
                if len(policy_dates[policy]) % 2 == 0 and policy_dates[policy][-1] < relax_day:
                    print('Not turning off policy %s at day %s because it is already off.' % (policy, str(relax_day)))
                elif len(policy_dates[policy]) % 2 != 0 and policy_dates[policy][-1] > relax_day:
                    print('Not turning off policy %s at day %s because it is already off. It will be turned on again on day %s' % (policy, str(relax_day), str(policy_dates[policy][-1])))
                else:
                    if policy in adapt_beta_policies:
                        baseline_schedule.end(policy, relax_day)
                    if policy in import_policies:
                        imports_dict = dict(days=np.append(range(len(i_cases)), np.arange(relax_day, n_days)), vals=np.append(i_cases, [import_policies[policy]['n_imports']] * (n_days-relax_day)))
                    if policy in clip_policies:
                        adapt_clip_policies[policy]['dates'] = sc.dcp([policy_dates[policy][-1], relax_day])
                    if policy in trace_policies:
                        adapt_trace_policies[policy]['end_day'] = relax_day
                        adapt_trace_policies[policy]['coverage'] = [cov for c, cov in enumerate(adapt_trace_policies[policy]['coverage']) if adapt_trace_policies[policy]['dates'][ c] < relax_day]
                        adapt_trace_policies[policy]['dates'] = [day for day in adapt_trace_policies[policy]['dates'] if day < relax_day]
                    policy_dates[policy].append(relax_day)
            else:
                print('Not turning off policy %s at day %s because it was never on.' % (policy, str(relax_day)))
    return baseline_schedule, imports_dict, adapt_clip_policies, adapt_trace_policies,  policy_dates

def turn_on_policies(scen, baseline_schedule, beta_policies, import_policies, clip_policies, trace_policies, i_cases, n_days, policy_dates, imports_dict):
    adapt_beta_policies = beta_policies
    adapt_clip_policies = clip_policies
    adapt_trace_policies = trace_policies
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
                            date_trigger = True
                    else:
                        adapt_clip_policies[policy + 'v2']['dates'] = [new_pol_dates[0], n_days]
                        if not date_trigger:
                            policy_dates[policy].extend([new_pol_dates[0], n_days])
                            date_trigger = True
                if policy in trace_policies:
                    adapt_trace_policies[policy + 'v2']= sc.dcp(adapt_trace_policies[policy])
                    if len(new_pol_dates) > 1:
                        adapt_trace_policies[policy + 'v2']['start_day'] = start_day
                        adapt_trace_policies[policy + 'v2']['dates'] = [start_day]
                        adapt_trace_policies[policy + 'v2']['end_day'] = new_pol_dates[1]
                        adapt_trace_policies[policy + 'v2']['coverage'] = [adapt_trace_policies[policy]['coverage'][-1]] # Start coverage where it was when trace_app was first ended, not sure what best option is here
                        if not date_trigger:
                            policy_dates[policy].extend(new_pol_dates)
                    else:
                        adapt_trace_policies[policy + 'v2']['start_day'] = start_day
                        adapt_trace_policies[policy + 'v2']['dates'] = [start_day]
                        adapt_trace_policies[policy + 'v2']['end_day'] = None
                        adapt_trace_policies[policy + 'v2']['coverage'] = [adapt_trace_policies[policy]['coverage'][-1]]  # Start coverage where it was when trace_app was first ended, not sure what best option is here
                        if not date_trigger:
                            policy_dates[policy].append(start_day)
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
            if policy in trace_policies:
                adapt_trace_policies[policy + 'v2'] = sc.dcp(adapt_trace_policies[policy])
                if len(new_pol_dates) > 1:
                    adapt_trace_policies[policy + 'v2']['start_day'] = start_day
                    adapt_trace_policies[policy + 'v2']['dates'] = [start_day]
                    adapt_trace_policies[policy + 'v2']['end_day'] = new_pol_dates[1]
                    adapt_trace_policies[policy + 'v2']['coverage'] = [adapt_trace_policies[policy]['coverage'][-1]] # Start coverage where it was when trace_app was first ended, not sure what best option is here
                    if not date_trigger:
                        policy_dates[policy] = new_pol_dates
                else:
                    adapt_trace_policies[policy + 'v2']['start_day'] = start_day
                    adapt_trace_policies[policy + 'v2']['dates'] = [start_day]
                    adapt_trace_policies[policy + 'v2']['end_day'] = None
                    adapt_trace_policies[policy + 'v2']['coverage'] = [adapt_trace_policies[policy]['coverage'][-1]]  # Start coverage where it was when trace_app was first ended, not sure what best option is here
                    if not date_trigger:
                        policy_dates[policy] = [start_day]
    return baseline_schedule, imports_dict, adapt_clip_policies, adapt_trace_policies, policy_dates

def replace_policies(scen, baseline_schedule, beta_policies, import_policies, clip_policies, trace_policies, i_cases, n_days, policy_dates, imports_dict):
    adapt_beta_policies = beta_policies
    adapt_clip_policies = clip_policies
    adapt_trace_policies = trace_policies
    for old_pol in scen['replace']:
        old_pol_dates = scen['replace'][old_pol]['dates']
        old_pol_reps = scen['replace'][old_pol]['replacements']
        old_date_trigger = False
        if old_pol in policy_dates:
            if len(policy_dates[old_pol]) % 2 == 0 and policy_dates[old_pol][-1] < old_pol_dates[0]:
                print('Not replacing policy %s at day %s because it is already off.' % (old_pol, str(old_pol_dates[0])))
            elif len(policy_dates[old_pol]) % 2 != 0 and policy_dates[old_pol][-1] > old_pol_dates[0]:
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
                        old_date_trigger = True
                if old_pol in trace_policies:
                    adapt_trace_policies[old_pol]['end_day'] = old_pol_dates[0]
                    adapt_trace_policies[old_pol]['coverage'] = [cov for c, cov in enumerate(adapt_trace_policies[old_pol]['coverage']) if adapt_trace_policies[old_pol]['dates'][c] < old_pol_dates[0]]
                    adapt_trace_policies[old_pol]['dates'] = [day for day in adapt_trace_policies[old_pol]['dates'] if day < old_pol_dates[0]]
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
                                if n != 0:
                                    adapt_clip_policies[old_pol_reps[n - 1] + 'v2'][1] = old_pol_dates[n]
                                adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                                if len(old_pol_dates) > 1:
                                    adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], old_pol_dates[n+1]]
                                    if not date_trigger:
                                        policy_dates[new_policy].extend([old_pol_dates[n], old_pol_dates[n+1]])
                                        date_trigger = True
                                else:
                                    adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], n_days]
                                    if not date_trigger:
                                        policy_dates[new_policy].extend([old_pol_dates[n], n_days])
                                        date_trigger = True
                            if new_policy in adapt_trace_policies:
                                if n != 0:
                                    adapt_trace_policies[old_pol_reps[n - 1] + 'v2'][1] = old_pol_dates[n]
                                adapt_trace_policies[new_policy + 'v2'] = sc.dcp(adapt_trace_policies[new_policy])
                                if len(old_pol_dates) > 1:
                                    adapt_trace_policies[new_policy + 'v2']['start_day'] = old_pol_dates[n]
                                    adapt_trace_policies[new_policy + 'v2']['end_day'] = old_pol_dates[n+1]
                                    adapt_trace_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n]]
                                    adapt_trace_policies[new_policy + 'v2']['coverage'] = [adapt_trace_policies[new_policy]['coverage'][-1]] # Start coverage where it was when trace_app was first ended, not sure what best option is here
                                    if not date_trigger:
                                        policy_dates[new_policy].extend([old_pol_dates[n], old_pol_dates[n+1]])
                                else:
                                    adapt_trace_policies[new_policy + 'v2']['start_day'] = old_pol_dates[n]
                                    adapt_trace_policies[new_policy + 'v2']['end_day'] = None
                                    adapt_trace_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n]]
                                    adapt_trace_policies[new_policy + 'v2']['coverage'] = [adapt_trace_policies[new_policy]['coverage'][-1]]  # Start coverage where it was when trace_app was first ended, not sure what best option is here
                                    if not date_trigger:
                                        policy_dates[new_policy].append(old_pol_dates[n])
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
                            if n != 0:
                                adapt_clip_policies[old_pol_reps[n - 1] + 'v2'][1] = old_pol_dates[n]
                            adapt_clip_policies[new_policy + 'v2'] = sc.dcp(adapt_clip_policies[new_policy])
                            if len(old_pol_dates) > 1:
                                adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], old_pol_dates[n+1]]
                                if not date_trigger:
                                    policy_dates[new_policy] = [old_pol_dates[n], old_pol_dates[n+1]]
                            else:
                                adapt_clip_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n], n_days]
                                if not date_trigger:
                                    policy_dates[new_policy] = [old_pol_dates[n], n_days]
                        if new_policy in adapt_trace_policies:
                            if n != 0:
                                adapt_trace_policies[old_pol_reps[n - 1] + 'v2'][1] = old_pol_dates[n]
                            adapt_trace_policies[new_policy + 'v2'] = sc.dcp(adapt_trace_policies[new_policy])
                            if len(old_pol_dates) > 1:
                                adapt_trace_policies[new_policy + 'v2']['start_day'] = old_pol_dates[n]
                                adapt_trace_policies[new_policy + 'v2']['end_day'] = old_pol_dates[n+1]
                                adapt_trace_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n]]
                                adapt_trace_policies[new_policy + 'v2']['coverage'] = [adapt_trace_policies[new_policy]['coverage'][-1]] # Start coverage where it was when trace_app was first ended, not sure what best option is here
                                if not date_trigger:
                                    policy_dates[new_policy] = [old_pol_dates[n], old_pol_dates[n+1]]
                            else:
                                adapt_trace_policies[new_policy + 'v2']['start_day'] = old_pol_dates[n]
                                adapt_trace_policies[new_policy + 'v2']['end_day'] = None
                                adapt_trace_policies[new_policy + 'v2']['dates'] = [old_pol_dates[n]]
                                adapt_trace_policies[new_policy + 'v2']['coverage'] = [adapt_trace_policies[new_policy]['coverage'][-1]]  # Start coverage where it was when trace_app was first ended, not sure what best option is here
                                if not date_trigger:
                                    policy_dates[new_policy] = [old_pol_dates[n]]
        else:
            print('Policy %s could not be replaced because it is not running.' % old_pol)
    return baseline_schedule, imports_dict, adapt_clip_policies, adapt_trace_policies, policy_dates

def policy_plot(scen, plot_ints=False, to_plot=None, do_save=None, fig_path=None, fig_args=None, plot_args=None,
    axis_args=None, fill_args=None, legend_args=None, as_dates=True, dateformat=None,
    interval=None, n_cols=1, font_size=18, font_family=None, grid=True, commaticks=True,
    do_show=True, sep_figs=False, verbose=None, y_lim=None):
    from covasim import defaults as cvd
    from matplotlib.ticker import StrMethodFormatter

    '''
    Plot the results -- can supply arguments for both the figure and the plots.

    Args:
        scen        (covasim Scenario): Scenario with results to be plotted
        scen_name   (str):  Name of the scenario with intervention start dates to plot
        plot_ints   (Bool): Whether or not to plot intervention start dates
        to_plot     (dict): Dict of results to plot; see default_scen_plots for structure
        do_save     (bool): Whether or not to save the figure
        fig_path    (str):  Path to save the figure
        fig_args    (dict): Dictionary of kwargs to be passed to pl.figure()
        plot_args   (dict): Dictionary of kwargs to be passed to pl.plot()
        axis_args   (dict): Dictionary of kwargs to be passed to pl.subplots_adjust()
        fill_args   (dict): Dictionary of kwargs to be passed to pl.fill_between()
        legend_args (dict): Dictionary of kwargs to be passed to pl.legend()
        as_dates    (bool): Whether to plot the x-axis as dates or time points
        dateformat  (str):  Date string format, e.g. '%B %d'
        interval    (int):  Interval between tick marks
        n_cols      (int):  Number of columns of subpanels to use for subplot
        font_size   (int):  Size of the font
        font_family (str):  Font face
        grid        (bool): Whether or not to plot gridlines
        commaticks  (bool): Plot y-axis with commas rather than scientific notation
        do_show     (bool): Whether or not to show the figure
        sep_figs    (bool): Whether to show separate figures for different results instead of subplots
        verbose     (bool): Display a bit of extra information

    Returns:
        fig: Figure handle
    '''

    if verbose is None:
        verbose = scen['verbose']
    sc.printv('Plotting...', 1, verbose)

    if to_plot is None:
        to_plot = cvd.default_scen_plots
    to_plot = sc.dcp(to_plot)  # In case it's supplied as a dict

    # Handle input arguments -- merge user input with defaults
    fig_args = sc.mergedicts({'figsize': (16, 14)}, fig_args)
    plot_args = sc.mergedicts({'lw': 3, 'alpha': 0.7}, plot_args)
    axis_args = sc.mergedicts(
        {'left': 0.15, 'bottom': 0.1, 'right': 0.95, 'top': 0.90, 'wspace': 0.25, 'hspace': 0.25}, axis_args)
    fill_args = sc.mergedicts({'alpha': 0.2}, fill_args)
    legend_args = sc.mergedicts({'loc': 'best'}, legend_args)

    if sep_figs:
        figs = []
    else:
        fig = pl.figure(**fig_args)
    pl.subplots_adjust(**axis_args)
    pl.rcParams['font.size'] = font_size
    if font_family:
        pl.rcParams['font.family'] = font_family

    n_rows = np.ceil(len(to_plot) / n_cols)  # Number of subplot rows to have
    baseline_days = []
    for rk, reskey in enumerate(to_plot):
        otherscen_days = []
        title = scen.base_sim.results[reskey].name  # Get the name of this result from the base simulation
        if sep_figs:
            figs.append(pl.figure(**fig_args))
            ax = pl.subplot(111)
        else:
            if rk == 0:
                ax = pl.subplot(n_rows, n_cols, rk + 1)
            else:
                ax = pl.subplot(n_rows, n_cols, rk + 1, sharex=ax)

        resdata = scen.results[reskey]
        colors = sc.gridcolors(len(resdata.items()))
        scennum = 0
        for scenkey, scendata in resdata.items():

            pl.fill_between(scen.tvec, scendata.low, scendata.high, **fill_args)
            pl.plot(scen.tvec, scendata.best, label=scendata.name, c=colors[scennum], **plot_args)
            scennum += 1
            pl.title(title)
            if rk == 0:
                pl.legend(**legend_args)

            pl.grid(grid)
            if commaticks:
                sc.commaticks()

            if scen.base_sim.data is not None and reskey in scen.base_sim.data:
                data_t = np.array((scen.base_sim.data.index - scen.base_sim['start_day']) / np.timedelta64(1, 'D'))
                pl.plot(data_t, scen.base_sim.data[reskey], 'sk', **plot_args)

            # Optionally reset tick marks (useful for e.g. plotting weeks/months)
            if interval:
                xmin, xmax = ax.get_xlim()
                ax.set_xticks(pl.arange(xmin, xmax + 1, interval))

            # Set xticks as dates
            if as_dates:
                @ticker.FuncFormatter
                def date_formatter(x, pos):
                    return (scen.base_sim['start_day'] + dt.timedelta(days=x)).strftime('%b-%d')

                ax.xaxis.set_major_formatter(date_formatter)
                if not interval:
                    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # Plot interventions
        scennum = 0
        if plot_ints:
            for s, scen_name in enumerate(scen.sims):
                if scen_name.lower() != 'baseline':
                    for intervention in scen.sims[scen_name][0]['interventions']:
                        if hasattr(intervention, 'days') and isinstance(intervention, PolicySchedule):
                            otherscen_days = [day for day in intervention.days if day not in baseline_days and day not in otherscen_days]
                        elif hasattr(intervention, 'start_day'):
                            if intervention.start_day not in baseline_days and intervention.start_day not in otherscen_days and intervention.start_day != 0:
                                otherscen_days.append(intervention.start_day)
                            if intervention.end_day not in baseline_days and intervention.end_day not in otherscen_days and isinstance(intervention.end_day, int) and intervention.end_day < scen.sims[scen_name][0]['n_days']:
                                otherscen_days.append(intervention.end_day)
                        for day in otherscen_days:
                            pl.axvline(x=day, color=colors[scennum], linestyle='--')
                        #intervention.plot(scen.sims[scen_name][0], ax)
                else:
                    for intervention in scen.sims[scen_name][0]['interventions']:
                        if hasattr(intervention, 'days') and isinstance(intervention, PolicySchedule) and rk == 0:
                            baseline_days = [day for day in intervention.days if day not in baseline_days]
                        elif hasattr(intervention, 'start_day'):
                            if intervention.start_day not in baseline_days and intervention.start_day != 0:
                                baseline_days.append(intervention.start_day)
                        for day in baseline_days:
                            pl.axvline(x=day, color=colors[scennum], linestyle='--')
                        #intervention.plot(scen.sims[scen_name][0], ax)
                scennum += 1
        if y_lim:
            if reskey in y_lim.keys():
                ax.set_ylim((0, y_lim[reskey]))
                if y_lim[reskey] < 20: # kind of arbitrary limit to add decimal places so that it doesn't just plot integer ticks on small ranges
                    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))

    # Ensure the figure actually renders or saves
    if do_save:
        if fig_path is None:  # No figpath provided - see whether do_save is a figpath
            fig_path = 'covasim_scenarios.png'  # Just give it a default name
        fig_path = sc.makefilepath(fig_path)  # Ensure it's valid, including creating the folder
        pl.savefig(fig_path)

    if do_show:
        pl.show()
    else:
        pl.close(fig)

    return fig

pretty_labels = {'communication': 'Phys. dist. communication',
                 'beach0': 'Beaches closed',
                 'beach2': 'Beaches restr. to 2',
                 'beach10': 'Beaches restr. to 10',
                 'nat_parks0': 'Nat. & state parks closed ',
                 'church0': 'Places of worship closed',
                 'church_4sqm': 'Places of worship restr. 4sqm/person',
                 'cafe_restaurant0': 'Cafe & rest. takeout only',
                 'cafe_restaurant_4sqm': 'Cafe & rest. restr. 4sqm/person',
                 'pub_bar0': 'Pubs & bars closed',
                 'pub_bar_4sqm': 'Pubs & bars restr. 4sqm/person',
                 'outdoor2': 'Outdoor gath. restr. to 2',
                 'outdoor10': 'Outdoor gath. restr. to 10',
                 'outdoor200': 'Outdoor gath. restr. to 200',
                 'pSports': 'Prof. sports cancelled for players',
                 'cSports': 'Comm. sports cancelled',
                 'child_care': 'Child care closed',
                 'schools': 'Schools closed',
                 'retail': 'NE retail outlets closed',
                 'entertainment': 'Entertainment venues closed',
                 'large_events': 'Large events cancelled',
                 'NE_work': 'NE work closed',
                 'NE_health': 'NE health services closed',
                 'travel_dom': 'Interstate travel increased',
                 'social': 'Social gath. restr. to 10',
                 'comm_relax': 'Phys. dist. relaxed'
                 }
