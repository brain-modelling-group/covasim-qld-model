import user_interface as ui
import utils
import os
import pickle

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['IL']
    # the name of the databook
    db_name = 'input_data_il'
    epi_name = 'epi_data_il'

    # country-specific parameters
    user_pars = {'IL': {'pop_size': int(10e4),
                               'beta': 0.225,
                               'n_days': 90}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'IL': {'pre-lockdown': {'beta': 1.},
                          'lockdown': {'beta': .15},
                          'lockdown_relax': {'beta': 0.17}}}

    # the policies to change during scenario runs
    policy_change = {'IL': {'Restrictions re-introduced Jul-Oct': {'replace': (
        ['lockdown_relax'], [['lockdown']], [[80 + 12 * 7, 80 + 12 * 7 + 10 * 7]])}}}

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
    # ui.policy_plot(scens, outcomes_toplot={'Cumulative Deaths': 'cum_deaths'})
    # ui.policy_plot(scens, outcomes_toplot={'New Infections': 'new_infections'})

    # plot
    scens['verbose'] = True

    dirname = os.path.dirname(__file__)
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs/' + locations[0] + '_deaths.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.0},
                       to_plot=['cum_deaths'])

    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs/' + locations[0] + '_infections.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.0},
                       to_plot=['new_infections'])

    filehandler = open('runs/' + locations[0] + '.obj', 'wb')
    pickle.dump(scens, filehandler)
