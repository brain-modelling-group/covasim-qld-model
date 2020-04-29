"""
Show contacts within different layers
"""
import covasim as cv
import sciris as sc
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import covasim as cv
import load_pop, load_parameters
import sciris as sc
import numpy as np
import matplotlib
sns.set(font_scale=2)

# load parameters
state, start_day, end_day, n_days, date, folder, file_path, data_path, databook_path, popfile, pars, metapars, \
population_subsets, trace_probs, trace_time = load_parameters.load_pars()

# Process and read in data
sd, i_cases, daily_tests = load_parameters.load_data(databook_path=databook_path, start_day=start_day,
                                                         end_day=end_day, data_path=data_path)
pars['pop_size'] = 200

popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'],
                                              contact_numbers=pars['contacts'], population_subsets=population_subsets)
sc.saveobj(popfile, popdict)

s_struct, w_struct, c_struct = [],[],[]
h_struct = np.zeros(6)
for i in range(0,pars['pop_size']-1):
    s_struct.append(len(popdict['contacts'][i]['S']) + 1)
    w_struct.append(len(popdict['contacts'][i]['W']) + 1)
    c_struct.append(len(popdict['contacts'][i]['C']) + 1)
    h_struct[len(popdict['contacts'][i]['H'])] += 1
h_struct / np.array((1, 2, 3, 4, 5, 6)) # account for over counting of households
fig_pop, axs = matplotlib.pyplot.subplots(3, 2)
axs[0, 0].hist(popdict['age'], bins=max(popdict['age'])-min(popdict['age']))
axs[0, 0].set_title("Age distribution of model population")
axs[0, 1].bar(np.array((1,2,3,4,5,6)),h_struct)
axs[0, 1].set_title("Household size distribution")
axs[1, 0].hist(s_struct, bins=max(s_struct)-min(s_struct))
axs[1, 0].set_title("School size distribution")
axs[1, 1].hist(w_struct, bins=max(w_struct)-min(w_struct))
axs[1, 1].set_title("Work size distribution")
axs[2, 0].hist(c_struct, bins=max(c_struct)-min(c_struct))
axs[2, 0].set_title("Community size distribution")
# Create sim
sim = cv.Sim(pars=pars)
sim.initialize(load_pop=True, popfile=popfile)

fig = plt.figure(figsize=(8,8))

mapping = dict(H='Households', S='Schools', W='Work', transport='Public transport')

for i, layer in enumerate(['H', 'S', 'W', 'transport']):
    ax = plt.subplot(2,2,i+1)
    hdf = sim.people.contacts[layer].to_df()
    hdf1 = set(list(sim.people['uid']))
    G = nx.Graph()
    G.add_nodes_from(hdf1)#set(list(hdf['p1'].unique()) + list(hdf['p2'].unique())))
    f = hdf['p1']
    t = hdf['p2']
    G.add_edges_from(zip(f,t))
#    G.nodes['color'] =
    print('Nodes:', G.number_of_nodes())
    print('Edges:', G.number_of_edges())

    nx.draw(G, ax=ax, node_size=5, width=1, scale=200, node_color = sim.people['age'], cmap = 'jet')
    ax.set_title(mapping[layer])
plt.savefig(fname='networks.png')
plt.show()

