import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Miami']
    # the name of the databook
    db_name = 'input_data_US_group1'
    epi_name = 'epi_data_US_group1'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Miami': {'pop_size': int(10e4),
                               'beta': 0.07,
                               'n_days': 365,
                                'pop_infected': 1800,
                                'calibration_end': '2020-06-30'}}


    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}


    # the policies to change during scenario runs

    scen_opts = {'Miami': {
                                'Small easing of restrictions on July 15':
                                    {'replace': (['policy_1'], [['policy_2']], [[132]])},

                                'Moderate easing of restrictions on July 15':
                                {'replace': (['policy_1'], [['policy_3']], [[132]])},

                                'Small easing of restrictions on August 15':
                                {'replace': (['policy_1'], [['policy_2']], [[163]])},

                                'Moderate easing of restrictions on August 15':
                                {'replace': (['policy_1'], [['policy_3']], [[163]])},

                                'No changes to current lockdown restrictions':
                                {'replace': (['policy_1'], [['policy_3']], [[370]])}
                                }}

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           user_pars=user_pars,
                           metapars=metapars,
                           scen_opts=scen_opts,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)


    # run the scenarios
    scens = ui.run_scens(scens)
    scens['verbose'] = True


    # plot cumulative deaths for calibration
    utils.policy_plot2(scens, plot_ints=False, do_save=False, do_show=True,
                    fig_path=dirname + '/Miami-calibrate' + '.png',
                    interval=30, n_cols=1,
                    fig_args=dict(figsize=(5, 5), dpi=100),
                    font_size=11,
                    # y_lim={'new_infections': 500},
                    legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
                    axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.15},
                    fill_args={'alpha': 0.3},
                    to_plot=['cum_diagnoses', 'cum_deaths'])

    # plot cumulative infections to see if all the population gets infected
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                    fig_path = dirname + '/Miami-projections_larger' + '.png',
                    interval = 30, n_cols = 1,
                    fig_args = dict(figsize=(10, 5), dpi=100),
                    font_size = 11,
                    # y_lim={'new_infections': 500},
                    legend_args = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
                    axis_args = {'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.3},
                    fill_args = {'alpha': 0.1},
                    to_plot = ['new_infections', 'cum_infections'])

    # Plot validation
    utils.policy_plot2(scens, plot_ints=False, do_save=False, do_show=True,
                       fig_path=dirname + '/Miami-validation' + '.png',
                       interval=30, n_cols=2,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
                       axis_args={'left': 0.05, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])

    remain = sum(scens['scenarios']['Miami'].results['new_infections']['No changes to current lockdown restrictions']['best'][239:359])
    print('Lockdown remains in place =', remain)
    relax_2 = sum( scens['scenarios']['Miami'].results['new_infections']['Small easing of restrictions on August 15']['best'][239:359])
    print('Small easing of restrictions on August 15  =', relax_2)
    relax_3 = sum(scens['scenarios']['Miami'].results['new_infections']['Moderate easing of restrictions on August 15'][ 'best'][239:359])
    print('Moderate easing of restrictions on August 15 =', relax_3)
    relax_4 = sum(scens['scenarios']['Miami'].results['new_infections']['Small easing of restrictions on July 15']['best'][239:359])
    print('Small easing of restrictions on July 15 =', relax_4)
    relax_5 = sum(scens['scenarios']['Miami'].results['new_infections']['Moderate easing of restrictions on July 15']['best'][239:359])
    print('Moderate easing of restrictions on July 15 =', relax_5)


    remain = scens['scenarios']['Miami'].results['cum_infections']['No changes to current lockdown restrictions']['best'][359]
    print('Lockdown remains in place =', remain)
    relax_2 = scens['scenarios']['Miami'].results['cum_infections']['Small easing of restrictions on August 15']['best'][359]
    print('Small easing of restrictions on August 15  =', relax_2)
    relax_3 = scens['scenarios']['Miami'].results['cum_infections']['Moderate easing of restrictions on August 15']['best'][359]
    print('Moderate easing of restrictions on August 15 =', relax_3)
    relax_4 = scens['scenarios']['Miami'].results['cum_infections']['Small easing of restrictions on July 15']['best'][359]
    print('Small easing of restrictions on July 15  =', relax_4)
    relax_5 = scens['scenarios']['Miami'].results['cum_infections']['Moderate easing of restrictions on July 15']['best'][359]
    print('Moderate easing of restrictions on July 15 =', relax_5)