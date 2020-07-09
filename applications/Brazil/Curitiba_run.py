import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)
import xlsxwriter

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Curitiba']
    # the name of the databook
    db_name = 'input_data_Brazil_FH'
    epi_name = 'epi_data_Brazil_FH'

    # Curitibaecify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-Curitibaecific parameters
    user_pars = {'Curitiba': {'pop_size': int(10e4),
                               'beta': 0.043,
                               'n_days': 289,
                               'calibration_end': '2020-07-07'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.02,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    # scen_opts = {'Curitiba': {'No changes to current lockdown restrictions': 
    scen_opts = {'Curitiba': {'Small easing of restrictions in mid-September': 
                              {'replace': (['relax1'], [['relax2']], [[181]]),
                              'policies': {'relax2': {'beta': 0.8}}},
                 
                            'Moderate easing of restrictions in mid-September': 
                              {'replace': (['relax1'], [['relax3']], [[181]]),
                              'policies': {'relax3': {'beta': 0.9}}},
                 
                            'Small easing of restrictions in mid-August': 
                              {'replace': (['relax1'], [['relax2']], [[150]]),
                              'policies': {'relax2': {'beta': 0.8}}},
                 
                            'Moderate easing of restrictions in mid-August': 
                              {'replace': (['relax1'], [['relax3']], [[150]]),
                              'policies': {'relax3': {'beta': 0.9}}},
                 
                            'No changes to current lockdown restrictions': 
                              {'replace': (['relax1'], [['relax1']], [[110]]),
                              'policies': {'relax1': {'beta': 0.7}}}}}
                     
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
    
    # plot cumulative infections to see if all the population gets infected    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path=dirname + '/figs/Curitiba-projection' + '.png',
                  interval=30, n_cols=1,
                  fig_args=dict(figsize=(10, 8), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -3)},
                  axis_args={'left': 0.1, 'wspace': 0.3, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
                  fill_args={'alpha': 0.3},
              to_plot=['new_infections', 'cum_infections', 'cum_diagnoses'])
    
    # Results
    population = 1933105
    
    # Lower Bound: no change in restrictions
    new_inf_LB_sep_oct = sum(scens['scenarios']['Curitiba'].results['new_infections']['No changes to current lockdown restrictions']['best'][181:226])    
    new_diag_LB_sep_oct = sum(scens['scenarios']['Curitiba'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][181:226])    
    cum_inf_LB_sep_oct = scens['scenarios']['Curitiba'].results['cum_infections']['No changes to current lockdown restrictions']['best'][226]    
    incidence_LB_sep_oct = 100*new_inf_LB_sep_oct*30/(226-181)/population
    detected_LB_sep_oct = 100*new_diag_LB_sep_oct*30/(226-181)/population
    seroprev_LB_sep_oct = cum_inf_LB_sep_oct/population

    new_inf_LB_nov_dec = sum(scens['scenarios']['Curitiba'].results['new_infections']['No changes to current lockdown restrictions']['best'][228:271])    
    new_diag_LB_nov_dec = sum(scens['scenarios']['Curitiba'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][228:271])    
    cum_inf_LB_nov_dec = scens['scenarios']['Curitiba'].results['cum_infections']['No changes to current lockdown restrictions']['best'][271]    
    incidence_LB_nov_dec = 100*new_inf_LB_nov_dec*30/(271-228)/population
    detected_LB_nov_dec = 100*new_diag_LB_nov_dec*30/(271-228)/population
    seroprev_LB_nov_dec = cum_inf_LB_nov_dec/population
    
    # Mid Bound: small change mid- July    
    new_inf_MB_sep_oct = sum(scens['scenarios']['Curitiba'].results['new_infections']['Small easing of restrictions in mid-August']['best'][181:226])    
    new_diag_MB_sep_oct = sum(scens['scenarios']['Curitiba'].results['new_diagnoses']['Small easing of restrictions in mid-August']['best'][181:226])    
    cum_inf_MB_sep_oct = scens['scenarios']['Curitiba'].results['cum_infections']['Small easing of restrictions in mid-August']['best'][226]    
    incidence_MB_sep_oct = 100*new_inf_MB_sep_oct*30/(226-181)/population
    detected_MB_sep_oct = 100*new_diag_MB_sep_oct*30/(226-181)/population
    seroprev_MB_sep_oct = cum_inf_MB_sep_oct/population

    new_inf_MB_nov_dec = sum(scens['scenarios']['Curitiba'].results['new_infections']['Small easing of restrictions in mid-August']['best'][228:271])    
    new_diag_MB_nov_dec = sum(scens['scenarios']['Curitiba'].results['new_diagnoses']['Small easing of restrictions in mid-August']['best'][228:271])    
    cum_inf_MB_nov_dec = scens['scenarios']['Curitiba'].results['cum_infections']['Small easing of restrictions in mid-August']['best'][271]    
    incidence_MB_nov_dec = 100*new_inf_MB_nov_dec*30/(271-228)/population
    detected_MB_nov_dec = 100*new_diag_MB_nov_dec*30/(271-228)/population
    seroprev_MB_nov_dec = cum_inf_MB_nov_dec/population
    
    # Upper Bound: moderate change mid-September    
    new_inf_UB_sep_oct = sum(scens['scenarios']['Curitiba'].results['new_infections']['Moderate easing of restrictions in mid-September']['best'][181:226])    
    new_diag_UB_sep_oct = sum(scens['scenarios']['Curitiba'].results['new_diagnoses']['Moderate easing of restrictions in mid-September']['best'][181:226])    
    cum_inf_UB_sep_oct = scens['scenarios']['Curitiba'].results['cum_infections']['Moderate easing of restrictions in mid-September']['best'][226]    
    incidence_UB_sep_oct = 100*new_inf_UB_sep_oct*30/(226-181)/population
    detected_UB_sep_oct = 100*new_diag_UB_sep_oct*30/(226-181)/population
    seroprev_UB_sep_oct = cum_inf_UB_sep_oct/population

    new_inf_UB_nov_dec = sum(scens['scenarios']['Curitiba'].results['new_infections']['Moderate easing of restrictions in mid-September']['best'][228:271])    
    new_diag_UB_nov_dec = sum(scens['scenarios']['Curitiba'].results['new_diagnoses']['Moderate easing of restrictions in mid-September']['best'][228:271])    
    cum_inf_UB_nov_dec = scens['scenarios']['Curitiba'].results['cum_infections']['Moderate easing of restrictions in mid-September']['best'][271]    
    incidence_UB_nov_dec = 100*new_inf_UB_nov_dec*30/(271-228)/population
    detected_UB_nov_dec = 100*new_diag_UB_nov_dec*30/(271-228)/population
    seroprev_UB_nov_dec = cum_inf_UB_nov_dec/population
    
    projections = [
        ['Mid Sep – end Oct', '', '', '', '', '', '', '', '', '', '', '', 'Nov – mid Dec'],
        ['Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '', 'seroprevalence', '', '',
         'Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '', 'seroprevalence'],
        ['MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB'],
        [int(new_inf_MB_sep_oct), int(new_inf_LB_sep_oct), int(new_inf_UB_sep_oct),
         incidence_MB_sep_oct, incidence_LB_sep_oct, incidence_UB_sep_oct,
         detected_MB_sep_oct, detected_LB_sep_oct, detected_UB_sep_oct,
         seroprev_MB_sep_oct, seroprev_LB_sep_oct, seroprev_UB_sep_oct,
         int(new_inf_MB_nov_dec), int(new_inf_LB_nov_dec), int(new_inf_UB_nov_dec),
         incidence_MB_nov_dec, incidence_LB_nov_dec, incidence_UB_nov_dec,
         detected_MB_nov_dec, detected_LB_nov_dec, detected_UB_nov_dec,
         seroprev_MB_nov_dec, seroprev_LB_nov_dec, seroprev_UB_nov_dec]
        ]
    
    # Export results to Excel
    workbook = xlsxwriter.Workbook('Curitiba_projections.xlsx')     
    worksheet = workbook.add_worksheet('Projections')
    worksheet.add_table('A1:X4', {'data': projections, 'header_row': False})
    workbook.close()