import sciris as sc
import covasim as cv
import numpy as np
import matplotlib.pyplot as plt


class PolicySchedule(cv.Intervention):
    def __init__(self, policies):
        self._baseline = dict(H=1, S=1, W=1, C=1, Church=1, pSport=1)
        self.policies = sc.dcp(policies) # Dict keyed by {policy_name: {'H':1, 'S':0.75}}
        self.policy_schedule = [] # Store policies as tuple of (start_day, end_day, Policy)
        self._exec_days = {}

    def start(self, policy_name:str, start_day:int):
        """
        Modify policy start date

        Use this
        Args:
            policy_name:
            start_day:

        Returns:

        """
        n_entries = len([x for x in self.policy_schedule if x[2] == policy_name])
        if n_entries < 1:
            raise Exception('Cannot start a policy that is not already scheduled - use PolicySchedule.add() instead')
        elif n_entries > 1:
            raise Exception('start_policy() cannot be used to start a policy that appears more than once - need to manually add an end day to the desired instance')

        for entry in self.policy_schedule:
            if entry[2] == policy_name:
                entry[0] = start_day

        self._update_exec_days()

    def end(self, policy_name:str, end_day:int):
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

        n_entries = len([x for x in self.policy_schedule if x[2]==policy_name])
        if n_entries <1:
            raise Exception('Cannot end a policy that is not already scheduled - use PolicySchedule.add() instead')
        elif n_entries > 1:
            raise Exception('end_policy() cannot be used to end a policy that appears more than once - need to manually add an end day to the desired instance')

        for entry in self.policy_schedule:
            if entry[2]==policy_name:
                entry[1] = end_day

        self._update_exec_days()

    def add(self, policy_name:str, start_day:int, end_day:int=np.inf):
        """
        Add a policy to the schedule

        Args:
            policy_name:
            start_day:
            end_day:

        Returns:

        """
        self.policy_schedule.append([start_day, end_day, policy_name])
        self._update_exec_days()

    def _update_exec_days(self):
        # This helper function updates the list of days on which policies start or stop
        # The apply() function only gets run on those days
        self._exec_days = {x[0] for x in self.policy_schedule}.union({x[1] for x in self.policy_schedule if np.isfinite(x[1])})

    def _compute_beta_layer(self, t):
        # Compute beta_layer at a given point in time
        # The computation is done from scratch each time
        beta_layer = self._baseline.copy()
        for start_day, end_day, policy_name in self.policy_schedule:
            rel_betas = self.policies[policy_name]
            if t >= start_day and t<end_day:
                for layer in beta_layer:
                    if layer in rel_betas:
                        beta_layer[layer] *= rel_betas[layer]
        return beta_layer

    def apply(self, sim):
        if sim.t in self._exec_days:
            sim['beta_layer'] = self._compute_beta_layer(sim.t)
            print(sim['beta_layer'])

    def plot(self):
        """
        Plot policy schedule as Gantt chart

        Returns: A matplotlib figure with a Gantt chart

        """
        fig, ax = plt.subplots()
        max_time = np.nanmax(np.array([x[0] for x in self.policy_schedule] + [x[1] for x in self.policy_schedule if np.isfinite(x[1])]))
        ax.set_yticks(np.arange(len(self.policies)))
        ax.set_yticklabels(list(self.policies.keys()))
        ax.set_ylim(0-0.5, len(self.policies)-0.5)
        ax.set_xlim(0, max_time+5) # Extend a few days so the ends of policies can be seen
        ax.set_xlabel('Days')

        policy_index = {x:i for i,x in enumerate(self.policies.keys())}

        colors = sc.gridcolors(len(self.policies))
        for start_day, end_day, policy_name in self.policy_schedule:
            if not np.isfinite(end_day):
                end_day = 1e6 # Arbitrarily large end day
            ax.broken_barh([(start_day, end_day-start_day)], (policy_index[policy_name]-0.5, 1),color=colors[policy_index[policy_name]])

        return fig

