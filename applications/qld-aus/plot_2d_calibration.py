import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
import covasim.misc as cvm


fig, axs = plt.subplots(nrows=2, ncols=7, figsize=(9, 6),
                        subplot_kw={'xticks': [], 'yticks': []})


data = np.load("recalibration_2d_pse_2020-01-15_2020-03-30_no-conv.npz")
yy = data['res']

x = data['x']
y = data['y']

yy_med = np.percentile(yy, q=50, axis=0)
yy_q1 = np.percentile(yy, q=25, axis=0)
yy_q3 = np.percentile(yy, q=75, axis=0)

ax00 = axs[0, 0].imshow(yy_med, interpolation='none', origin='lower', extent = [0, 1, 0, 1])
ax01 = axs[0, 1].imshow(0.1+np.log10(yy_med), interpolation='none', origin='lower', extent = [0, 1, 0, 1])

ax02 = axs[0, 2].imshow(yy_q1, interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1])
ax03 = axs[0, 3].imshow(np.log10(yy_q1), interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1])

ax04 = axs[0, 4].imshow(yy_q3, interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1])
ax05 = axs[0, 5].imshow(np.log10(yy_q3), interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1])
ax06 = axs[0, 6].imshow(yy_q3+yy_q1+yy_med, interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1])

ax10 = axs[1, 0].imshow(yy_med, interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=1)
ax11 = axs[1, 1].imshow(0.1+np.log10(yy_med), interpolation='none', origin='lower', extent = [0, 1, 0, 1])

ax12 = axs[1, 2].imshow(yy_q1, interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1], vmax=1.0)
ax13 = axs[1, 3].imshow(np.log10(yy_q1), interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1])

ax14 = axs[1, 4].imshow(yy_q3, interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1], vmax=4.0)
ax15 = axs[1, 5].imshow(np.log10(yy_q3), interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1])
ax16 = axs[1, 6].imshow(yy_q3+yy_q1+yy_med, interpolation='none', aspect = 'equal', origin='lower', extent = [0, 1, 0, 1], vmax=2)

#fig.colorbar(ax00, ax=axs[0,0])

#plt.imshow(2*yy_std+yy_med, interpolation='none', aspect = 'equal', origin='lower', vmax = 5)

axs[1,6].set_xticks([0.0, 0.5, 1.0])
axs[1,6].set_xticklabels(["1", "12.5", "25"])
axs[1,6].set_yticks([0.0, 0.5, 1.0])
axs[1,6].set_yticklabels(["0.01", "0.015", "0.03"])
plt.xlabel('num seed infections')
plt.ylabel('beta')


titles = ['median error', 'log10(median error)', 'Q1-error', 'log10(Q1-error)', 'Q3-error', 'log10(Q3-error)', 'Q1+Q2+Q3',
          'median error \nvmax=1', '-', 'Q1-error \nvmax=0.0', '-', 'Q3-error \nvmax=4.0', '-', 'Q1+Q2+Q3\nvmax=2.0']

for ax, im, this_title in zip(axs.flat, [ax00, ax01, ax02, ax03, ax04, ax05, ax06, ax10, ax11, ax12, ax13, ax14, ax15, ax16], titles):
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.02)
    plt.colorbar(im, cax=cax)
    ax.set_title(str(this_title))


# # Load empirical data
# inputs_folder = 'inputs'
# input_data = 'qld_health_epi_data.csv'

# # Load data
# data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

# start_data_idx = 0 # First data point of empirical data is 22-01-2020
# end_data_idx   = cvm.day('2020-03-30', start_day='2020-01-22') # Last data point of empirical data is today

# xx = data['new_locally_acquired_cases'][start_data_idx:end_data_idx]
# num_days = 3
# xx = np.convolve(xx, np.ones((num_days, ))/num_days, mode='same')
# plt.plot(yy[:, 0:10, 10], color=[0.0, 0.0, 0.0], alpha=0.4)
# plt.plot(xx, color=[1.0, 0.0, 0.0], alpha=1.0)
# plt.ylim([0, 30])
#import pdb; pdb.set_trace()

plt.tight_layout()
plt.show()


