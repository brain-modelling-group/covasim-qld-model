import user_interface as ui
from utils import policy_plot2
import os


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Victoria']
    # the name of the databook
    db_name = 'input_data_Australia'
    epi_name = 'epi_data_Australia'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C', 'church','pSport','cSport','beach','entertainment','cafe_restaurant','pub_bar',
                 'transport','national_parks','public_parks','large_events','child_care','social','aged_care']
    dynamic_lkeys = ['C','beach','entertainment','cafe_restaurant','pub_bar',
                 'transport','national_parks','public_parks','large_events']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Victoria': {'pop_size': int(2e4),
                               'beta': 0.06,
                               'n_days': 150,
                               'calibration_end': '2020-03-15'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 2,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

#Pub app scenarios
    scen_base = {'Victoria': {'Base': {'replace': (['lockdown'], [['lockdown_relax']], [[60]])}}}

    scen_pub_app = {'Victoria': {'Open pubs with no app': {'replace':  (['lockdown'], [['lockdown_relax']], [[60]]),
                                                           'turn_on': (['import_cases'],[60]),
                                                        'turn_off': (['pub_bar0'],[60])}}}#,
                             # 'Open pubs with 40% app': {'replace': (['lockdown'], [['lockdown_relax']], [[60]]),
                             #                            'turn_off': (['pub_bar0'], [60]),
                             #                      'tracing_policies': {'tracing_app': {'coverage': [0,0.4], 'days': [0,60]}}},
                             # 'Open pubs with 70% app': {'replace': (['lockdown'], [['lockdown_relax']], [[60]]),
                             #                            'turn_off': (['pub_bar0'], [60]),
                             #                        'tracing_policies': {'tracing_app': {'coverage': [0,0.7], 'days': [0,60]}}}}}

    scen_pub_distancing = {'Victoria': {'Open pubs with no distancing': {'replace':  (['lockdown'], [['lockdown_relax']], [[60]]),
                                                        'turn_off': (['pub_bar0'],[60])}},
                             'Open pubs with 20% distancing': {'replace': (['lockdown', 'pub_bar0'],
                                                                            [['lockdown_relax'],['pub_bar_4sqm']],
                                                                            [[60],[60]]),
                                                  'policies': {'pub_bar_4sqm': {'pub_bar': 0.8}}},
                             'Open pubs with 60% distancing': {'replace': (['lockdown', 'pub_bar0'],
                                                                            [['lockdown_relax'], ['pub_bar_4sqm']],
                                                                            [[60], [60]]),
                                                    'policies': {'pub_bar_4sqm': {'pub_bar': 0.4}}}}

    scen_pub_IDs = {'Victoria': {'Open pubs': {'replace': (['lockdown'], [['lockdown_relax']], [[60]]),
                                                           'turn_off': (['pub_bar0'], [60])},
                                 'Open pubs with 40% ID checks': {'replace': (['lockdown'], [['lockdown_relax']], [[60]]),
                                                            'turn_off': (['pub_bar0'], [60]),
                                                            'id_checks': {'coverage': [0,0.4], 'days': [0, 60]}},
                                 'Open pubs with 80% ID checks': {'replace': (['lockdown'], [['lockdown_relax']], [[60]]),
                                                            'turn_off': (['pub_bar0'], [60]),
                                                            'id_checks': {'coverage': [0, 0.8], 'days': [0, 60]}}}}

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_pub_app,
                           user_pars=user_pars,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)
    # run the scenarios
    scens = ui.run_scens(scens)

    #ui.policy_plot(scens)

    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    dirname = os.path.dirname(__file__)
    scens['verbose'] = True

    policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/vic_test' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       y_lim={'new_diagnoses': 200},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections','new_diagnoses','cum_deaths'])
