import pandas as pd

states = ['vic','nsw','qld']

def scrape_data(metric, column, fname):
    dfs = []
    for state in states:
        df = pd.read_html(f'https://covidlive.com.au/report/{metric.lower()}/{state}', attrs={'class': metric.upper()})[0]
        df['DATE'] = pd.to_datetime(df['DATE'] + ' 2020', format='%a %d %b %Y')  # Parse dates
        df = df.replace({'-':None})
        df = df.rename({'DATE': 'Date', column: state}, axis=1).reindex(['Date', state], axis=1).set_index('Date')
        dfs.append(df)
    pd.concat(dfs, axis=1).to_csv(fname)

scrape_data('daily-cases','NET','new_cases.csv')
scrape_data('daily-tests','NET','new_tests.csv')
scrape_data('daily-active-cases','ACTIVE','active_cases.csv')
scrape_data('daily-hospitalised','HOSP','hospitalised.csv')
scrape_data('daily-hospitalised','ICU','icu.csv')


