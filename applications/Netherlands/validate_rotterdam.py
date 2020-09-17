import user_interface as ui
import utils
import xlsxwriter
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # analysis location(s) for this analysis
    locations = ['Rotterdam']
    # databook names
    db_name = 'input_data_NLD'
    epi_name = 'epi_data_NLD'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Rotterdam': {'pop_size': int(10e4),
                            'beta': 0.08, # key calibration parameter, overwrites value in input databook `other_par` tab
                            'n_days': 155, # number of days in data series (validation: 2/3 days)
                            'pop_infected': 200, # number cases day 0, may need adjustment
                            'calibration_end': '2020-08-06'}} # data series end date
    
    metapars = {'n_runs': 8,   #test = 1, run = 8
                'noise': 0.1, #test = 0, run = 0.03
                'verbose': 1,
                'rand_seed': 1}

    # the policies to change during scenario runs
    scen_opts = {'Rotterdam': {
                                'No changes to current lockdown restrictions':
                                {'replace': (['relax3'], [['relax3']], [[122]])}
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

    # Plot validation
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs_rotterdam/Rotterdam-calibration1' + '.png',
                       interval=30, n_cols=2,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
                       axis_args={'left': 0.05, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])






