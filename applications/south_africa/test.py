import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)
import xlsxwriter

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['GP']
    # the name of the databook
    db_name = 'input_data_sa_FH'
    epi_name = 'epi_data_sa_FH'

    # GPecify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'GP': {'pop_size': int(10e4),
                               'beta': 0.118,
                               'n_days': 131,
                               'calibration_end': '2020-07-13'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    scen_opts = {locations[0]: {
                            'New restrictions enforced mid-July small effect, eased mid-August':
                                {'replace': (['lockdown2'], [['relax1']], [[50]])},

                            'New restrictions enforced mid-July moderate effect, eased mid-August':
                                {'replace': (['lockdown2'], [['relax2']], [[50]])}}}
                         
    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_opts,
                           user_pars=user_pars,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)
    
    # run the scenario
    scens = ui.run_scens(scens)   
    scens['verbose'] = True
    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
              fig_path=dirname + '/figs/GP-calibrate' + '.png',
              interval=30, n_cols = 2,
              fig_args=dict(figsize=(10, 5), dpi=100),
              font_size=11,
              #y_lim={'new_infections': 500},
              legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
              axis_args={'left': 0.1, 'wspace': 0.2,'right': 0.99, 'hspace': 0.4,'bottom': 0.15},
              fill_args={'alpha': 0.3},
              to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])
    
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #           fig_path=dirname + '/figs/GP-validate' + '.png',
    #           interval=30, n_cols = 2,
    #           fig_args=dict(figsize=(10, 5), dpi=100),
    #           font_size=11,
    #           #y_lim={'new_infections': 500},
    #           legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
    #           axis_args={'left': 0.08, 'wspace': 0.2,'right': 0.99, 'hspace': 0.4,'bottom': 0.15},
    #           fill_args={'alpha': 0.3},
    #           to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])
    
    
    # cum_diag_calib_end1 = scens['scenarios']['GP'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][82]    
    # cum_diag_calib_1week = scens['scenarios']['GP'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][89]    
    # cum_diag_calib_2week = scens['scenarios']['GP'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][96]    
    # cum_diag_calib_end2 = scens['scenarios']['GP'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][131]    
    # cum_death_calib_end1 = scens['scenarios']['GP'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][82]    
    # cum_death_calib_1week = scens['scenarios']['GP'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][89]    
    # cum_death_calib_2week = scens['scenarios']['GP'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][96]    
    # cum_death_calib_end2 = scens['scenarios']['GP'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][131]    
        
    # workbook = xlsxwriter.Workbook('GP_validation.xlsx')     
    # worksheet = workbook.add_worksheet('Validation')
    
    # validation = [['Cumulative Diagnoses (Projections)', '', '', '', 'Cumulative Diagnoses (Data)', '', '', '',
    #               'Cumulative Deaths (Projections)', '', '', '', 'Cumulative Deaths (Data)', '', '', ''],
    #               ['At end of calibration', 'After 1 week', 'After 2 weeks', 'At end of projection',
    #                 'At end of calibration', 'After 1 week', 'After 2 weeks', 'At end of projection',
    #                 'At end of calibration', 'After 1 week', 'After 2 weeks', 'At end of projection',
    #                 'At end of calibration', 'After 1 week', 'After 2 weeks', 'At end of projection'],
    #               [int(cum_diag_calib_end1), int(cum_diag_calib_1week), int(cum_diag_calib_2week), int(cum_diag_calib_end2),
    #               '', '', '', '',
    #               int(cum_death_calib_end1), int(cum_death_calib_1week), int(cum_death_calib_2week), int(cum_death_calib_end2)]
    #               ]
    

    # worksheet.add_table('A1:P3', {'data': validation, 'header_row': False})
    # workbook.close()