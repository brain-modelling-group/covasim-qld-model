import user_interface as ui
import pickle

locations = ['KZN']
filehandler = open('runs/' + locations[0] + '.obj', 'rb')
scens = pickle.load(filehandler)

infections = [sum(scens[locations[0]].results['new_infections']['8 week relax']['best'][231:323]),  # don't forget to change these dates for KZN
              sum(scens[locations[0]].results['new_infections']['12 week relax']['best'][231:323]),
              sum(scens[locations[0]].results['new_infections']['16 week relax']['best'][231:323])]
print(infections)

ui.policy_plot(scens, scens_toplot={locations[0]: ['8 week relax', '12 week relax', '16 week relax']},
               outcomes_toplot={'Cumulative Deaths': 'cum_deaths', 'New Infections': 'new_infections'})
# ui.policy_plot(scens, outcomes_toplot={'Cumulative Deaths': 'cum_deaths'}, scens_toplot={locations[0]: ['8 week relax', '12 week relax', '16 week relax']})
# ui.policy_plot(scens, outcomes_toplot={'New Infections': 'new_infections'}, scens_toplot={locations[0]: ['8 week relax', '12 week relax', '16 week relax']})
# ui.policy_plot(scens, outcomes_toplot={'Cumulative Diagnoses': 'cum_diagnoses'}, scens_toplot={locations[0]: ['8 week relax', '12 week relax', '16 week relax']})
