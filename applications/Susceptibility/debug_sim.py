import sys
sys.path.append('../../')
import outbreak
from outbreak.main import run_australia_outbreak, run_australia_test_prob, get_australia_outbreak
import sciris as sc
import pandas as pd
import numpy as np


packages = outbreak.load_packages()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, pop_infected=1, n_days=31)
# sim1 = run_australia_outbreak(1, params, packages['Relax 1'])
# sim2 = run_australia_test_prob(1, params, packages['No policies'], symp_prob=1.0,asymp_quar_prob=1.0)

import covasim as cv
from pathlib import Path
import covasim as cv
import pandas as pd
import contacts as co
import data
import parameters
import policy_updates
import sciris as sc
import utils
import functools
import numpy as np
import sys

base_sim = get_australia_outbreak(1, params, packages['Pre outbreak'])

#### RUN

sim = sc.dcp(base_sim)

# Remove the testing intervention
sim.pars['interventions'] = [x for x in sim.pars['interventions'] if not isinstance(x, cv.test_num)]

# Add a test_prob intervention
sim.pars['interventions'].append(cv.test_prob(
    symp_prob=0.2,
    asymp_prob=0,
    symp_quar_prob=1,
    asymp_quar_prob=1,
))

# sim.pars['iso_factor'] = 0
# sim.pars['quar_factor'] = {k:0 if k=='H' else 0 for k in sim.pars['quar_factor'] }

sim.run()
sim.results['cum_infections']

