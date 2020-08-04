import xlsxwriter
import pickle
import os
from datetime import date, timedelta
import pandas as pd

dirname = os.path.dirname(__file__)
locations = ['Birmingham']
population = 210000
filehandler = open('runs/' + locations[0] + '.obj', 'rb')
scens = pickle.load(filehandler)

mid_july = 132  # make this the key date
mid_aug = mid_july + 31
mid_sep = mid_aug + 31
end_oct = mid_sep + 46
mid_nov = end_oct + 15
end_dec = mid_nov + 46

# Lower Bound: no change in restrictions
new_inf_LB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions']['best'][203:249])
new_diag_LB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][203:249])
cum_inf_LB_sep_oct = scens['scenarios'][locations[0]].results['cum_infections']['No changes to current lockdown restrictions']['best'][249]
incidence_LB_sep_oct = 100 * new_inf_LB_sep_oct * 30 / (249 - 203) / population
detected_LB_sep_oct = 100 * new_diag_LB_sep_oct * 30 / (249 - 203) / population
seroprev_LB_sep_oct = cum_inf_LB_sep_oct / population

new_inf_LB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions']['best'][250:294])
new_diag_LB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][250:294])
cum_inf_LB_nov_dec = scens['scenarios'][locations[0]].results['cum_infections']['No changes to current lockdown restrictions']['best'][294]
incidence_LB_nov_dec = 100 * new_inf_LB_nov_dec * 30 / (294 - 250) / population
detected_LB_nov_dec = 100 * new_diag_LB_nov_dec * 30 / (294 - 250) / population
seroprev_LB_nov_dec = cum_inf_LB_nov_dec / population

# Mid Bound: small change mid- July
new_inf_MB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_infections']['Small easing of restrictions on July 15']['best'][203:249])
new_diag_MB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['Small easing of restrictions on July 15']['best'][203:249])
cum_inf_MB_sep_oct = scens['scenarios'][locations[0]].results['cum_infections']['Small easing of restrictions on July 15']['best'][249]
incidence_MB_sep_oct = 100 * new_inf_MB_sep_oct * 30 / (249 - 203) / population
detected_MB_sep_oct = 100 * new_diag_MB_sep_oct * 30 / (249 - 203) / population
seroprev_MB_sep_oct = cum_inf_MB_sep_oct / population

new_inf_MB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_infections']['Small easing of restrictions on July 15']['best'][250:294])
new_diag_MB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['Small easing of restrictions on July 15']['best'][250:294])
cum_inf_MB_nov_dec = scens['scenarios'][locations[0]].results['cum_infections']['Small easing of restrictions on July 15']['best'][294]
incidence_MB_nov_dec = 100 * new_inf_MB_nov_dec * 30 / (294 - 250) / population
detected_MB_nov_dec = 100 * new_diag_MB_nov_dec * 30 / (294 - 250) / population
seroprev_MB_nov_dec = cum_inf_MB_nov_dec / population

# Upper Bound: moderate change mid-August
new_inf_UB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_infections']['Moderate easing of restrictions on August 1']['best'][203:249])
new_diag_UB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['Moderate easing of restrictions on August 1']['best'][203:249])
cum_inf_UB_sep_oct = scens['scenarios'][locations[0]].results['cum_infections']['Moderate easing of restrictions on August 1']['best'][249]
incidence_UB_sep_oct = 100 * new_inf_UB_sep_oct * 30 / (249 - 203) / population
detected_UB_sep_oct = 100 * new_diag_UB_sep_oct * 30 / (249 - 203) / population
seroprev_UB_sep_oct = cum_inf_UB_sep_oct / population

new_inf_UB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_infections']['Moderate easing of restrictions on August 1']['best'][250:294])
new_diag_UB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['Moderate easing of restrictions on August 1']['best'][250:294])
cum_inf_UB_nov_dec = scens['scenarios'][locations[0]].results['cum_infections']['Moderate easing of restrictions on August 1']['best'][294]
incidence_UB_nov_dec = 100 * new_inf_UB_nov_dec * 30 / (294 - 250) / population
detected_UB_nov_dec = 100 * new_diag_UB_nov_dec * 30 / (294 - 250) / population
seroprev_UB_nov_dec = cum_inf_UB_nov_dec / population

projections = [
    ['Mid Sep – end Oct', '', '', '', '', '', '', '', '', '', '', '', 'Nov – mid Dec'],
    ['Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '', 'seroprevalence',
     '', '',
     'Projected cases', '', '', '30 day incidence (%)', '', '', '30 day detected cases (%)', '', '', 'seroprevalence'],
    ['MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB',
     'MB', 'LB', 'UB', 'MB', 'LB', 'UB', 'MB', 'LB', 'UB'],
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
workbook = xlsxwriter.Workbook(locations[0] + '_projections.xlsx')
worksheet = workbook.add_worksheet('Projections')
worksheet.add_table('A1:X4', {'data': projections})
worksheet2 = workbook.add_worksheet('Daily projections')
sdate = date(2020, 7, 15)  # start date
edate = date(2020, 12, 31)  # end date

daily_inf_small_aug = scens['scenarios'][locations[0]].results['new_infections'][
                          'Small easing of restrictions on August 1'] \
                          ['best'][mid_july:end_dec]
daily_death_small_aug = scens['scenarios'][locations[0]].results['new_deaths'][
                            'Small easing of restrictions on August 1'] \
                            ['best'][mid_july:end_dec]
daily_diag_small_aug = scens['scenarios'][locations[0]].results['new_diagnoses'][
                           'Small easing of restrictions on August 1'] \
                           ['best'][mid_july:end_dec]

daily_inf_mod_aug = scens['scenarios'][locations[0]].results['new_infections'][
                        'Moderate easing of restrictions on August 1'] \
                        ['best'][mid_july:end_dec]
daily_death_mod_aug = scens['scenarios'][locations[0]].results['new_deaths'][
                          'Moderate easing of restrictions on August 1'] \
                          ['best'][mid_july:end_dec]
daily_diag_mod_aug = scens['scenarios'][locations[0]].results['new_diagnoses'][
                         'Moderate easing of restrictions on August 1'] \
                         ['best'][mid_july:end_dec]

daily_inf_small_sep = scens['scenarios'][locations[0]].results['new_infections'][
                          'Small easing of restrictions on July 15'] \
                          ['best'][mid_july:end_dec]
daily_death_small_sep = scens['scenarios'][locations[0]].results['new_deaths'][
                            'Small easing of restrictions on July 15'] \
                            ['best'][mid_july:end_dec]
daily_diag_small_sep = scens['scenarios'][locations[0]].results['new_diagnoses'][
                           'Small easing of restrictions on July 15'] \
                           ['best'][mid_july:end_dec]

daily_inf_mod_sep = scens['scenarios'][locations[0]].results['new_infections'][
                        'Moderate easing of restrictions on July 15'] \
                        ['best'][mid_july:end_dec]
daily_death_mod_sep = scens['scenarios'][locations[0]].results['new_deaths'][
                          'Moderate easing of restrictions on July 15'] \
                          ['best'][mid_july:end_dec]
daily_diag_mod_sep = scens['scenarios'][locations[0]].results['new_diagnoses'][
                         'Moderate easing of restrictions on July 15'] \
                         ['best'][mid_july:end_dec]

daily_inf_no_release = \
    scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions'] \
        ['best'][mid_july:end_dec]
daily_death_no_release = \
    scens['scenarios'][locations[0]].results['new_deaths']['No changes to current lockdown restrictions'] \
        ['best'][mid_july:end_dec]
daily_diag_no_release = \
    scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions'] \
        ['best'][mid_july:end_dec]

daily_projections = [
    ['Dates'] + [str(d) for d in pd.date_range(sdate, edate - timedelta(days=1), freq='d')],
    ['New infections Small easing of restrictions on August 1'] + [int(val) for val in
                                                                                            daily_inf_small_aug],
    ['New infections Moderate easing of restrictions on August 1'] + [int(val) for val in
                                                                                               daily_inf_mod_aug],
    ['New infections Small easing of restrictions on July 15'] + [int(val) for val in
                                                                                               daily_inf_small_sep],
    ['New infections Moderate easing of restrictions on July 15'] + [int(val) for val in
                                                                                                  daily_inf_mod_sep],
    ['New infections No changes to current lockdown restrictions'] + [int(val) for val in daily_inf_no_release],
    ['New deaths Small easing of restrictions on August 1'] + [int(val) for val in
                                                                                        daily_death_small_aug],
    ['New deaths Moderate easing of restrictions on August 1'] + [int(val) for val in
                                                                                           daily_death_mod_aug],
    ['New deaths Small easing of restrictions on July 15'] + [int(val) for val in
                                                                                           daily_death_small_sep],
    ['New deaths Moderate easing of restrictions on July 15'] + [int(val) for val in
                                                                                              daily_death_mod_sep],
    ['New deaths No changes to current lockdown restrictions'] + [int(val) for val in daily_death_no_release],
    ['New diagnoses Small easing of restrictions on August 1'] + [int(val) for val in
                                                                                           daily_diag_small_aug],
    ['New diagnoses Moderate easing of restrictions on August 1'] + [int(val) for val in
                                                                                              daily_diag_mod_aug],
    ['New diagnoses Small easing of restrictions on July 15'] + [int(val) for val in
                                                                                              daily_diag_small_sep],
    ['New diagnoses Moderate easing of restrictions on July 15'] + [int(val) for val in
                                                                                                 daily_diag_mod_sep],
    ['New diagnoses No changes to current lockdown restrictions'] + [int(val) for val in daily_diag_no_release]]
worksheet2.add_table('A1:FO17', {'data': daily_projections})
workbook.close()
