import user_interface as ui
import utils
import xlsxwriter
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Chicago']
    # the name of the databook
    db_name = 'input_data_US_group2'
    epi_name = 'epi_data_US_group2'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Chicago': {'pop_size': int(10e4),
                               'beta': 0.139,
                               'n_days': 370,
                               'symp_test': 100.0,
                               'calibration_end': '2020-06-30'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    # scen_opts = {'Chicago': {'No changes to current lockdown restrictions': {'replace': (['relax3'], ['relax3'], 
    #                                                     [[140]])}}}
    scen_opts = {'Chicago': {'Small easing of restrictions on August 15': 
                              {'replace': (['relax3'], [['relax4']], [[173]]),
                              'policies': {'relax4': {'beta': 0.40}}},
                 
                            'Moderate easing of restrictions on August 15': 
                              {'replace': (['relax3'], [['relax5']], [[173]]),
                              'policies': {'relax5': {'beta': 0.50}}},
                 
                            'Small easing of restrictions on July 15': 
                              {'replace': (['relax3'], [['relax4']], [[142]]),
                              'policies': {'relax4': {'beta': 0.40}}},
                 
                            'Moderate easing of restrictions on July 15': 
                              {'replace': (['relax3'], [['relax5']], [[142]]),
                              'policies': {'relax5': {'beta': 0.50}}},
                 
                            'No changes to current lockdown restrictions': 
                              {'replace': (['relax3'], [['relax3']], [[140]]),
                              'policies': {'relax3': {'beta': 0.30}}}}}
                     
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

    # Results
    population = 2706000
    extra_days = 6

    # Lower Bound: no change in restrictions
    new_inf_LB_sep_oct = sum(scens['scenarios']['Chicago'].results['new_infections']['No changes to current lockdown restrictions']['best'][(197 + extra_days):(243 + extra_days)])
    new_diag_LB_sep_oct = sum(scens['scenarios']['Chicago'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][(197 + extra_days):(243 + extra_days)])
    cum_inf_LB_sep_oct = scens['scenarios']['Chicago'].results['cum_infections']['No changes to current lockdown restrictions']['best'][(243 + extra_days)]
    incidence_LB_sep_oct = 100 * new_inf_LB_sep_oct * 30 / (46) / population
    detected_LB_sep_oct = 100 * new_diag_LB_sep_oct * 30 / (46) / population
    seroprev_LB_sep_oct = cum_inf_LB_sep_oct / population

    new_inf_LB_nov_dec = sum(scens['scenarios']['Chicago'].results['new_infections']['No changes to current lockdown restrictions']['best'][(244 + extra_days):(288 + extra_days)])
    new_diag_LB_nov_dec = sum(scens['scenarios']['Chicago'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][(244 + extra_days):(288 + extra_days)])
    cum_inf_LB_nov_dec = scens['scenarios']['Chicago'].results['cum_infections']['No changes to current lockdown restrictions']['best'][(288 + extra_days)]
    incidence_LB_nov_dec = 100 * new_inf_LB_nov_dec * 30 / (44) / population
    detected_LB_nov_dec = 100 * new_diag_LB_nov_dec * 30 / (44) / population
    seroprev_LB_nov_dec = cum_inf_LB_nov_dec / population

    # Mid Bound: small change mid- July
    new_inf_MB_sep_oct = sum(scens['scenarios']['Chicago'].results['new_infections']['Small easing of restrictions on July 15']['best'][(197 + extra_days):(243 + extra_days)])
    new_diag_MB_sep_oct = sum(scens['scenarios']['Chicago'].results['new_diagnoses']['Small easing of restrictions on July 15']['best'][(197 + extra_days):(243 + extra_days)])
    cum_inf_MB_sep_oct = scens['scenarios']['Chicago'].results['cum_infections']['Small easing of restrictions on July 15']['best'][(243 + extra_days)]
    incidence_MB_sep_oct = 100 * new_inf_MB_sep_oct * 30 / (46) / population
    detected_MB_sep_oct = 100 * new_diag_MB_sep_oct * 30 / (46) / population
    seroprev_MB_sep_oct = cum_inf_MB_sep_oct / population

    new_inf_MB_nov_dec = sum(scens['scenarios']['Chicago'].results['new_infections']['Small easing of restrictions on July 15']['best'][(244 + extra_days):(288 + extra_days)])
    new_diag_MB_nov_dec = sum(scens['scenarios']['Chicago'].results['new_diagnoses']['Small easing of restrictions on July 15']['best'][(244 + extra_days):(288 + extra_days)])
    cum_inf_MB_nov_dec = scens['scenarios']['Chicago'].results['cum_infections']['Small easing of restrictions on July 15']['best'][(288 + extra_days)]
    incidence_MB_nov_dec = 100 * new_inf_MB_nov_dec * 30 / (44) / population
    detected_MB_nov_dec = 100 * new_diag_MB_nov_dec * 30 / (44) / population
    seroprev_MB_nov_dec = cum_inf_MB_nov_dec / population

    # Upper Bound: moderate change mid-August
    new_inf_UB_sep_oct = sum(scens['scenarios']['Chicago'].results['new_infections']['Moderate easing of restrictions on August 15']['best'][(197 + extra_days):(243 + extra_days)])
    new_diag_UB_sep_oct = sum(scens['scenarios']['Chicago'].results['new_diagnoses']['Moderate easing of restrictions on August 15']['best'][(197 + extra_days):(243 + extra_days)])
    cum_inf_UB_sep_oct = scens['scenarios']['Chicago'].results['cum_infections']['Moderate easing of restrictions on August 15']['best'][(243 + extra_days)]
    incidence_UB_sep_oct = 100 * new_inf_UB_sep_oct * 30 / (46) / population
    detected_UB_sep_oct = 100 * new_diag_UB_sep_oct * 30 / (46) / population
    seroprev_UB_sep_oct = cum_inf_UB_sep_oct / population

    new_inf_UB_nov_dec = sum(scens['scenarios']['Chicago'].results['new_infections']['Moderate easing of restrictions on August 15']['best'][(244+extra_days):(288+extra_days)])
    new_diag_UB_nov_dec = sum(scens['scenarios']['Chicago'].results['new_diagnoses']['Moderate easing of restrictions on August 15']['best'][(244+extra_days):(288+extra_days)])
    cum_inf_UB_nov_dec = scens['scenarios']['Chicago'].results['cum_infections']['Moderate easing of restrictions on August 15']['best'][(288 + extra_days)]
    incidence_UB_nov_dec = 100 * new_inf_UB_nov_dec * 30 / (44) / population
    detected_UB_nov_dec = 100 * new_diag_UB_nov_dec * 30 / (44) / population
    seroprev_UB_nov_dec = cum_inf_UB_nov_dec / population

    projections = [
        ['Mid Sep – end Oct', '', '', '', '', '', '', '', '', '', '', '', 'Nov – mid Dec'],
        ['Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '', 'seroprevalence', '', '',
         'Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '', 'seroprevalence'],
        ['MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB',
         'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB'],
        [int(new_inf_MB_sep_oct), int(new_inf_LB_sep_oct), int(new_inf_UB_sep_oct),
         incidence_MB_sep_oct, incidence_LB_sep_oct, incidence_UB_sep_oct,
         int(detected_MB_sep_oct), int(detected_LB_sep_oct), int(detected_UB_sep_oct),
         seroprev_MB_sep_oct, seroprev_LB_sep_oct, seroprev_UB_sep_oct,
         int(new_inf_MB_nov_dec), int(new_inf_LB_nov_dec), int(new_inf_UB_nov_dec),
         incidence_MB_nov_dec, incidence_LB_nov_dec, incidence_UB_nov_dec,
         int(detected_MB_nov_dec), int(detected_LB_nov_dec), int(detected_UB_nov_dec),
         seroprev_MB_nov_dec, seroprev_LB_nov_dec, seroprev_UB_nov_dec]
    ]

    # Export results to Excel
    workbook = xlsxwriter.Workbook('Chicago_projections.xlsx')
    worksheet = workbook.add_worksheet('Projections')
    worksheet.add_table('A1:X4', {'data': projections, 'header_row': False})
    workbook.close()
    
    # plot cumulative deaths for calibration
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                 fig_path=dirname + '/figs/Chicago-calibrate' + '.png',
    #                 interval=30, n_cols=1,
    #                 fig_args=dict(figsize=(5, 5), dpi=100),
    #                 font_size=11,
    #                 # y_lim={'new_infections': 500},
    #                 legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
    #                 axis_args={'left': 0.15, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.15},
    #                 fill_args={'alpha': 0.3},
    #                 to_plot=['new_diagnoses', 'cum_deaths'])
    
    # plot cumulative infections to see if all the population gets infected    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path=dirname + '/figs/Chicago-projections_t' + '.png',
                        interval=30, n_cols=1,
                        fig_args=dict(figsize=(10, 8), dpi=100),
                        font_size=11,
                        # y_lim={'new_infections': 500},
                        legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -3)},
                        axis_args={'left': 0.1, 'wspace': 0.3, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
                        fill_args={'alpha': 0.3},
                        to_plot=['new_infections', 'cum_infections', 'cum_diagnoses'])