#!/usr/bin/env python
# coding: utf-8
"""
Calculate moving average for new tests
=============================================================
"""

import numpy as np
import pandas as pd


# Load empirical data
inputs_folder = 'inputs'
input_data = 'qld_epi_data_qld-health.csv'
output_data = 'qld_epi_data_qld-health_mav9.csv'

# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

xx = data['new_tests_raw'].astype(float)

num_days = 9
xx = np.convolve(xx, np.ones((num_days, ))/num_days, mode='same')

data['new_tests'] = np.round(xx)


data.to_csv("/".join((inputs_folder, output_data)))
