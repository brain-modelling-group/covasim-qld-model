import pandas as pd

repo = 'C:/Users/anna.palmer/Documents/GitHub/covid19za/data/'
provinces = ['EC', 'FS', 'GP', 'KZN', 'LP', 'MP', 'NC', 'NW', 'WC']

cases = pd.read_csv(repo + 'covid19za_provincial_cumulative_timeline_confirmed.csv')[['date'] + provinces]

cases = pd.melt(cases, id_vars=['date'], value_vars=provinces,
                var_name='location', value_name='cum_infections')

deaths = pd.read_csv(repo + 'covid19za_provincial_cumulative_timeline_deaths.csv')[['date'] + provinces]

deaths = pd.melt(deaths, id_vars=['date'], value_vars=provinces,
                var_name='location', value_name='cum_deaths')

tests = pd.read_csv(repo + 'covid19za_provincial_cumulative_timeline_testing.csv')[['date'] + provinces]

tests = pd.melt(tests, id_vars=['date'], value_vars=provinces,
                var_name='location', value_name='cum_tests')

# Combine into one dataset
cases = cases.set_index(['date', 'location'])
deaths = deaths.set_index(['date', 'location'])
tests = tests.set_index(['date', 'location'])

epi_data = cases.join(deaths)
epi_data = epi_data.join(tests)

epi_data = epi_data.reset_index()
epi_data.loc[0, 'cum_deaths'] = 0
epi_data.loc[0, 'cum_tests'] = 0

# Get rid of the NAs
for i in range(1, len(epi_data)):
    if epi_data.loc[i, 'location']==epi_data.loc[i-1, 'location']:

        if epi_data['cum_infections'].isna()[i]:
            epi_data.loc[i, 'cum_infections'] = epi_data.loc[i-1, 'cum_infections']

        if epi_data['cum_deaths'].isna()[i]:
            epi_data.loc[i, 'cum_deaths'] = epi_data.loc[i-1, 'cum_deaths']

        if epi_data['cum_tests'].isna()[i]:
            epi_data.loc[i, 'cum_tests'] = epi_data.loc[i-1, 'cum_tests']

    else:

        if epi_data['cum_infections'].isna()[i]:
            epi_data.loc[i, 'cum_infections'] = 0

        if epi_data['cum_deaths'].isna()[i]:
            epi_data.loc[i, 'cum_deaths'] = 0

        if epi_data['cum_tests'].isna()[i]:
            epi_data.loc[i, 'cum_tests'] = 0

new = pd.DataFrame(columns=['date', 'location', 'new_diagnoses', 'new_deaths', 'new_tests'])
new = new.set_index(['date', 'location'])
for i in provinces:
    epi_data2 = epi_data.loc[epi_data['location']==i]
    epi_data2 = epi_data2.set_index(['date', 'location'])
    new2 = epi_data2.diff().rename(columns={'cum_infections': 'new_diagnoses', 'cum_deaths': 'new_deaths', 'cum_tests': 'new_tests'})
    new = pd.concat([new, new2])

new = new.reset_index()
epi_data = pd.merge_asof(epi_data, new, on='date', by='location', left_index=True, right_index=True)
epi_data = epi_data.fillna(0)
num = epi_data._get_numeric_data()
num[num<0] = 0

epi_data['daily_imported_cases'] = 0

epi_data.to_csv('epi_data_sa.csv', index=False)

