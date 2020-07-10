import user_interface as ui
import utils
import pickle

# Sympt_test = 8

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Columbus']
    # the name of the databook
    db_name = 'input_data_US_Boston'
    epi_name = 'epi_data_US_cities_Boston_Birmingham'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Columbus': {'pop_size': int(10e4),
                             'beta': 0.11,
                             'pop_infected': 5,
                             'n_days': 380,
                                'calibration_end': '2020-06-27'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 6,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}

    scen_opts = {'Columbus': {'No changes to current lockdown restrictions': {'replace': (['relax2'], [['relax2']], [[140]])},
                            'Small easing of restrictions on August 1': {'replace': (['relax2'], [['relax3']], [[158]])},
                            'Moderate easing of restrictions on August 1': {'replace': (['relax2'], [['relax4']], [[158]])},
                            'Small easing of restrictions on July 15': {'replace': (['relax2'], [['relax3']], [[142]])},
                            'Moderate easing of restrictions on July 15': {'replace': (['relax2'], [['relax4']], [[142]])},
                            }}

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_opts,
                           user_pars=user_pars,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)

    # run the scenarios
    scens = ui.run_scens(scens)
    scens['verbose'] = True

    # # Print number of new infections
    # print('New Infections Nov-Feb')
    # October1_10release = sum(scens['scenarios']['Columbus'].results['new_infections']['Small easing of restrictions on August 1']['best'][251:370])
    # print('Small easing of restrictions on August 1 =', October1_10release)
    # no_release = sum(scens['scenarios']['Columbus'].results['new_infections']['No changes to current lockdown restrictions']['best'][251:370])
    # print('No changes to current lockdown restrictions =', no_release)
    # October1_40release = sum(scens['scenarios']['Columbus'].results['new_infections']['Moderate easing of restrictions on August 1']['best'][251:370])
    # print('Moderate easing of restrictions on August 1 =', October1_40release)
    # September1_10release = sum(scens['scenarios']['Columbus'].results['new_infections']['Small easing of restrictions on July 15']['best'][251:370])
    # print('Small easing of restrictions on July 15 =', September1_10release)
    # September1_40release = sum(scens['scenarios']['Columbus'].results['new_infections']['Moderate easing of restrictions on July 15']['best'][251:370])
    # print('Moderate easing of restrictions on July 15 =', September1_40release)
    #
    # # Print estimated seroprevalence
    # print('Seroprevalence end of Feb 2021')
    # October1_10release = scens['scenarios']['Columbus'].results['cum_infections']['Small easing of restrictions on August 1']['best'][370]/892533
    # print('Small easing of restrictions on August 1 =', October1_10release)
    # no_release = scens['scenarios']['Columbus'].results['cum_infections']['No changes to current lockdown restrictions']['best'][370]/892533
    # print('No changes to current lockdown restrictions =', no_release)
    # October1_40release = scens['scenarios']['Columbus'].results['cum_infections']['Moderate easing of restrictions on August 1']['best'][370]/892533
    # print('Moderate easing of restrictions on August 1 =', October1_40release)
    # September1_10release = scens['scenarios']['Columbus'].results['cum_infections']['Small easing of restrictions on July 15']['best'][370]/892533
    # print('Small easing of restrictions on July 15 =', September1_10release)
    # September1_40release = scens['scenarios']['Columbus'].results['cum_infections']['Moderate easing of restrictions on July 15']['best'][370]/892533
    # print('Moderate easing of restrictions on July 15 =', September1_40release)

    import os
    dirname = os.path.dirname(__file__)

    # # Validation Plots
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                    fig_path=dirname + '/figs_' + locations[0] + '/validate' + '.png',
    #                    interval=30, n_cols=2,
    #                    fig_args=dict(figsize=(10, 5), dpi=100),
    #                    font_size=11,
    #                    # y_lim={'new_infections': 500},
    #                    legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
    #                    axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
    #                    fill_args={'alpha': 0.3},
    #                    to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])

    # # Calibration Plots
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                    fig_path=dirname + '/figs_' + locations[0] + '/calibration' + '.png',
    #                    interval=30, n_cols=2,
    #                    fig_args=dict(figsize=(10, 5), dpi=100),
    #                    font_size=11,
    #                    # y_lim={'new_infections': 500},
    #                    legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
    #                    axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
    #                    fill_args={'alpha': 0.3},
    #                    to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])

    # Projection Plots
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs_' + locations[0] + '/projection' + '.png',
                       interval=30, n_cols=1,
                       fig_args=dict(figsize=(10, 8), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -3)},
                       axis_args={'left': 0.1, 'wspace': 0.3, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses'])

    filehandler = open('runs/' + locations[0] + '.obj', 'wb')
    pickle.dump(scens, filehandler)
