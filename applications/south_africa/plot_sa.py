import user_interface as ui
import pickle
import os
import utils

dirname = os.path.dirname(__file__)
locations = ['NW']
filehandler = open('runs/' + locations[0] + '.obj', 'rb')
scens = pickle.load(filehandler)
scens['verbose'] = True

utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True, fig_path=dirname + '/' + locations[0] + '.png',
                  interval=30,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                  axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                  fill_args={'alpha': 0.0},
                  to_plot=['new_infections'])

# infections = [sum(scens[locations[0]].results['new_infections']['Restrictions re-introduced Jul-Oct']['best'][219:311]),  # don't forget to change these dates for KZN
#               sum(scens[locations[0]].results['new_infections']['Restrictions re-introduced Sep-Nov']['best'][219:311])]
# print(infections)
#
# # ui.policy_plot(scens, outcomes_toplot={'Cumulative Deaths': 'cum_deaths'}, scens_toplot={locations[0]: ['baseline']}, plot_ints=False)
# ui.policy_plot(scens, outcomes_toplot={'New Infections': 'new_infections'}, scens_toplot={locations[0]: ['Restrictions re-introduced Jul-Oct',
#                                                                                                          'Restrictions re-introduced Sep-Nov']},
#                plot_ints=False, do_save=True, name='FS')
