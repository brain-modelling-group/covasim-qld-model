import user_interface as ui
import pickle

locations = ['FS']
filehandler = open('runs/' + locations[0] + '.obj', 'rb')
scens = pickle.load(filehandler)

infections = [sum(scens[locations[0]].results['new_infections']['Restrictions re-introduced Jul-Oct']['best'][231:323]),  # don't forget to change these dates for KZN
              sum(scens[locations[0]].results['new_infections']['Restrictions re-introduced Sep-Nov']['best'][231:323])]
print(infections)

# ui.policy_plot(scens, outcomes_toplot={'Cumulative Deaths': 'cum_deaths'}, scens_toplot={locations[0]: ['baseline']}, plot_ints=False)
ui.policy_plot(scens, outcomes_toplot={'New Infections': 'new_infections'}, scens_toplot={locations[0]: ['Restrictions re-introduced Jul-Oct',
                                                                                                         'Restrictions re-introduced Sep-Nov']}, plot_ints=False)
