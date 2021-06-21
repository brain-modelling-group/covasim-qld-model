import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="ticks" )

df = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/sct_cluster_vax_b117_facetgrid.csv')

# Initialize a grid of plots with an Axes for cluster
grid = sns.FacetGrid(df, row="vp", col="ve", hue="vevp", palette="coolwarm_r", height=1.5)

# Draw a horizontal line to show the starting point
grid.map(plt.axhline, y=10, ls=":", c="0.5")

# Draw a line plot to show the trajectory of each random walk
grid.map(plt.plot, "cluster_size", "sct_prob", marker="o")

# # Adjust the tick positions and labels
grid.set(xticks=np.arange(11), xlim=(0.5, 10.5), ylim=(0, 102), ylabel="P[SCT] (%)", xlabel="cluster size")

# Adjust the arrangement of the plots
grid.fig.tight_layout(w_pad=1)
plt.show()
