'''
Load Australian epi data
'''

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop, os
import numpy as np
import networkx as nx
import seaborn as sns


dirname = os.path.dirname(os.path.abspath(__file__))

def get_distributions(databook_path):
    import pandas as pd
    import os
    """
        Pull household and age distributions from input data
    """
    dirname = os.path.dirname(os.path.abspath(__file__))
    reference = pd.read_excel(dirname + '/' + databook_path, sheet_name='age_sex')['Total']
    reference.iloc[0:18] = 0
    reference.iloc[18:28] = reference.iloc[18:28] * np.linspace(0.1, 1, 10)

    household_dist = pd.read_excel(dirname + '/' + databook_path, sheet_name='households')['no. households']  # Household size distribution
    # calculate the population size generated by the household data, so that the household distribution can be scaled based no model population
    household_dist.index = household_dist.index + 1  # Convert from index to number of people in the household (starting at 1)
    # Calculate the number of households we need to fill to meet the population size requirement
    #n_households = (pop_size * (household_dist / sum(household_dist.index * household_dist))).round().astype(int)
    #n_households[1] += pop_size - sum(n_households * n_households.index)  # Adjust single-person households to fill the gap

    age_dist_vals = pd.read_excel(dirname + '/' + databook_path, sheet_name='age_sex')['Total']  # Household size distribution
    age_dist = np.array((age_dist_vals.values))
    return household_dist.values, age_dist


verbose    = 1
seed       = 1

pars, metapars, extra_pars, population_subsets = load_parameters.load_pars()
sd, extra_pars['i_cases'], extra_pars['daily_tests'] = load_parameters.load_data(databook_path=extra_pars['databook_path'],
                                                                                         start_day=pars['start_day'], end_day=extra_pars['end_day'], data_path=extra_pars['data_path'])

popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'],
                                              contact_numbers=pars['contacts'], population_subsets=population_subsets)
sc.saveobj(extra_pars['file_path'] + 'temp_pop', popdict)

house_dist, age_dist = get_distributions(extra_pars['databook_path'])

s_struct, w_struct, c_struct, church_struct = [],[],[],[]
h_struct = np.zeros(6)
age_struct = np.zeros(115)
for i in range(0,pars['pop_size']-1):
    if (popdict['age'][i] >= 5 and popdict['age'][i] <= 18):
        s_struct.append(len(popdict['contacts'][i]['S']) + 1)
    if (popdict['age'][i] >= 18 and popdict['age'][i] <= 65):
        w_struct.append(len(popdict['contacts'][i]['W']) + 1)
    c_struct.append(len(popdict['contacts'][i]['C']) + 1)
    if 'Church' in popdict['contacts'][i]:
        church_struct.append(len(popdict['contacts'][i]['Church']) + 1)
    h_struct[len(popdict['contacts'][i]['H'])] += 1
    age_struct[popdict['age'][i]] += 1
h_struct = h_struct / np.array((1, 2, 3, 4, 5, 6)) # account for over counting of households
fig_pop1, axs1 = matplotlib.pyplot.subplots(2, 2, **{'figsize': (10,8)})
axs1[0, 0].bar(np.arange(0, 116), age_dist)
axs1[0, 0].set_title("Age distribution of Australian population")
axs1[0, 1].bar(np.arange(0, 115), age_struct)
axs1[0, 1].set_title("Age distribution of model population")
axs1[1, 0].bar(np.array(('1','2','3','4','5','6+')),house_dist)
axs1[1, 0].set_title("Australian household size distribution")
axs1[1, 1].bar(np.array(('1','2','3','4','5','6+')),h_struct)
axs1[1, 1].set_title("Model household size distribution")
plt.savefig(fname=dirname + '/figures/compare_distributions.png')
plt.close()
fig_pop2, axs2 = matplotlib.pyplot.subplots(3, 1, **{'figsize': (10,10)})
axs2[0].hist(s_struct, bins=max(s_struct)-min(s_struct))
axs2[0].set_title("School-contact size distribution")
axs2[1].hist(w_struct, bins=max(w_struct)-min(w_struct))
axs2[1].set_title("Work-contact size distribution")
axs2[2].hist(c_struct, bins=max(c_struct)-min(c_struct))
axs2[2].set_title("Community-contact size distribution")

plt.savefig(fname=dirname + '/figures/distributions.png')


## Mixing matrix
mixing_matrix, bin_lower, bin_upper = load_pop.get_mixing_matrix(extra_pars['databook_path'], 'contact matrices-home')
mixing_matrix = mixing_matrix.iloc[::-1]

g = sns.heatmap(mixing_matrix)
fig2 = g.get_figure()
fig2.savefig(dirname + "/figures/H_mixing.png")
#fig2.show()


## Networks
pars['pop_size'] = 200
popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'],
                                              contact_numbers=pars['contacts'], population_subsets=population_subsets)
sc.saveobj(extra_pars['file_path'] + 'temp_pop', popdict)
sim = cv.Sim(pars=pars)
sim.initialize(load_pop=True, popfile=extra_pars['file_path'] + 'temp_pop')

fig3 = plt.figure(figsize=(8,8))
mapping = dict(H='Households', S='Schools', W='Work', transport='Public transport')
for i, layer in enumerate(['H', 'S', 'W', 'transport']):
    ax = plt.subplot(2,2,i+1)
    hdf = sim.people.contacts[layer].to_df()
    hdf1 = set(list(sim.people['uid']))
    G = nx.Graph()
    G.add_nodes_from(hdf1)#set(list(hdf['p1'].unique()) + list(hdf['p2'].unique())))
    f = hdf['p1']
    t = hdf['p2']
    G.add_edges_from(zip(f, t))
    node_list = list(nx.nodes(G))
    isolates = list(nx.isolates(G))
    if layer == 'H':
        connected = node_list
    else:
        connected = [x for x in node_list if x not in isolates]
        G.remove_nodes_from(list(nx.isolates(G)))
#    G.nodes['color'] =
    print('Nodes:', G.number_of_nodes())
    print('Edges:', G.number_of_edges())
    pos = nx.spring_layout(G, k=0.3, iterations=50)

    nx.draw(G, ax=ax, node_size=5, width=0.9, scale=200, fontsize=10, node_color = sim.people['age'][connected], cmap = 'jet', pos=pos)
    ax.set_title(mapping[layer])
plt.savefig(fname=dirname + '/figures/networks.png')
plt.show()