import user_interface as ui
from utils import policy_plot2
import os

if __name__ == "__main__":
    dirname = os.path.dirname(__file__)
    locations = ['Victoria']  # the list of locations for this analysis
    db_name = 'input_data_Australia'  # the name of the databook
    epi_name = 'epi_data_Australia'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events', 'child_care', 'social']
    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Victoria': {'pop_size': int(5e4),
                              'beta': 0.05,
                              'n_days': 200,
                              'calibration_end': '2020-07-06'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0.0,
                'verbose': 1,
                'rand_seed': 1}

    # Pub app scenarios
    scen_base = {'Victoria': {'baseline': {'replace': (['lockdown', 'pub_bar0', 'cafe_restaurant0', 'outdoor2', 'church'],
                                                       [['lockdown_relax'], ['pub_bar_4sqm'], ['cafe_restaurant_4sqm'],
                                                        ['outdoor10'], ['church_4sqm']],
                                                       [[93], [93], [93], [93], [114]]),
                                           'turn_off': (['schools', 'social', 'retail', 'nat_parks0', 'beach0', 'NE_health'],
                                                        [87, 74, 74, 74, 74, 58]),
                                           'tracing_policies': {'tracing_app': {'coverage': [0, 0.1], 'days': [0, 60]},
                                                                'id_checks': {'coverage': [0, 0.8], 'days': [0, 93]}}},
                              }
                 }
    # https: // www.dhhs.vic.gov.au / coronavirus / updates
    # 15 March: internaitonal borders closed
    # 19 March: 4 sqm rule, entertainment, large events
    # 22 March: take away only
    # 29 March: stage 3 (only 4 reasons to leave home)
    # 27 April [58]: elective surgery
    # 13 May [74]: small social gatherings https://www.abc.net.au/news/2020-05-11/coronavirus-victoria-eases-restrictions-the-new-covid-19-rules/12233798
    # 26 May [87]: students go to class
    # 1 June [93]: restaurants, cafes, and other hospitality businesses to resume dine-in service <20 ppl
    # 22 June [114]: social events, ceremonies, community services, U18 sports start sport and exercise. libraries, community centres and halls will be able to open to 50 people
    # 1 July [123]: 10 postcodes lockdown
    # 4 July [123]: 2 more postcodes locked down
    # 4 July [123]: lockdown of public housing
    # July 1 Gyms https://sport.vic.gov.au/our-work/return-to-play/return-to-play-for-community-sport-and-active-recreation

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_base,
                           user_pars=user_pars,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)

    # run the scenarios
    scens = ui.run_scens(scens)

    # ui.policy_plot(scens)

    policy_plot2(scens, plot_ints=True, plot_base=True, do_save=True, do_show=True,
                 fig_path=dirname + '/vic_test' + '.png',
                 interval=30, n_cols=2,
                 fig_args=dict(figsize=(10, 5), dpi=100), font_size=11,
                 # y_lim={'new_infections': 500},
                 legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
                 axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
                 fill_args={'alpha': 0.3},
                 to_plot=['new_infections', 'cum_diagnoses', 'new_diagnoses', 'cum_deaths'])
