import user_interface as ui
from utils import policy_plot2
import os
import outbreak
import contacts as co
import covasim as cv
import policy_updates
import utils
import sciris as sc
import pandas as pd


# GENERAL PLAN
# - Consider 9th July, the date of the new policies, as the critical date
# - Prior to 9th July
start_day_relative_to_jul_9 = -40 # Start this many days beforehand
n_days = 14-start_day_relative_to_jul_9

params = outbreak.load_australian_parameters('Victoria', pop_size=5e4, pop_infected=0, n_days=n_days)
params.pars["n_imports"] = 0 # Number of imports per day

people, popdict = co.make_people(params)

# setup simulation for this location
sim = cv.Sim(pars=params.pars,
             datafile=None,
             popfile=people,
             pop_size=params.pars['pop_size'],
             load_pop=True,
             save_pop=False)

interventions = []

# ADD DYNAMIC LAYERS INTERVENTION
interventions.append(policy_updates.UpdateNetworks(layers=params.dynamic_lkeys, contact_numbers=params.pars['contacts'], popdict=popdict))

# SET BETA POLICIES
beta_schedule = policy_updates.PolicySchedule(params.pars["beta_layer"], params.policies['beta_policies'])
# Policies before 9th July
# beta_schedule.start('lockdown_relax', 0) # Lockdown-relax currently has no
beta_schedule.start('church_4sqm', 0)
beta_schedule.start('cafe_restaurant_4sqm', 0)
beta_schedule.start('pub_bar_4sqm', 0)
beta_schedule.start('outdoor200', 0)
beta_schedule.start('large_events', 0)

# Add these on 9th July
beta_schedule.start('cSports', -start_day_relative_to_jul_9)
beta_schedule.start('entertainment', -start_day_relative_to_jul_9)

# Replace these on 9th July
beta_schedule.end('cafe_restaurant_4sqm', -start_day_relative_to_jul_9)
beta_schedule.start('cafe_restaurant0', -start_day_relative_to_jul_9)
beta_schedule.end('pub_bar_4sqm', -start_day_relative_to_jul_9)
beta_schedule.start('pub_bar0', -start_day_relative_to_jul_9)
beta_schedule.end('outdoor200', -start_day_relative_to_jul_9)
beta_schedule.start('outdoor2', -start_day_relative_to_jul_9)

interventions.append(beta_schedule)

# ADD CLIPPING POLICIES - Only NE_work is active
interventions.append(cv.clip_edges(days=0, layers=params.policies['clip_policies']['NE_work']['layers'], changes=params.policies['clip_policies']['NE_work']['change']))

# # ADD TESTING INTERVENTION
# interventions.append(cv.test_num(
#     daily_tests=params.extrapars["future_daily_tests"],
#     symp_test=params.extrapars['symp_test'],
#     quar_test=params.extrapars['quar_test'],
#     sensitivity=params.extrapars['sensitivity'],
#     test_delay=params.extrapars['test_delay'],
#     loss_prob=params.extrapars['loss_prob']))
#
# interventions.append(cv.test_prob(
#     symp_prob=symp_prob,
#     asymp_prob=asymp_prob,
#     symp_quar_prob=symp_quar_prob,
#     asymp_quar_prob=asymp_quar_prob,
# ))


# ADD TRACING INTERVENTION
interventions.append(cv.contact_tracing(trace_probs=params.extrapars['trace_probs'],
                                        trace_time=params.extrapars['trace_time'],
                                        start_day=0))
tracing_app, id_checks = policy_updates.make_tracing(trace_policies=params.policies["tracing_policies"])
if tracing_app is not None:
    interventions.append(tracing_app)
if id_checks is not None:
    interventions.append(id_checks)

sim.pars['interventions'] = interventions

# Now when we run the model, the major free parameters are the overall beta
# And the date of the seed infection
sim.pars['beta'] = 0.065
seed_day = 2
sim.pars['interventions'].append(utils.SeedInfection({seed_day: 1}))

# Add testing interventions
sim.pars['interventions'].append(cv.test_prob(
    symp_prob=0.05,
    asymp_prob=0.005,
    symp_quar_prob=0.2,
    asymp_quar_prob=0.01,
    start_day=0,
    end_day=20,
))
sim.pars['interventions'].append(cv.test_prob(
    symp_prob=0.05,
    asymp_prob=0.005,
    symp_quar_prob=0.2,
    asymp_quar_prob=0.01,
    start_day=21,
))

from outbreak.celery import run_multi_sim

def analyzer(s):
    return s.results

results = run_multi_sim(sim,4, analyzer=analyzer)


# Plot the results, aligned to our assumed start date
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
for result in results:
    plt.plot(result['t'], result['cum_diagnoses'], color='b', alpha=0.05)

# plt.plot(s2[0]['t'], s2[0]['cum_infections'])

cases = pd.read_csv('new_cases.csv',parse_dates=['Date'])
cases['day'] = (cases['Date']-pd.to_datetime('2020-07-09')).dt.days # Get day index relative to start day of 18th June
cases.set_index('day',inplace=True)
cases = cases.loc[cases.index>=start_day_relative_to_jul_9]['vic'].astype(int).cumsum()
plt.scatter(cases.index-start_day_relative_to_jul_9,cases.values,color='k')
plt.title('Cumulative cases')


import matplotlib.pyplot as plt
fig, ax = plt.subplots()
for result in results:
    plt.plot(result['t'], result['new_tests'], color='r', alpha=0.05)

# plt.plot(s2[0]['t'], s2[0]['cum_infections'])

tests = pd.read_csv('new_tests.csv',parse_dates=['Date'])
tests['day'] = (tests['Date']-pd.to_datetime('2020-07-09')).dt.days # Get day index relative to start day of 18th June
tests.set_index('day',inplace=True)
tests = tests.loc[tests.index>=start_day_relative_to_jul_9]['vic'].replace('-', None, regex=True).astype(int)
tests = tests*sim.n/4.9e6  # Approximately scale to number of simulation agents
plt.scatter(tests.index-start_day_relative_to_jul_9,tests.values,color='k')
plt.title('Daily tests')

# assert style in {'samples', 'quartile', 'ci', 'std'}
#
# if not self.samples:
#     raise Exception('Cannot plot samples because no samples have been added yet')
# results = sc.promotetolist(results) if results is not None else self.results
# outputs = sc.promotetolist(outputs) if outputs is not None else self.outputs
# pops = sc.promotetolist(pops) if pops is not None else self.pops
#
# if fig is None:
#     fig = plt.figure()
# ax = plt.gca()
#
# series_lookup = self._get_series()
#
# for result in results:
#     for output in outputs:
#         for pop in pops:
#
#             these_series = series_lookup[result, pop, output]
#             vals = np.vstack([x.vals.ravel() for x in these_series])  # Turn samples into a matrix
#
#             if self.baseline:
#                 baseline_series = self.baseline[result, pop, output]
#                 plt.plot(baseline_series.tvec, baseline_series.vals, color=baseline_series.color, label='%s: %s-%s-%s (baseline)' % (self.name, result, pop, output))[0]
#             else:
#                 plt.plot(these_series[0].tvec, np.mean(vals, axis=0), color=these_series[0].color, linestyle='dashed', label='%s: %s-%s-%s (mean)' % (self.name, result, pop, output))[0]
#
#             if style == 'samples':
#                 for series in these_series:
#                     plt.plot(series.tvec, series.vals, color=series.color, alpha=0.05)
#
#             elif style == 'quartile':
#                 ax.fill_between(these_series[0].tvec, np.quantile(vals, 0.25, axis=0), np.quantile(vals, 0.75, axis=0), alpha=0.15, color=these_series[0].color)
#             elif style == 'ci':
#                 ax.fill_between(these_series[0].tvec, np.quantile(vals, 0.025, axis=0), np.quantile(vals, 0.975, axis=0), alpha=0.15, color=these_series[0].color)
#             elif style == 'std':
#                 if self.baseline:
#                     ax.fill_between(baseline_series.tvec, baseline_series.vals - np.std(vals, axis=0), baseline_series.vals + np.std(vals, axis=0), alpha=0.15, color=baseline_series.color)
#                 else:
#                     ax.fill_between(these_series[0].tvec, np.mean(vals, axis=0) - np.std(vals, axis=0), np.mean(vals, axis=0) + np.std(vals, axis=0), alpha=0.15, color=these_series[0].color)
#             else:
#                 raise Exception('Unknown style')
#
#     proposed_label = "%s (%s)" % (output, these_series[0].unit_string)
#     if ax.yaxis.get_label().get_text():
#         assert proposed_label == ax.yaxis.get_label().get_text(), 'The outputs being superimposed have different units'
#     else:
#         ax.set_ylabel(proposed_label)
#
# ax.set_xlabel('Year')
# if legend:
#     ax.legend()
# return fig