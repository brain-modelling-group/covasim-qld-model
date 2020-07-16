import user_interface as ui
import utils
import os

dirname = os.path.dirname(__file__)
import xlsxwriter

# symp_test =

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['KZN']
    # the name of the databook
    db_name = 'input_data_sa'
    epi_name = 'epi_data_sa_KZN'

    # Manausecify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-Manausecific parameters
    user_pars = {locations[0]: {'pop_size': int(10e4),
                            'beta': 0.16,
                            'n_days': 320,
                            'calibration_end': '2020-07-14'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 6,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}

    # the policies to change during scenario runs
    scen_opts = {locations[0]: {
                            'New restrictions enforced mid-July small effect, eased mid-August':
                                {'replace': (['lockdown_v2'], [['lockdown_s3_v2']], [[163]])},

                            'New restrictions enforced mid-July moderate effect, eased mid-August':
                                {'replace': (['lockdown_v2'], [['lockdown_s3_v2']], [[163]])},

                            'New restrictions enforced mid-July small effect, eased mid-September':
                                {'replace': (['lockdown_v2'], [['lockdown_s3_v2']], [[194]])},

                            'New restrictions enforced mid-July moderate effect, eased mid-September':
                                {'replace': (['lockdown_v2'], [['lockdown_s3_v2']], [[194]])},

                            'New restrictions moderate effect, never released':
                                {'replace': (['lockdown_v2'], [['lockdown_s3_v2']], [[500]])}}}

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_opts,
                           user_pars=user_pars,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)

    small = 0.1
    mod = 0.05
    scens['scenarios'][locations[0]].scenarios['New restrictions enforced mid-July small effect, eased mid-August']['pars']['interventions'][0].policies['lockdown_v2'] = \
        {'H': small, 'S': small, 'W': small, 'C': small}
    scens['scenarios'][locations[0]].scenarios['New restrictions enforced mid-July small effect, eased mid-September']['pars']['interventions'][0].policies['lockdown_v2'] = \
        {'H': small, 'S': small, 'W': small, 'C': small}
    scens['scenarios'][locations[0]].scenarios['New restrictions enforced mid-July moderate effect, eased mid-August']['pars']['interventions'][0].policies['lockdown_v2'] = \
        {'H': mod, 'S': mod, 'W': mod, 'C': mod}
    scens['scenarios'][locations[0]].scenarios['New restrictions enforced mid-July moderate effect, eased mid-September']['pars']['interventions'][0].policies['lockdown_v2'] = \
        {'H': mod, 'S': mod, 'W': mod, 'C': mod}
    scens['scenarios'][locations[0]].scenarios['New restrictions moderate effect, never released']['pars']['interventions'][0].policies['lockdown_v2'] = \
        {'H': mod, 'S': mod, 'W': mod, 'C': mod}

    # run the scenarios
    scens = ui.run_scens(scens)
    scens['verbose'] = True

    # plot cumulative infections to see if all the population gets infected
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs/' + locations[0] + '-projections' + '.png',
                       interval=30, n_cols=1,
                       fig_args=dict(figsize=(10, 8), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -3)},
                       axis_args={'left': 0.1, 'wspace': 0.3, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses'])

    # # Calibration Plot
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                    fig_path=dirname + '/figs/' + locations[0] + '-calibrate' + '.png',
    #                    interval=30, n_cols=2,
    #                    fig_args=dict(figsize=(10, 5), dpi=100),
    #                    font_size=11,
    #                    # y_lim={'new_infections': 500},
    #                    legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
    #                    axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
    #                    fill_args={'alpha': 0.3},
    #                    to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])

    # Export results to Excel
    workbook = xlsxwriter.Workbook(locations[0] + '_projections.xlsx')
    worksheet = workbook.add_worksheet('Projections')
    population = 11200000

    # Calibration data
    cum_diag_calib_end = \
    scens['scenarios'][locations[0]].results['cum_diagnoses']['New restrictions moderate effect, never released']['best'][131]
    cum_diag_calib_1week = \
    scens['scenarios'][locations[0]].results['cum_diagnoses']['New restrictions moderate effect, never released']['best'][138]
    cum_diag_calib_2week = \
    scens['scenarios'][locations[0]].results['cum_diagnoses']['New restrictions moderate effect, never released']['best'][145]
    cum_diag_calib_4week = \
    scens['scenarios'][locations[0]].results['cum_diagnoses']['New restrictions moderate effect, never released']['best'][159]
    cum_death_calib_end = \
    scens['scenarios'][locations[0]].results['cum_deaths']['New restrictions moderate effect, never released']['best'][131]
    cum_death_calib_1week = \
    scens['scenarios'][locations[0]].results['cum_deaths']['New restrictions moderate effect, never released']['best'][138]
    cum_death_calib_2week = \
    scens['scenarios'][locations[0]].results['cum_deaths']['New restrictions moderate effect, never released']['best'][145]
    cum_death_calib_4week = \
    scens['scenarios'][locations[0]].results['cum_deaths']['New restrictions moderate effect, never released']['best'][159]

    # Lower Bound: no change in restrictions
    new_inf_LB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_infections']['New restrictions moderate effect, never released']['best'][
        194:240])
    new_diag_LB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['New restrictions moderate effect, never released']['best'][
        194:240])
    cum_inf_LB_sep_oct = \
    scens['scenarios'][locations[0]].results['cum_infections']['New restrictions moderate effect, never released']['best'][240]
    incidence_LB_sep_oct = 100 * new_inf_LB_sep_oct * 30 / (240 - 194) / population
    detected_LB_sep_oct = 100 * new_diag_LB_sep_oct * 30 / (240 - 194) / population
    seroprev_LB_sep_oct = cum_inf_LB_sep_oct / population

    new_inf_LB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_infections']['New restrictions moderate effect, never released']['best'][
        241:285])
    new_diag_LB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['New restrictions moderate effect, never released']['best'][
        241:285])
    cum_inf_LB_nov_dec = \
    scens['scenarios'][locations[0]].results['cum_infections']['New restrictions moderate effect, never released']['best'][285]
    incidence_LB_nov_dec = 100 * new_inf_LB_nov_dec * 30 / (285 - 241) / population
    detected_LB_nov_dec = 100 * new_diag_LB_nov_dec * 30 / (285 - 241) / population
    seroprev_LB_nov_dec = cum_inf_LB_nov_dec / population

    # Mid Bound: small change mid- July
    new_inf_MB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_infections']['New restrictions enforced mid-July small effect, eased mid-September']['best'][
        194:240])
    new_diag_MB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['New restrictions enforced mid-July small effect, eased mid-September']['best'][
        194:240])
    cum_inf_MB_sep_oct = \
    scens['scenarios'][locations[0]].results['cum_infections']['New restrictions enforced mid-July small effect, eased mid-September']['best'][240]
    incidence_MB_sep_oct = 100 * new_inf_MB_sep_oct * 30 / (240 - 194) / population
    detected_MB_sep_oct = 100 * new_diag_MB_sep_oct * 30 / (240 - 194) / population
    seroprev_MB_sep_oct = cum_inf_MB_sep_oct / population

    new_inf_MB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_infections']['New restrictions enforced mid-July small effect, eased mid-September']['best'][
        241:285])
    new_diag_MB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['New restrictions enforced mid-July small effect, eased mid-September']['best'][
        241:285])
    cum_inf_MB_nov_dec = \
    scens['scenarios'][locations[0]].results['cum_infections']['New restrictions enforced mid-July small effect, eased mid-September']['best'][285]
    incidence_MB_nov_dec = 100 * new_inf_MB_nov_dec * 30 / (285 - 241) / population
    detected_MB_nov_dec = 100 * new_diag_MB_nov_dec * 30 / (285 - 241) / population
    seroprev_MB_nov_dec = cum_inf_MB_nov_dec / population

    # Upper Bound: moderate change mid-August
    new_inf_UB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_infections']['New restrictions enforced mid-July small effect, eased mid-August']['best'][
        194:240])
    new_diag_UB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['New restrictions enforced mid-July small effect, eased mid-August']['best'][
        194:240])
    cum_inf_UB_sep_oct = \
    scens['scenarios'][locations[0]].results['cum_infections']['New restrictions enforced mid-July small effect, eased mid-August']['best'][240]
    incidence_UB_sep_oct = 100 * new_inf_UB_sep_oct * 30 / (240 - 194) / population
    detected_UB_sep_oct = 100 * new_diag_UB_sep_oct * 30 / (240 - 194) / population
    seroprev_UB_sep_oct = cum_inf_UB_sep_oct / population

    new_inf_UB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_infections']['New restrictions enforced mid-July small effect, eased mid-August']['best'][
        241:285])
    new_diag_UB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['New restrictions enforced mid-July small effect, eased mid-August']['best'][
        241:285])
    cum_inf_UB_nov_dec = \
    scens['scenarios'][locations[0]].results['cum_infections']['New restrictions enforced mid-July small effect, eased mid-August']['best'][285]
    incidence_UB_nov_dec = 100 * new_inf_UB_nov_dec * 30 / (285 - 241) / population
    detected_UB_nov_dec = 100 * new_diag_UB_nov_dec * 30 / (285 - 241) / population
    seroprev_UB_nov_dec = cum_inf_UB_nov_dec / population

    projections = [
        ['Mid Sep – end Oct', '', '', '', '', '', '', '', '',
         'Nov – mid Dec', '', '', '', '', '', '', '', ''],
        ['Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '',
         'seroprevalence', '', '',
         'Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '',
         'seroprevalence', '', ''],
        #['MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB',
         #'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB'],
        [int(new_inf_MB_sep_oct), int(new_inf_LB_sep_oct), int(new_inf_UB_sep_oct),
         incidence_MB_sep_oct, incidence_LB_sep_oct, incidence_UB_sep_oct,
         detected_MB_sep_oct, detected_LB_sep_oct, detected_UB_sep_oct,
         seroprev_MB_sep_oct, seroprev_LB_sep_oct, seroprev_UB_sep_oct,
         int(new_inf_MB_nov_dec), int(new_inf_LB_nov_dec), int(new_inf_UB_nov_dec),
         incidence_MB_nov_dec, incidence_LB_nov_dec, incidence_UB_nov_dec,
         detected_MB_nov_dec, detected_LB_nov_dec, detected_UB_nov_dec,
         seroprev_MB_nov_dec, seroprev_LB_nov_dec, seroprev_UB_nov_dec]
    ]

    worksheet.add_table('A1:X4', {'data': projections})
    workbook.close()