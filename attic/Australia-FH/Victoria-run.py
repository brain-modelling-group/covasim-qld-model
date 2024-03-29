import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)
import xlsxwriter
from datetime import date, timedelta
import pandas as pd

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Victoria']
    # the name of the databook
    db_name = 'input_data_Australia-FH'
    epi_name = 'epi_data_Australia-FH'

    # Victoria specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C', 'aged_care']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-Victoria specific parameters
    user_pars = {'Victoria': {'pop_size': int(10e4),
                               'beta': 0.1,
                               'n_days': 215,
                               'calibration_end': '2020-08-11'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}

    mid_july = 45 # make this the key date
    end_july = mid_july + 16
    mid_aug = end_july + 15
    end_aug = mid_aug + 15
    mid_sep = mid_aug + 31
    end_sep = mid_sep + 15
    mid_oct = mid_sep + 30
    end_oct = mid_sep + 46
    start_nov = end_oct + 1
    mid_nov = end_oct + 15
    end_dec = mid_nov + 46

    # the policies to change during scenario runs
    scen_opts = {'Victoria': {'Small increase of restrictions in mid-September': 
                              {'replace': (['disaster'], [['relax1']], [[mid_sep]])},

                            'Moderate increase of restrictions in mid-September': 
                              {'replace': (['disaster'], [['relax2']], [[mid_sep]])},

                            'Small increase of restrictions in mid-October': 
                              {'replace': (['disaster'], [['relax1']], [[mid_oct]])},

                            'Moderate increase of restrictions in mid-October': 
                              {'replace': (['disaster'], [['relax2']], [[mid_oct]])},

                            'No changes to current lockdown restrictions': 
                              {'replace': (['disaster'], [['restrictions']], [[1]])}}}

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
                        fig_path=dirname + '/figs/Victoria-projection' + '.png',
                  interval=30, n_cols=1,
                  fig_args=dict(figsize=(10, 8), dpi=100),
                  font_size=11,
                  # y_lim={'new_infections': 10000},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -3)},
                  axis_args={'left': 0.1, 'wspace': 0.3, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
                  fill_args={'alpha': 0.3},
              to_plot=['new_infections', 'cum_infections', 'cum_diagnoses'])

    # Results
    population = 6651074

    # Lower Bound: no change in restrictions
    new_inf_LB_sep_oct = sum(scens['scenarios']['Victoria'].results['new_infections']['No changes to current lockdown restrictions']['best'][mid_sep:end_oct])    
    new_diag_LB_sep_oct = sum(scens['scenarios']['Victoria'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][mid_sep:end_oct])    
    cum_inf_LB_sep_oct = scens['scenarios']['Victoria'].results['cum_infections']['No changes to current lockdown restrictions']['best'][end_oct]    
    incidence_LB_sep_oct = 100*new_inf_LB_sep_oct*30/(end_oct-mid_sep)/population
    detected_LB_sep_oct = 100*new_diag_LB_sep_oct*30/(end_oct-mid_sep)/population
    seroprev_LB_sep_oct = cum_inf_LB_sep_oct/population

    new_inf_LB_nov_dec = sum(scens['scenarios']['Victoria'].results['new_infections']['No changes to current lockdown restrictions']['best'][start_nov:end_dec])    
    new_diag_LB_nov_dec = sum(scens['scenarios']['Victoria'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][start_nov:end_dec])    
    cum_inf_LB_nov_dec = scens['scenarios']['Victoria'].results['cum_infections']['No changes to current lockdown restrictions']['best'][end_dec]    
    incidence_LB_nov_dec = 100*new_inf_LB_nov_dec*30/(end_dec-start_nov)/population
    detected_LB_nov_dec = 100*new_diag_LB_nov_dec*30/(end_dec-start_nov)/population
    seroprev_LB_nov_dec = cum_inf_LB_nov_dec/population

    # Mid Bound: small change mid- July    
    new_inf_MB_sep_oct = sum(scens['scenarios']['Victoria'].results['new_infections']['Small increase of restrictions in mid-September']['best'][mid_sep:end_oct])    
    new_diag_MB_sep_oct = sum(scens['scenarios']['Victoria'].results['new_diagnoses']['Small increase of restrictions in mid-September']['best'][mid_sep:end_oct])    
    cum_inf_MB_sep_oct = scens['scenarios']['Victoria'].results['cum_infections']['Small increase of restrictions in mid-September']['best'][end_oct]    
    incidence_MB_sep_oct = 100*new_inf_MB_sep_oct*30/(end_oct-mid_sep)/population
    detected_MB_sep_oct = 100*new_diag_MB_sep_oct*30/(end_oct-mid_sep)/population
    seroprev_MB_sep_oct = cum_inf_MB_sep_oct/population

    new_inf_MB_nov_dec = sum(scens['scenarios']['Victoria'].results['new_infections']['Small increase of restrictions in mid-September']['best'][start_nov:end_dec])    
    new_diag_MB_nov_dec = sum(scens['scenarios']['Victoria'].results['new_diagnoses']['Small increase of restrictions in mid-September']['best'][start_nov:end_dec])    
    cum_inf_MB_nov_dec = scens['scenarios']['Victoria'].results['cum_infections']['Small increase of restrictions in mid-September']['best'][end_dec]    
    incidence_MB_nov_dec = 100*new_inf_MB_nov_dec*30/(end_dec-start_nov)/population
    detected_MB_nov_dec = 100*new_diag_MB_nov_dec*30/(end_dec-start_nov)/population
    seroprev_MB_nov_dec = cum_inf_MB_nov_dec/population

    # Upper Bound: moderate change mid-September    
    new_inf_UB_sep_oct = sum(scens['scenarios']['Victoria'].results['new_infections']['Moderate increase of restrictions in mid-October']['best'][mid_sep:end_oct])    
    new_diag_UB_sep_oct = sum(scens['scenarios']['Victoria'].results['new_diagnoses']['Moderate increase of restrictions in mid-October']['best'][mid_sep:end_oct])    
    cum_inf_UB_sep_oct = scens['scenarios']['Victoria'].results['cum_infections']['Moderate increase of restrictions in mid-October']['best'][end_oct]    
    incidence_UB_sep_oct = 100*new_inf_UB_sep_oct*30/(end_oct-mid_sep)/population
    detected_UB_sep_oct = 100*new_diag_UB_sep_oct*30/(end_oct-mid_sep)/population
    seroprev_UB_sep_oct = cum_inf_UB_sep_oct/population

    new_inf_UB_nov_dec = sum(scens['scenarios']['Victoria'].results['new_infections']['Moderate increase of restrictions in mid-October']['best'][start_nov:end_dec])    
    new_diag_UB_nov_dec = sum(scens['scenarios']['Victoria'].results['new_diagnoses']['Moderate increase of restrictions in mid-October']['best'][start_nov:end_dec])    
    cum_inf_UB_nov_dec = scens['scenarios']['Victoria'].results['cum_infections']['Moderate increase of restrictions in mid-October']['best'][end_dec]    
    incidence_UB_nov_dec = 100*new_inf_UB_nov_dec*30/(end_dec-start_nov)/population
    detected_UB_nov_dec = 100*new_diag_UB_nov_dec*30/(end_dec-start_nov)/population
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
    workbook = xlsxwriter.Workbook('Victoria_projections.xlsx')     
    worksheet = workbook.add_worksheet('Projections')
    worksheet.add_table('A1:X4', {'data': projections, 'header_row': False})

    worksheet2 = workbook.add_worksheet('Daily projections')
    sdate = date(2020, 7, 15)  # start date
    edate = date(2020, 12, 31)  # end date


    daily_inf_small_aug = scens['scenarios'][locations[0]].results['new_infections'][
                              'Small increase of restrictions in mid-October'] \
                              ['best'][mid_july:end_dec]
    daily_death_small_aug = scens['scenarios'][locations[0]].results['new_deaths'][
                                'Small increase of restrictions in mid-October'] \
                                ['best'][mid_july:end_dec]
    daily_diag_small_aug = scens['scenarios'][locations[0]].results['new_diagnoses'][
                               'Small increase of restrictions in mid-October'] \
                               ['best'][mid_july:end_dec]

    daily_inf_mod_aug = scens['scenarios'][locations[0]].results['new_infections'][
                            'Moderate increase of restrictions in mid-October'] \
                            ['best'][mid_july:end_dec]
    daily_death_mod_aug = scens['scenarios'][locations[0]].results['new_deaths'][
                              'Moderate increase of restrictions in mid-October'] \
                              ['best'][mid_july:end_dec]
    daily_diag_mod_aug = scens['scenarios'][locations[0]].results['new_diagnoses'][
                             'Moderate increase of restrictions in mid-October'] \
                             ['best'][mid_july:end_dec]

    daily_inf_small_sep = scens['scenarios'][locations[0]].results['new_infections'][
                              'Small increase of restrictions in mid-September'] \
                              ['best'][mid_july:end_dec]
    daily_death_small_sep = scens['scenarios'][locations[0]].results['new_deaths'][
                                'Small increase of restrictions in mid-September'] \
                                ['best'][mid_july:end_dec]
    daily_diag_small_sep = scens['scenarios'][locations[0]].results['new_diagnoses'][
                               'Small increase of restrictions in mid-September'] \
                               ['best'][mid_july:end_dec]

    daily_inf_mod_sep = scens['scenarios'][locations[0]].results['new_infections'][
                            'Moderate increase of restrictions in mid-September'] \
                            ['best'][mid_july:end_dec]
    daily_death_mod_sep = scens['scenarios'][locations[0]].results['new_deaths'][
                              'Moderate increase of restrictions in mid-September'] \
                              ['best'][mid_july:end_dec]
    daily_diag_mod_sep = scens['scenarios'][locations[0]].results['new_diagnoses'][
                             'Moderate increase of restrictions in mid-September'] \
                             ['best'][mid_july:end_dec]

    daily_inf_no_release = scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions'] \
        ['best'][mid_july:end_dec]
    daily_death_no_release = scens['scenarios'][locations[0]].results['new_deaths']['No changes to current lockdown restrictions'] \
        ['best'][mid_july:end_dec]
    daily_diag_no_release = scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions'] \
        ['best'][mid_july:end_dec]

    daily_projections = [
        ['Dates'] + [str(d) for d in pd.date_range(sdate, edate - timedelta(days=1), freq='d')],
        ['New infections'],
        ['Small increase of restrictions in mid-October'] + [int(val) for val in daily_inf_small_aug],
        ['Moderate increase of restrictions in mid-October'] + [int(val) for val in daily_inf_mod_aug],
        ['Small increase of restrictions in mid-September'] + [int(val) for val in daily_inf_small_sep],
        ['Moderate increase of restrictions in mid-September'] + [int(val) for val in daily_inf_mod_sep],
        ['No changes to current lockdown restrictions'] + [int(val) for val in daily_inf_no_release],
        ['New deaths'],
        ['Small increase of restrictions in mid-October'] + [int(val) for val in daily_death_small_aug],
        ['Moderate increase of restrictions in mid-October'] + [int(val) for val in daily_death_mod_aug],
        ['Small increase of restrictions in mid-September'] + [int(val) for val in daily_death_small_sep],
        ['Moderate increase of restrictions in mid-September'] + [int(val) for val in daily_death_mod_sep],
        ['No changes to current lockdown restrictions'] + [int(val) for val in daily_death_no_release],
        ['New diagnoses'],
        ['Small increase of restrictions in mid-October'] + [int(val) for val in daily_diag_small_aug],
        ['Moderate increase of restrictions in mid-October'] + [int(val) for val in daily_diag_mod_aug],
        ['Small increase of restrictions in mid-September'] + [int(val) for val in daily_diag_small_sep],
        ['Moderate increase of restrictions in mid-September'] + [int(val) for val in daily_diag_mod_sep],
        ['No changes to current lockdown restrictions'] + [int(val) for val in daily_diag_no_release]]
    worksheet2.add_table('A1:FO20', {'data': daily_projections})
    workbook.close()