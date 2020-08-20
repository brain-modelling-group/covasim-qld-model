# Load scenario results and process into a dataframe/csv

from pathlib import Path
import pandas as pd
import sciris as sc

scendir = Path(__file__).parent/'scenarios'

records = []

for statsfile in scendir.rglob('*.stats'):
    scenario_name = statsfile.parent.name
    package_name = statsfile.stem
    stats = sc.loadobj(statsfile)
    for d in stats:
        d['scenario_name'] = scenario_name
        d['package_name'] = package_name
    records += stats

df = pd.DataFrame.from_records(records)
df.set_index(['scenario_name','package_name'],inplace=True)
df.to_csv(scendir/'results.csv')


