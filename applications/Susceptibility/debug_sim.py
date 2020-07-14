import sys
sys.path.append('../../')
import outbreak
from outbreak.main import run_australia_outbreak
import sciris as sc
import pandas as pd
import numpy as np


packages = outbreak.load_packages()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, pop_infected=1, n_days=31)
sim = run_australia_outbreak(1, params, packages['Relax 1'])
