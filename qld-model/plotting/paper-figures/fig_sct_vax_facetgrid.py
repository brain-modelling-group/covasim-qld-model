import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="ticks")

# Create a dataset with many short random walks
rs = np.random.RandomState(4)
pos = rs.randint(-1, 2, (20, 5)).cumsum(axis=1)
pos -= pos[:, 0, np.newaxis]
step = np.tile(range(5), 20)
walk = np.repeat(range(20), 5)

df = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/sct_cluster_vax_b117_facetgrid.csv')



# Initialize a grid of plots with an Axes for each walk
grid = sns.FacetGrid(df, row="vp", col="ve", hue="vp", palette="tab20c", height=1.5)

# Draw a horizontal line to show the starting point
#grid.map(plt.axhline, y=0, ls=":")

# Draw a line plot to show the trajectory of each random walk
grid.map(plt.plot, "cluster_size", "sct_prob", marker="o")

# # Adjust the tick positions and labels
grid.set(xticks=np.arange(11), xlim=(0.5, 10.5), ylim=(0, 100), ylabel="P[SCT] (%)", xlabel="cluster size")

# Adjust the arrangement of the plots
grid.fig.tight_layout(w_pad=1)
plt.show()
