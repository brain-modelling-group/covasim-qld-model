import xlsxwriter
import pickle
import os

dirname = os.path.dirname(__file__)
locations = ['Boston']
population = 690000
filehandler = open('runs/' + locations[0] + '.obj', 'rb')
scens = pickle.load(filehandler)

# Lower Bound: no change in restrictions
new_inf_LB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions']['best'][203:249])
new_diag_LB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][203:249])
cum_inf_LB_sep_oct = scens['scenarios'][locations[0]].results['cum_infections']['No changes to current lockdown restrictions']['best'][249]
incidence_LB_sep_oct = 100 * new_inf_LB_sep_oct * 30 / (249 - 203) / population
detected_LB_sep_oct = 100 * new_diag_LB_sep_oct * 30 / (249 - 203)
seroprev_LB_sep_oct = cum_inf_LB_sep_oct / population

new_inf_LB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_infections']['No changes to current lockdown restrictions']['best'][250:294])
new_diag_LB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][250:294])
cum_inf_LB_nov_dec = scens['scenarios'][locations[0]].results['cum_infections']['No changes to current lockdown restrictions']['best'][294]
incidence_LB_nov_dec = 100 * new_inf_LB_nov_dec * 30 / (294 - 250) / population
detected_LB_nov_dec = 100 * new_diag_LB_nov_dec * 30 / (294 - 250)
seroprev_LB_nov_dec = cum_inf_LB_nov_dec / population

# Mid Bound: small change mid- July
new_inf_MB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_infections']['Small easing of restrictions on July 15']['best'][203:249])
new_diag_MB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['Small easing of restrictions on July 15']['best'][203:249])
cum_inf_MB_sep_oct = scens['scenarios'][locations[0]].results['cum_infections']['Small easing of restrictions on July 15']['best'][249]
incidence_MB_sep_oct = 100 * new_inf_MB_sep_oct * 30 / (249 - 203) / population
detected_MB_sep_oct = 100 * new_diag_MB_sep_oct * 30 / (249 - 203)
seroprev_MB_sep_oct = cum_inf_MB_sep_oct / population

new_inf_MB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_infections']['Small easing of restrictions on July 15']['best'][250:294])
new_diag_MB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['Small easing of restrictions on July 15']['best'][250:294])
cum_inf_MB_nov_dec = scens['scenarios'][locations[0]].results['cum_infections']['Small easing of restrictions on July 15']['best'][294]
incidence_MB_nov_dec = 100 * new_inf_MB_nov_dec * 30 / (294 - 250) / population
detected_MB_nov_dec = 100 * new_diag_MB_nov_dec * 30 / (294 - 250)
seroprev_MB_nov_dec = cum_inf_MB_nov_dec / population

# Upper Bound: moderate change mid-August
new_inf_UB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_infections']['Moderate easing of restrictions on August 1']['best'][203:249])
new_diag_UB_sep_oct = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['Moderate easing of restrictions on August 1']['best'][203:249])
cum_inf_UB_sep_oct = scens['scenarios'][locations[0]].results['cum_infections']['Moderate easing of restrictions on August 1']['best'][249]
incidence_UB_sep_oct = 100 * new_inf_UB_sep_oct * 30 / (249 - 203) / population
detected_UB_sep_oct = 100 * new_diag_UB_sep_oct * 30 / (249 - 203)
seroprev_UB_sep_oct = cum_inf_UB_sep_oct / population

new_inf_UB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_infections']['Moderate easing of restrictions on August 1']['best'][250:294])
new_diag_UB_nov_dec = sum(scens['scenarios'][locations[0]].results['new_diagnoses']['Moderate easing of restrictions on August 1']['best'][250:294])
cum_inf_UB_nov_dec = scens['scenarios'][locations[0]].results['cum_infections']['Moderate easing of restrictions on August 1']['best'][294]
incidence_UB_nov_dec = 100 * new_inf_UB_nov_dec * 30 / (294 - 250) / population
detected_UB_nov_dec = 100 * new_diag_UB_nov_dec * 30 / (294 - 250)
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
     int(detected_MB_sep_oct), int(detected_LB_sep_oct), int(detected_UB_sep_oct),
     seroprev_MB_sep_oct, seroprev_LB_sep_oct, seroprev_UB_sep_oct,
     int(new_inf_MB_nov_dec), int(new_inf_LB_nov_dec), int(new_inf_UB_nov_dec),
     incidence_MB_nov_dec, incidence_LB_nov_dec, incidence_UB_nov_dec,
     int(detected_MB_nov_dec), int(detected_LB_nov_dec), int(detected_UB_nov_dec),
     seroprev_MB_nov_dec, seroprev_LB_nov_dec, seroprev_UB_nov_dec]
]

# Export results to Excel
workbook = xlsxwriter.Workbook(locations[0] + '_projections.xlsx')
worksheet = workbook.add_worksheet('Projections')
worksheet.add_table('A1:X4', {'data': projections, 'header_row': False})
workbook.close()
