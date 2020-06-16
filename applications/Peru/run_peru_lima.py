import user_interface as ui
import plot
import os
import utils


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Lima']
    # the name of the databook
    db_name = 'input_data_peru'
    epi_name = 'epi_data_peru'

    # country-specific parameters
    user_pars = {'Lima': {'pop_size': int(2e4),
                               'beta': 0.1,
                               'n_days': 365,
                          'pop_infected': 50}

                 }

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Lima': {'lockdown': {'beta': 0.28},
                              'heavy_lockdown': {'beta': 0.1},
                              'phase_1': {'beta': 0.15},
                              'phase_2': {'beta': 0.5},
                              'phase_3': {'beta': 0.2},
                              'phase_4': {'beta': 0.8}},
                   }
    # the policies to change during scenario runs

    policy_change = {'Lima': {'Restrictions relaxed in August': {'replace': (['heavy_lockdown'], [['phase_3']], [[150]])},
                            'Restrictions relaxed in November': {'replace': (['heavy_lockdown'], [['phase_3']], [[243]])},

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
    infections_base = sum(scens['Lima'].results['new_infections']['baseline']['best'][243:363])
    print('infections base =', infections_base)


    August_release = sum(scens['Lima'].results['new_infections']['Restrictions relaxed in August']['best'][243:363])
    print('5% of restrictions lifted in August =',August_release)
    November_release = sum(scens['Lima'].results['new_infections']['Restrictions relaxed in November']['best'][243:363])
    print('5% of restrictions lifted in November  =', November_release)

    #PLOT
    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=False, do_show=True, fig_path=dirname + '/Lima_v1' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.0},
                       to_plot=['new_infections'])

