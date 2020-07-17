import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)
import xlsxwriter

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Rio']
    # the name of the databook
    db_name = 'input_data_Brazil'
    epi_name = 'epi_data_Brazil'

    # Rioecify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-Rioecific parameters
    user_pars = {'Rio': {'pop_size': int(10e4),
                               'beta': 0.0935,
                               'n_days': 130,
                               'calibration_end': '2020-05-20'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    scen_opts = {'Rio': {'No changes to current lockdown restrictions': 
                             {'replace': (['relax2'], ['relax2'], [[107]]),
                              'policies': {'relax2': {'beta': 0.6}}}}}
                         
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
    
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #           fig_path=dirname + '/figs/Rio-calibrate' + '.png',
    #           interval=30, n_cols = 2,
    #           fig_args=dict(figsize=(10, 5), dpi=100),
    #           font_size=11,
    #           #y_lim={'new_infections': 500},
    #           legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
    #           axis_args={'left': 0.08, 'wspace': 0.2,'right': 0.99, 'hspace': 0.4,'bottom': 0.15},
    #           fill_args={'alpha': 0.3},
    #           to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])
    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
              fig_path=dirname + '/figs/Rio-validate' + '.png',
              interval=30, n_cols = 2,
              fig_args=dict(figsize=(10, 5), dpi=100),
              font_size=11,
              #y_lim={'new_infections': 500},
              legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
              axis_args={'left': 0.1, 'wspace': 0.2,'right': 0.99, 'hspace': 0.4,'bottom': 0.15},
              fill_args={'alpha': 0.3},
              to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])
    
    
    cum_diag_calib_end1 = scens['scenarios']['Rio'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][83]    
    cum_diag_calib_1week = scens['scenarios']['Rio'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][90]    
    cum_diag_calib_2week = scens['scenarios']['Rio'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][97]    
    cum_diag_calib_end2 = scens['scenarios']['Rio'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][128]    
    cum_death_calib_end1 = scens['scenarios']['Rio'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][83]    
    cum_death_calib_1week = scens['scenarios']['Rio'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][90]    
    cum_death_calib_2week = scens['scenarios']['Rio'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][97]    
    cum_death_calib_end2 = scens['scenarios']['Rio'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][128]    
        
    workbook = xlsxwriter.Workbook('Rio_validation.xlsx')     
    worksheet = workbook.add_worksheet('Validation')
    
    validation = [['Cumulative Diagnoses (Projections)', '', '', '', 'Cumulative Diagnoses (Data)', '', '', '',
                  'Cumulative Deaths (Projections)', '', '', '', 'Cumulative Deaths (Data)', '', '', ''],
                  ['At end of calibration', 'After 1 week', 'After 2 weeks', 'At end of projection',
                    'At end of calibration', 'After 1 week', 'After 2 weeks', 'At end of projection',
                    'At end of calibration', 'After 1 week', 'After 2 weeks', 'At end of projection',
                    'At end of calibration', 'After 1 week', 'After 2 weeks', 'At end of projection'],
                  [int(cum_diag_calib_end1), int(cum_diag_calib_1week), int(cum_diag_calib_2week), int(cum_diag_calib_end2),
                  '', '', '', '',
                  int(cum_death_calib_end1), int(cum_death_calib_1week), int(cum_death_calib_2week), int(cum_death_calib_end2)]
                  ]
    

    worksheet.add_table('A1:P3', {'data': validation, 'header_row': False})
    workbook.close()