from pathlib import Path
import pandas as pd

resultsdir = Path(__file__).parent/'results_400'
results = []
for result in resultsdir.rglob('calibrate_*.csv'):
    print(result)
    df = pd.read_csv(result)
    df['seed'] = int(result.stem.split('_')[1])
    results.append(df)