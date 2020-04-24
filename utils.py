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
        self._baseline = baseline  #: Store baseline relative betas for each layer
        self.policies = sc.dcp(policies)  #: Store available policy interventions (name and effect)
        for policy, layer_values in self.policies.items():
            assert set(layer_values.keys()).issubset(self._baseline.keys()), f'Policy "{policy}" has effects on layers not included in the baseline'
        self.policy_schedule = []  #: Store the scheduling of policies [(start_day, end_day, policy_name)]
        self._exec_days = {}  #: Internal cache for when the beta_layer values need to be recalculated during simulation. Updated using `_update_exec_days`

    def start(self, policy_name: str, start_day: int) -> None:
        """
        Change policy start date

        If the policy is not already present, then it will be added with no end date instead
        Args:
            policy_name:
            start_day:

        Returns:

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

        self._update_exec_days()

    def end(self, policy_name: str, end_day: int) -> None:
        """
        Modify policy end date

        This only works if the policy only appears once in the schedule. If a policy gets used multiple times,
        either add the end days upfront, or insert them directly into the policy schedule. The policy should
        already appear in the schedule

        Args:
            policy_name: Name of the po
            end_day:

        Returns:

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

        self._update_exec_days()

    def add(self, policy_name: str, start_day: int, end_day: int = np.inf) -> None:
        """
        Add a policy to the schedule

        Args:
            policy_name:
            start_day:
            end_day:

        Returns:

        """
        assert policy_name in self.policies, 'Unrecognized policy'
        self.policy_schedule.append([start_day, end_day, policy_name])
        self._update_exec_days()

    def remove(self, policy_name: str) -> None:
        """
        Remove a policy from the schedule

        Args:
            policy_name:

        Returns:

        """

        self.policy_schedule = [x for x in self.policy_schedule if x[2] != policy_name]
        self._update_exec_days()

    def _update_exec_days(self) -> None:
        # This helper function updates the list of days on which policies start or stop
        # The apply() function only gets run on those days
        self._exec_days = {x[0] for x in self.policy_schedule}.union({x[1] for x in self.policy_schedule if np.isfinite(x[1])})

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
        if sim.t in self._exec_days:
            sim['beta_layer'] = self._compute_beta_layer(sim.t)
            if sim['verbose']:
                print(f"PolicySchedule: Changing beta_layer values to {sim['beta_layer']}")

    def plot(self):
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
