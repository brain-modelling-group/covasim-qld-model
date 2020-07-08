import user_interface as ui
import utils
import os

dirname = os.path.dirname(__file__)
import xlsxwriter

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Campinas']
    # the name of the databook
    db_name = 'input_data_Brazil'
    epi_name = 'epi_data_Brazil'

    # Manausecify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-Manausecific parameters
    user_pars = {'Campinas': {'pop_size': int(10e4),
                            'beta': 0.071,
                            'n_days': 303,
                            'pop_infected': 27,
                            'calibration_end': '2020-07-06'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}

    # the policies to change during scenario runs
    scen_opts = {'Campinas': {'Small easing of restrictions in mid-August':
                                {'replace': (['relax1'], [['relax2']], [[165]]),
                                 'policies': {'relax2': {'beta': 0.5}}},

                            'Moderate easing of restrictions in mid-August':
                                {'replace': (['relax1'], [['relax2']], [[165]]),
                                 'policies': {'relax2': {'beta': 0.6}}},

                            'Small easing of restrictions in mid-July':
                                {'replace': (['relax1'], [['relax2']], [[134]]),
                                 'policies': {'relax2': {'beta': 0.5}}},

                            'Moderate easing of restrictions in mid-July':
                                {'replace': (['relax1'], [['relax2']], [[134]]),
                                 'policies': {'relax2': {'beta': 0.6}}},

                            'No changes to current lockdown restrictions':
                                {'replace': (['relax1'], [['relax1']], [[500]]),
                                 'policies': {'relax1': {'beta': 0.2}}}}}

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
                       fig_path=dirname + '/figs/Campinas-projections' + '.png',
                       interval=30, n_cols=1,
                       fig_args=dict(figsize=(10, 8), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -3)},
                       axis_args={'left': 0.1, 'wspace': 0.3, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses'])

    # Export results to Excel
    workbook = xlsxwriter.Workbook('Campinas_projections.xlsx')
    worksheet = workbook.add_worksheet('Projections')
    population = 1200000

    # Calibration data
    cum_diag_calib_end = \
    scens['scenarios']['Campinas'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][125]
    cum_diag_calib_1week = \
    scens['scenarios']['Campinas'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][132]
    cum_diag_calib_2week = \
    scens['scenarios']['Campinas'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][139]
    cum_diag_calib_4week = \
    scens['scenarios']['Campinas'].results['cum_diagnoses']['No changes to current lockdown restrictions']['best'][153]
    cum_death_calib_end = \
    scens['scenarios']['Campinas'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][125]
    cum_death_calib_1week = \
    scens['scenarios']['Campinas'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][132]
    cum_death_calib_2week = \
    scens['scenarios']['Campinas'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][139]
    cum_death_calib_4week = \
    scens['scenarios']['Campinas'].results['cum_deaths']['No changes to current lockdown restrictions']['best'][153]

    # Lower Bound: no change in restrictions
    new_inf_LB_sep_oct = sum(
        scens['scenarios']['Campinas'].results['new_infections']['No changes to current lockdown restrictions']['best'][
        196:241])
    new_diag_LB_sep_oct = sum(
        scens['scenarios']['Campinas'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][
        196:241])
    cum_inf_LB_sep_oct = \
    scens['scenarios']['Campinas'].results['cum_infections']['No changes to current lockdown restrictions']['best'][246]
    incidence_LB_sep_oct = 100 * new_inf_LB_sep_oct * 30 / (241 - 196) / population
    detected_LB_sep_oct = 100 * new_diag_LB_sep_oct * 30 / (241 - 196)
    seroprev_LB_sep_oct = cum_inf_LB_sep_oct / population

    new_inf_LB_nov_dec = sum(
        scens['scenarios']['Campinas'].results['new_infections']['No changes to current lockdown restrictions']['best'][
        243:286])
    new_diag_LB_nov_dec = sum(
        scens['scenarios']['Campinas'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][
        243:286])
    cum_inf_LB_nov_dec = \
    scens['scenarios']['Campinas'].results['cum_infections']['No changes to current lockdown restrictions']['best'][291]
    incidence_LB_nov_dec = 100 * new_inf_LB_nov_dec * 30 / (286 - 243) / population
    detected_LB_nov_dec = 100 * new_diag_LB_nov_dec * 30 / (286 - 243)
    seroprev_LB_nov_dec = cum_inf_LB_nov_dec / population

    # Mid Bound: small change mid- July
    new_inf_MB_sep_oct = sum(
        scens['scenarios']['Campinas'].results['new_infections']['Small easing of restrictions in mid-July']['best'][
        196:241])
    new_diag_MB_sep_oct = sum(
        scens['scenarios']['Campinas'].results['new_diagnoses']['Small easing of restrictions in mid-July']['best'][
        196:241])
    cum_inf_MB_sep_oct = \
    scens['scenarios']['Campinas'].results['cum_infections']['Small easing of restrictions in mid-July']['best'][246]
    incidence_MB_sep_oct = 100 * new_inf_MB_sep_oct * 30 / (241 - 196) / population
    detected_MB_sep_oct = 100 * new_diag_MB_sep_oct * 30 / (241 - 196)
    seroprev_MB_sep_oct = cum_inf_MB_sep_oct / population

    new_inf_MB_nov_dec = sum(
        scens['scenarios']['Campinas'].results['new_infections']['Small easing of restrictions in mid-July']['best'][
        243:286])
    new_diag_MB_nov_dec = sum(
        scens['scenarios']['Campinas'].results['new_diagnoses']['Small easing of restrictions in mid-July']['best'][
        243:286])
    cum_inf_MB_nov_dec = \
    scens['scenarios']['Campinas'].results['cum_infections']['Small easing of restrictions in mid-July']['best'][291]
    incidence_MB_nov_dec = 100 * new_inf_MB_nov_dec * 30 / (286 - 243) / population
    detected_MB_nov_dec = 100 * new_diag_MB_nov_dec * 30 / (286 - 243)
    seroprev_MB_nov_dec = cum_inf_MB_nov_dec / population

    # Upper Bound: moderate change mid-August
    new_inf_UB_sep_oct = sum(
        scens['scenarios']['Campinas'].results['new_infections']['Moderate easing of restrictions in mid-August']['best'][
        196:241])
    new_diag_UB_sep_oct = sum(
        scens['scenarios']['Campinas'].results['new_diagnoses']['Moderate easing of restrictions in mid-August']['best'][
        196:241])
    cum_inf_UB_sep_oct = \
    scens['scenarios']['Campinas'].results['cum_infections']['Moderate easing of restrictions in mid-August']['best'][246]
    incidence_UB_sep_oct = 100 * new_inf_UB_sep_oct * 30 / (241 - 196) / population
    detected_UB_sep_oct = 100 * new_diag_UB_sep_oct * 30 / (241 - 196)
    seroprev_UB_sep_oct = cum_inf_UB_sep_oct / population

    new_inf_UB_nov_dec = sum(
        scens['scenarios']['Campinas'].results['new_infections']['Moderate easing of restrictions in mid-August']['best'][
        243:286])
    new_diag_UB_nov_dec = sum(
        scens['scenarios']['Campinas'].results['new_diagnoses']['Moderate easing of restrictions in mid-August']['best'][
        243:286])
    cum_inf_UB_nov_dec = \
    scens['scenarios']['Campinas'].results['cum_infections']['Moderate easing of restrictions in mid-August']['best'][291]
    incidence_UB_nov_dec = 100 * new_inf_UB_nov_dec * 30 / (286 - 243) / population
    detected_UB_nov_dec = 100 * new_diag_UB_nov_dec * 30 / (286 - 243)
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
         int(detected_MB_sep_oct), int(detected_LB_sep_oct), int(detected_UB_sep_oct),
         seroprev_MB_sep_oct, seroprev_LB_sep_oct, seroprev_UB_sep_oct,
         int(new_inf_MB_nov_dec), int(new_inf_LB_nov_dec), int(new_inf_UB_nov_dec),
         incidence_MB_nov_dec, incidence_LB_nov_dec, incidence_UB_nov_dec,
         int(detected_MB_nov_dec), int(detected_LB_nov_dec), int(detected_UB_nov_dec),
         seroprev_MB_nov_dec, seroprev_LB_nov_dec, seroprev_UB_nov_dec]
    ]

    worksheet.add_table('A1:X4', {'data': projections})
    workbook.close()