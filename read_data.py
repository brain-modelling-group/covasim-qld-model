'''
Script to load demographic data
'''

import xlrd
import numpy as np


def import_demo(spreadsheet):
    workbook = xlrd.open_workbook(spreadsheet)

    age_par = {}
    worksheet = workbook.sheet_by_name('age_sex')
    for i in range(1, 19):
        age_par.update({worksheet.cell(i,0).value: {'male': worksheet.cell(i,1).value, 'female': worksheet.cell(i,2).value}})

    house_par = {}
    worksheet = workbook.sheet_by_name('households')
    for i in range(1,7):
        house_par.update({worksheet.cell(i,0).value: worksheet.cell(i,1).value})

    house_str_par = {}
    worksheet = workbook.sheet_by_name('household_structure')
    for i in range(1,14):
        house_str_par.update({worksheet.cell(i,0).value: worksheet.cell(i,1).value})

    worksheet = workbook.sheet_by_name('schools')
    school_par1 = {}
    for i in range(1,10):
        school_par1.update({worksheet.cell(i,1).value: worksheet.cell(i,2).value})
    school_par2 = {}
    for i in range(10,21):
        school_par2.update({worksheet.cell(i,1).value: worksheet.cell(i,2).value})
    school_par = {'primary schools': school_par1, 'secondary schools': school_par2, 'special schools': worksheet.cell(21, 2).value}

    work_par = {}
    worksheet = workbook.sheet_by_name('workplaces')
    for i in range(1,6):
        work_par.update({worksheet.cell(i,0).value: worksheet.cell(i,1).value})

    return {'age dist': age_par, 'households': house_par, 'household structure': house_str_par, 'school size': school_par, 'workplace size': work_par}


def import_contact(spreadsheet):
    workbook = xlrd.open_workbook(spreadsheet)
    worksheet = workbook.sheet_by_name('contact matrices-home')
    home = np.array([[worksheet.cell(i,j).value for j in range(1, 17)] for i in range(1,17)])
    home = (home + home.transpose())/2  # make symmetric

    worksheet = workbook.sheet_by_name('contact matrices-work')
    work = np.array([[worksheet.cell(i,j).value for j in range(1, 17)] for i in range(1,17)])
    work = (work + work.transpose()) / 2  # make symmetric

    worksheet = workbook.sheet_by_name('contact matrices-school')
    school = np.array([[worksheet.cell(i,j).value for j in range(1, 17)] for i in range(1,17)])
    school = (school + school.transpose()) / 2  # make symmetric

    worksheet = workbook.sheet_by_name('contact matrices-other')
    other = np.array([[worksheet.cell(i,j).value for j in range(1, 17)] for i in range(1,17)])
    other = (other + other.transpose()) / 2  # make symmetric

    return home, work, school, other


def import_impcases(spreadsheet, state):
    workbook = xlrd.open_workbook(spreadsheet)
    worksheet = workbook.sheet_by_name(state)
    cases = np.array([[worksheet.cell(i, 1).value for i in range(1, 82)],
                      [worksheet.cell(i, 2).value for i in range(1, 82)]])
    return cases


spreadsheet = 'demographic.xlsx'
par_dict = import_demo(spreadsheet)
home, work, school, other = import_contact(spreadsheet)

spreadsheet = 'imported-cases.xlsx'
i_cases = import_impcases(spreadsheet, 'Victoria')



