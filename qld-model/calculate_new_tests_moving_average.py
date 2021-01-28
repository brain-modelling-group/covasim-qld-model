#!/usr/bin/env python
# coding: utf-8
"""
Calculate moving average for new tests
=============================================================
"""

import numpy as np
import pandas as pd
import covasim.misc as cvm


# Load empirical data
inputs_folder = 'inputs'
input_data = 'qld_health_epi_data_calibration.csv'

# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

xx = data['new_tests_raw'].astype(float)

num_days = 15
xx = np.convolve(xx, np.ones((num_days, ))/num_days, mode='same')

data['new_tests'] = np.round(xx)


data.to_csv("/".join((inputs_folder, input_data)))
