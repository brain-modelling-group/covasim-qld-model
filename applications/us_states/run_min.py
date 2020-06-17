import user_interface as ui
import plot
import os
import utils

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Minesota']
    # the name of the databook
    db_name = 'input_data_min'
    epi_name = 'epi_data_min'

    # country-specific parameters
    user_pars = {'Minesota': {'pop_size': int(7.5e4),
                               'beta': 0.1,
                               'n_days': 365,
                          'pop_infected': 300}

                 }

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Minesota': {'lockdown_1':{'beta':0.53},
                                'lockdown_2': {'beta': 0.27},
                                'relax_1': {'beta': 0.25},
                                'relax_2': {'beta': 0.2},
                   }}
    # the policies to change during scenario runs

    policy_change = {'Minesota': {'Lockdown relaxed in August': {'replace': (['relax_1'], [['relax_2']], [[365]])},
                                  'Lockdown increased in October': {'replace':(['relax_1'], [['relax_2']],[[180]])}
                                  }}
    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           policy_change=policy_change,
                           user_pars=user_pars,
                           metapars=metapars,
                           policy_vals=policy_vals)
    # run the scenarios
    scens = ui.run_scens(scens)

    #PRINT INFECTIONS IN NOV-FEB



    #PLOT
    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/Minesota_in_prog_infections' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.0},
                       to_plot=['new_infections'])

    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=False, do_show=True,
                       fig_path=dirname + '/Minesota_in_prog_deaths_calibrate' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.0},
                       to_plot=['cum_deaths'])

    August_release = sum(scens['Minesota'].results['new_infections']['Lockdown relaxed in August']['best'][243:363])
    print('restrictions lifted in August =', August_release)
    November_release = sum(scens['Minesota'].results['new_infections']['Lockdown increased in October']['best'][243:363])
    print('Lockdown increased October  =', November_release)
