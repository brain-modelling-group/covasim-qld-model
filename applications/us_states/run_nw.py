import user_interface as ui
import plot
import os
import utils

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Newark']
    # the name of the databook
    db_name = 'input_data_US_NY_NH_NB_NW'
    epi_name = 'epi_data_US_NY_NH_NB_NW'

    # country-specific parameters
    user_pars = {'Newark': {'pop_size': int(10e4),
                               'beta': 0.05,
                               'n_days': 365,
                                'pop_infected': 2000}

                 }

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Newark': {'lockdown': {'beta': .5},
                            'relax_1': {'beta': .236},
                            'relax_2': {'beta': .8},
                            'relax_3': {'beta': 1},
                            'relax_4': {'beta': .8},
                            'relax_5': {'beta': 1}
                   }}
    # the policies to change during scenario runs

    policy_change = {'Newark': {'Small easing of restrictions on July 15': {'replace': (['relax_1'], [['relax_2']], [[132]])},
                                'Moderate easing of restrictions on July 15': {'replace': (['relax_1'], [['relax_3']], [[132]])},
                                'Small easing of restrictions on August 15': {'replace': (['relax_1'], [['relax_4']], [[163]])},
                                'Moderate easing of restrictions on August 15': {'replace': (['relax_1'], [['relax_5']], [[163]])},
                                'No changes to current lockdown restrictions': {'replace': (['relax_1'], [['relax_2']], [[370]])}
                                       }}

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           policy_change=policy_change,
                           user_pars=user_pars,
                           metapars=metapars,
                           policy_vals=policy_vals)
    #Change sym_test
    scens['Newark'].scenarios['baseline']['pars']['interventions'][2].symp_test =90
    scens['Newark'].scenarios['Small easing of restrictions on July 15']['pars']['interventions'][2].symp_test = 90
    scens['Newark'].scenarios['Moderate easing of restrictions on July 15']['pars']['interventions'][2].symp_test = 90
    scens['Newark'].scenarios['Small easing of restrictions on August 15']['pars']['interventions'][2].symp_test = 90
    scens['Newark'].scenarios['Moderate easing of restrictions on August 15']['pars']['interventions'][2].symp_test = 90
    scens['Newark'].scenarios['No changes to current lockdown restrictions']['pars']['interventions'][2].symp_test = 90

    # run the scenarios
    scens = ui.run_scens(scens)

    #PRINT INFECTIONS IN NOV-FEB



    #PLOT
    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/Newark_in_prog_infections_year_long' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.3},
                       fill_args={'alpha': 0.0},
                       to_plot=['new_infections'])

    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/Newark_in_prog_deaths_calibrate_year_long_2606' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.3},
                       fill_args={'alpha': 0.0},
                       to_plot=['cum_deaths'])

    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/Newark_diagnosed_calibrate_year_long_2606' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.3},
                       fill_args={'alpha': 0.0},
                       to_plot=['new_diagnoses'])

    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True, fig_path=dirname + '/newark_multiplot_2606' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 10), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.4)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.0},
                       to_plot=['new_infections', 'cum_infections'])

    remain = sum(scens['Newark'].results['new_infections']['No changes to current lockdown restrictions']['best'][241:361])
    print('Lockdown remains in place =', remain)
    relax_2 = sum(scens['Newark'].results['new_infections']['Small easing of restrictions on July 15']['best'][241:361])
    print('Lockdown relax July small  =', relax_2)
    relax_3 = sum(scens['Newark'].results['new_infections']['Moderate easing of restrictions on July 15']['best'][241:361])
    print('Lockdown relax July moderate =', relax_3)
    relax_4 = sum(scens['Newark'].results['new_infections']['Small easing of restrictions on August 15']['best'][241:361])
    print('Lockdown relax August small  =', relax_4)
    relax_5 = sum(scens['Newark'].results['new_infections']['Moderate easing of restrictions on August 15']['best'][241:361])
    print('Lockdown relax August Moderate =', relax_5)

