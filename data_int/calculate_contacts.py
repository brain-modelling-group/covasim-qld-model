import pandas as pd
import numpy as np

spreadsheet = 'input_data.xlsx'

age_sex = pd.read_excel(spreadsheet, sheet_name='age_sex', index_col=[0,1], header=0)
household_data = pd.read_excel(spreadsheet, sheet_name='households', index_col=0, header=0)
layers_data = pd.read_excel(spreadsheet, sheet_name='layers-main', header=[0,1], index_col=0)
layers_other = pd.read_excel(spreadsheet, sheet_name='layers-other', header=[0,1], index_col=0)
polices = pd.read_excel(spreadsheet, sheet_name='policies', header=[0,1], index_col=0)
other_data = pd.read_excel(spreadsheet, sheet_name='other_par', index_col=0)
contact_home = pd.read_excel(spreadsheet, sheet_name='contact matrices-home', index_col=[0,1], header=0)
contact_school = pd.read_excel(spreadsheet, sheet_name='contact matrices-school', index_col=[0,1], header=0)
contact_work = pd.read_excel(spreadsheet, sheet_name='contact matrices-work', index_col=[0,1], header=0)
contact_other = pd.read_excel(spreadsheet, sheet_name='contact matrices-other', index_col=[0,1], header=0)

countries = list(other_data.index)
age_groups = list(age_sex.columns)[0:16]

for i in countries:

    age_sex.loc[(i, 'Total'), :] = age_sex.loc[(i, 'Male'), :] + age_sex.loc[(i, 'Female'), :]
    age_sex.loc[(i, 'Proportion'), :] = age_sex.loc[(i, 'Total'), :]/age_sex.loc[(i, 'Total'), 'Total']

    for j in age_groups:
        contact_home.loc[(i, j), 'Total'] = sum(contact_home.loc[(i, j), age_groups])
        contact_school.loc[(i, j), 'Total'] = sum(contact_school.loc[(i, j), age_groups])
        contact_work.loc[(i, j), 'Total'] = sum(contact_work.loc[(i, j), age_groups])
        contact_other.loc[(i, j), 'Total'] = sum(contact_other.loc[(i, j), age_groups])

    layers_data.loc[i, ('H', 'contacts')] = (round(sum(
        np.array(age_sex.loc[(i, 'Proportion'), age_groups]) * np.array(contact_home.loc[(i, age_groups), 'Total']))))
    layers_data.loc[i, ('S', 'contacts')] = (round(sum(
        np.array(age_sex.loc[(i, 'Proportion'), age_groups]) * np.array(contact_school.loc[(i, age_groups), 'Total']))))
    layers_data.loc[i, ('W', 'contacts')] = (round(sum(
        np.array(age_sex.loc[(i, 'Proportion'), age_groups]) * np.array(contact_work.loc[(i, age_groups), 'Total']))))
    layers_data.loc[i, ('C', 'contacts')] = (round(sum(
        np.array(age_sex.loc[(i, 'Proportion'), age_groups]) * np.array(contact_other.loc[(i, age_groups), 'Total']))))

writer = pd.ExcelWriter('input_data.xlsx', engine='xlsxwriter')
age_sex.to_excel(writer, sheet_name='age_sex')
household_data.to_excel(writer, sheet_name='households')
layers_data.to_excel(writer, sheet_name='layers-main')
layers_other.to_excel(writer, sheet_name='layers-other')
polices.to_excel(writer, sheet_name='policies')
other_data.to_excel(writer, sheet_name='other_par')
contact_home.to_excel(writer, sheet_name='contact matrices-home')
contact_school.to_excel(writer, sheet_name='contact matrices-school')
contact_work.to_excel(writer, sheet_name='contact matrices-work')
contact_other.to_excel(writer, sheet_name='contact matrices-other')
writer.save()
