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
                               'beta': 0.0284,
                               'n_days': 365}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'IL': {'lockdown': {'beta': .15},
                          'lockdown_relax': {'beta': 1.}}}

    # the policies to change during scenario runs
    policy_change = {'IL': {'Restrictions re-introduced Jul-Oct': {'replace': (['lockdown_relax'], [['lockdown']], [[80 + 8 * 7, 80 + 8 * 7 + 10 * 7]])},
                            'Restrictions re-introduced Sep-Nov': {'replace': (['lockdown_relax'], [['lockdown']], [[80 + 16 * 7, 80 + 16 * 7 + 10 * 7]])}}}

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

    # plot
    scens['verbose'] = True

    dirname = os.path.dirname(__file__)
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/' + locations[0] + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.0},
                       to_plot=['new_infections'])

    infections = [sum(scens[locations[0]].results['new_infections']['Restrictions re-introduced Jul-Oct']['best'][236:356]),  # don't forget to change these dates for KZN
                  sum(scens[locations[0]].results['new_infections']['Restrictions re-introduced Sep-Nov']['best'][236:356])]
    print(infections)

    filehandler = open('runs/' + locations[0] + '.obj', 'wb')
    pickle.dump(scens, filehandler)