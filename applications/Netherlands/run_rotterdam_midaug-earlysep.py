import user_interface as ui
import utils
import os
from datetime import date, timedelta
import pandas as pd

dirname = os.path.dirname(__file__)
import xlsxwriter

if __name__ == "__main__":
    # analysis location(s) for this analysis
    locations = ['Rotterdam']
    # databook names
    db_name = 'input_data_rotterdam'
    epi_name = 'epi_data_rotterdam'

    # Specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {locations[0]: {'pop_size': int(10e4),
                        'beta': 0.04,  # key calibration parameter, overwrites value in input databook `other_par` tab
                        'n_days': 353, # number of days from day 0 to end Feb
                        'pop_infected': 200, # number cases day 0, may need adjustment
                        'calibration_end': '2020-08-06'}} # data series end date last data entry available, for validation calibration: data series start 2020-03-08 (1st case) to end 2020-08-01, 147 days * 2/3rd data series (i.e. *0.67)= 98 days -> 2020-03-08 + 98 days= 2020-06-13 


    mid_july = 124 # make this the key date
    mid_aug = mid_july + 31 # 15 July is day 0, ie, subtract 1 from counts
    end_aug = mid_july + 47
    early_sep = end_aug + 1
    mid_sep = early_sep + 14
    end_sep = mid_sep + 15
    end_oct = end_sep + 31
    mid_nov = end_oct + 15
    end_dec = mid_nov + 46

    # metapars for all countries and scenarios
    metapars = {'n_runs': 8,   #test = 1, run = 8
                'noise': 0.1,    #test = 0, run = 0.03
                'verbose': 1,
                'rand_seed': 1}

    # the policies to change during scenario runs
    scen_opts = {locations[0]:  {'Small easing of restrictions in mid-August':
                                {'replace': (['relax3'], [['relax4']], [[mid_aug]]),
                                },
                                 
                                'Moderate easing of restrictions in mid-August':
                                {'replace': (['relax3'], [['relax5']], [[mid_aug]]),
                                },
                                
                                'Small easing of restrictions in early-September':
                                {'replace': (['relax3'], [['relax4']], [[early_sep]]),
                                },
                                 
                                'Moderate easing of restrictions in early-September':
                                {'replace': (['relax3'], [['relax5']], [[early_sep]]),
                                },
                                 
                                'No changes to current lockdown restrictions':
                                {'replace': (['relax3'], [['relax3']], [[500]])},
                                }}

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

    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs_rotterdam/Rotterdam-projections' + '.png',
                       interval=30, n_cols=1,
                       fig_args=dict(figsize=(10, 8), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -3)},
                       axis_args={'left': 0.1, 'wspace': 0.3, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses'])

    population = 644618

    # Lower Bound (LB): no change in restrictions
    new_inf_LB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions']['best'][
        mid_sep:end_oct])
    new_diag_LB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][
        mid_sep:end_oct])
    cum_inf_LB_sep_oct = \
    scens['scenarios'][locations[0]].results['cum_infections']['No changes to current lockdown restrictions']['best'][end_oct]
    incidence_LB_sep_oct = 100 * new_inf_LB_sep_oct * 30 / (end_oct - mid_sep) / population
    detected_LB_sep_oct = 100 * new_diag_LB_sep_oct * 30 / (end_oct - mid_sep) / population
    seroprev_LB_sep_oct = cum_inf_LB_sep_oct / population

    new_inf_LB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions']['best'][
        mid_nov:end_dec])
    new_diag_LB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][
        mid_nov:end_dec])
    cum_inf_LB_nov_dec = \
    scens['scenarios'][locations[0]].results['cum_infections']['No changes to current lockdown restrictions']['best'][end_dec]
    incidence_LB_nov_dec = 100 * new_inf_LB_nov_dec * 30 / (end_dec - mid_nov) / population
    detected_LB_nov_dec = 100 * new_diag_LB_nov_dec * 30 / (end_dec - mid_nov) / population
    seroprev_LB_nov_dec = cum_inf_LB_nov_dec / population

    # Mid Bound (MB): small change mid-August
    new_inf_MB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_infections']['Moderate easing of restrictions in mid-August']['best'][mid_sep:end_oct])
    new_diag_MB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['Moderate easing of restrictions in mid-August']['best'][mid_sep:end_oct])
    cum_inf_MB_sep_oct = \
    scens['scenarios'][locations[0]].results['cum_infections']['Moderate easing of restrictions in mid-August']['best'][end_oct]
    incidence_MB_sep_oct = 100 * new_inf_MB_sep_oct * 30 / (end_oct - mid_sep) / population
    detected_MB_sep_oct = 100 * new_diag_MB_sep_oct * 30 / (end_oct - mid_sep) / population
    seroprev_MB_sep_oct = cum_inf_MB_sep_oct / population

    new_inf_MB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_infections']['Moderate easing of restrictions in early-September']['best'][mid_nov:end_dec])
    new_diag_MB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['Moderate easing of restrictions in early-September']['best'][mid_nov:end_dec])
    cum_inf_MB_nov_dec = \
    scens['scenarios'][locations[0]].results['cum_infections']['Moderate easing of restrictions in early-September']['best'][end_dec]
    incidence_MB_nov_dec = 100 * new_inf_MB_nov_dec * 30 / (end_dec - mid_nov) / population
    detected_MB_nov_dec = 100 * new_diag_MB_nov_dec * 30 / (end_dec - mid_nov) / population
    seroprev_MB_nov_dec = cum_inf_MB_nov_dec / population

    # Upper Bound (UB): moderate change early-September
    new_inf_UB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_infections']['Moderate easing of restrictions in early-September']['best'][
        mid_sep:end_oct])
    new_diag_UB_sep_oct = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['Moderate easing of restrictions in early-September']['best'][
        mid_sep:end_oct])
    cum_inf_UB_sep_oct = \
    scens['scenarios'][locations[0]].results['cum_infections']['Moderate easing of restrictions in early-September']['best'][end_oct]
    incidence_UB_sep_oct = 100 * new_inf_UB_sep_oct * 30 / (end_oct - mid_sep) / population
    detected_UB_sep_oct = 100 * new_diag_UB_sep_oct * 30 / (end_oct - mid_sep) / population
    seroprev_UB_sep_oct = cum_inf_UB_sep_oct / population

    new_inf_UB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_infections']['Moderate easing of restrictions in early-September']['best'][
        mid_nov:end_dec])
    new_diag_UB_nov_dec = sum(
        scens['scenarios'][locations[0]].results['new_diagnoses']['Moderate easing of restrictions in early-September']['best'][
        mid_nov:end_dec])
    cum_inf_UB_nov_dec = \
    scens['scenarios'][locations[0]].results['cum_infections']['Moderate easing of restrictions in early-September']['best'][end_dec]
    incidence_UB_nov_dec = 100 * new_inf_UB_nov_dec * 30 / (end_dec - mid_nov) / population
    detected_UB_nov_dec = 100 * new_diag_UB_nov_dec * 30 / (end_dec - mid_nov) / population
    seroprev_UB_nov_dec = cum_inf_UB_nov_dec / population

    projections = [
        ['Mid Sep – end Oct', '', '', '', '', '', '', '', '', '', '', '',
         'Nov – mid Dec', '', '', '', '', '', '', '', '', '', '', ''],
        ['Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '',
         'seroprevalence', '', '',
         'Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '',
         'seroprevalence', '', ''],
        ['MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB',
         'MB', 'LB', 'UB', 'MB', 'LB', 'UB'],
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
    workbook = xlsxwriter.Workbook('Rotterdam_projections.xlsx')
    worksheet = workbook.add_worksheet('Projections')
    worksheet.add_table('A1:X4', {'data': projections, 'header_row': False})
    worksheet2 = workbook.add_worksheet('Daily projections')
    sdate = date(2020, 7, 15)  # start date
    edate = date(2020, 12, 31)  # end date

    # fist scenario time period
    daily_inf_small_aug = scens['scenarios'][locations[0]].results['new_infections'][
                              'Small easing of restrictions in mid-August'] \
                              ['best'][mid_aug:end_dec]
    daily_death_small_aug = scens['scenarios'][locations[0]].results['new_deaths'][
                                'Small easing of restrictions in mid-August'] \
                                ['best'][mid_aug:end_dec]
    daily_diag_small_aug = scens['scenarios'][locations[0]].results['new_diagnoses'][
                               'Small easing of restrictions in mid-August'] \
                               ['best'][mid_aug:end_dec]

    daily_inf_mod_aug = scens['scenarios'][locations[0]].results['new_infections'][
                            'Moderate easing of restrictions in mid-August'] \
                            ['best'][mid_aug:end_dec]
    daily_death_mod_aug = scens['scenarios'][locations[0]].results['new_deaths'][
                              'Moderate easing of restrictions in mid-August'] \
                              ['best'][mid_aug:end_dec]
    daily_diag_mod_aug = scens['scenarios'][locations[0]].results['new_diagnoses'][
                             'Moderate easing of restrictions in mid-August'] \
                             ['best'][mid_aug:end_dec]
 
    # second scenario time period
    daily_inf_small_sep = scens['scenarios'][locations[0]].results['new_infections'][
                              'Small easing of restrictions in early-September'] \
                              ['best'][early_sep:end_dec]
    daily_death_small_sep = scens['scenarios'][locations[0]].results['new_deaths'][
                                'Small easing of restrictions in early-September'] \
                                ['best'][early_sep:end_dec]
    daily_diag_small_sep = scens['scenarios'][locations[0]].results['new_diagnoses'][
                               'Small easing of restrictions in early-September'] \
                               ['best'][early_sep:end_dec]

    daily_inf_mod_sep = scens['scenarios'][locations[0]].results['new_infections'][
                            'Moderate easing of restrictions in early-September'] \
                            ['best'][early_sep:end_dec]
    daily_death_mod_sep = scens['scenarios'][locations[0]].results['new_deaths'][
                              'Moderate easing of restrictions in early-September'] \
                              ['best'][early_sep:end_dec]
    daily_diag_mod_sep = scens['scenarios'][locations[0]].results['new_diagnoses'][
                             'Moderate easing of restrictions in early-September'] \
                             ['best'][early_sep:end_dec]

    daily_inf_no_release = \
        scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions'] \
            ['best'][mid_aug:end_dec]
    daily_death_no_release = \
        scens['scenarios'][locations[0]].results['new_deaths']['No changes to current lockdown restrictions'] \
            ['best'][mid_aug:end_dec]
    daily_diag_no_release = \
        scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions'] \
            ['best'][mid_aug:end_dec]

    daily_projections = [
        ['Dates'] + [str(d) for d in pd.date_range(sdate, edate - timedelta(days=1), freq='d')],
        ['Small easing of restrictions in early-September'] + [int(val) for val in daily_inf_small_sep],
        ['Moderate easing of restrictions in early-September'] + [int(val) for val in daily_inf_mod_sep],
        ['Small easing of restrictions in mid-August'] + [int(val) for val in daily_inf_small_aug],
        ['Moderate easing of restrictions in mid-August'] + [int(val) for val in daily_inf_mod_aug],
        ['No changes to current lockdown restrictions'] + [int(val) for val in daily_inf_no_release],
        ['Small easing of restrictions in early-September'] + [int(val) for val in daily_death_small_sep],
        ['Moderate easing of restrictions in early-September'] + [int(val) for val in daily_death_mod_sep],
        ['Small easing of restrictions in mid-August'] + [int(val) for val in daily_death_small_aug],
        ['Moderate easing of restrictions in mid-August'] + [int(val) for val in daily_death_mod_aug],
        ['No changes to current lockdown restrictions'] + [int(val) for val in daily_death_no_release],
        ['Small easing of restrictions in early-September'] + [int(val) for val in daily_diag_small_sep],
        ['Moderate easing of restrictions in early-September'] + [int(val) for val in daily_diag_mod_sep],
        ['Small easing of restrictions in mid-August'] + [int(val) for val in daily_diag_small_aug],
        ['Moderate easing of restrictions in mid-August'] + [int(val) for val in daily_diag_mod_aug],
        ['No changes to current lockdown restrictions'] + [int(val) for val in daily_diag_no_release]]
    worksheet2.add_table('A1:EK17', {'data': daily_projections})
    workbook.close()