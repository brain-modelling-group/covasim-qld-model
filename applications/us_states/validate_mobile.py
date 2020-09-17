import user_interface as ui
import utils
import xlsxwriter
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # analysis location(s) for this analysis
    locations = ['Mobile']
    # databook names
    db_name = 'input_data_US_mobile'
    epi_name = 'epi_data_US_mobile'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Mobile': {'pop_size': int(10e4),
                            'beta': 0.1, # key calibration parameter, overwrites value in input databook `other_par` tab
                            'n_days': 147, # number of days in data series (start day = day 0; calibration: all days; validation: 2/3 days)
                            'pop_infected': 5, # initial number of people infected, may need adjustment when calibrating
                            'calibration_end': '2020-08-01'}} #for first, and run calibration: date last data entry available, for validation calibration: data series start 2020-03-08 (1st case) to end 2020-08-01, 147 days * 2/3rd data series (i.e. *0.67)= 98 days -> 2020-03-08 + 98 days= 2020-06-13 


    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,   #test = 1, run = 8
                'noise': 0.3,  #test = 0, run = 0.03
                'verbose': 0,
                'rand_seed': 1}


    # the policies to change during scenario runs
    scen_opts = {'Mobile': {

                                'No changes to current lockdown restrictions':
                                {'replace': (['relax3'], [['relax3']], [[130]])}
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
                       fig_path=dirname + '/figs_mobile/Mobile-calibration' + '.png',
                       interval=30, n_cols=2,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
                       axis_args={'left': 0.05, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])






