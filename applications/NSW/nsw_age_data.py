import covasim as cv
import pandas as pd
import sciris as sc
import pylab as pl
import numpy as np
from matplotlib import ticker
import datetime as dt
import matplotlib.patches as patches


# Import data
agedata = pd.read_csv("covid-19-cases-by-notification-date-and-age-range.csv")

sim = cv.Sim(pop_type='hybrid')