import user_interface as ui
import utils
import xlsxwriter
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Durham']
    # the name of the databook
    db_name = 'input_data_US_group1'
    epi_name = 'epi_data_US_group1'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Durham': {'pop_size': int(10e4),
                               'beta': 0.05,
                               'n_days': 120,
                                'pop_infected': 54,
                                'symp_test': 35.0,
                                'calibration_end': '2020-05-15'}}

    #future_daily = 500, av_daily = 500


    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}


    # the policies to change during scenario runs

    scen_opts = {'Durham': {'No changes to current lockdown restrictions':
                                {'replace': (['policy_1'], [['policy_3']], [[370]])}
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

    #Plot validation
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs_Durham/Durham-validate' + '.png',
                       interval=30, n_cols=2,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
                       axis_args={'left': 0.05, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])


# Results
    cum_diag_calib_end1 = scens['scenarios']['Durham'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][69]
    cum_diag_calib_1week = scens['scenarios']['Durham'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][76]
    cum_diag_calib_2week = scens['scenarios']['Durham'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][83]
    cum_diag_calib_end2 = scens['scenarios']['Durham'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][104]
    cum_death_calib_end1 = scens['scenarios']['Durham'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][69]
    cum_death_calib_1week = scens['scenarios']['Durham'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][76]
    cum_death_calib_2week = scens['scenarios']['Durham'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][83]
    cum_death_calib_end2 = scens['scenarios']['Durham'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][104]

    workbook = xlsxwriter.Workbook('Durham_validate.xlsx')
    worksheet = workbook.add_worksheet('validate')

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





