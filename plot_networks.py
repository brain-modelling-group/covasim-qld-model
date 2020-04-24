"""
Show contacts within different layers
"""
import covasim as cv
import sciris as sc
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import covasim as cv
import load_pop
import sciris as sc
import numpy as np
import matplotlib
sns.set(font_scale=2)

state = 'vic'
start_day = sc.readdate('2020-03-01')
end_day   = sc.readdate('2020-06-19')
n_days    = (end_day - start_day).days
date      = '2020apr19'
folder    = f'results_{date}'
this_fig_path = folder + '/networks.png'
popfile = f'data/popfile.obj'
data_path = f'data/{state}-data-{date}.csv' # This gets created and then read in
databook_path = f'data/{state}-data.xlsx'
popfile = f'data/popfile.obj'

pars = {
    'pop_size': 300, # start with a small pool
    'pop_type': 'hybrid', # synthpops, hybrid
    'pop_infected': 0, # Infect none for starters
    'n_days': 100, # 40d is long enough for everything to play out
    'contacts': {'H': 4.0, 'S': 7, 'W': 5, 'C': 5, 'Church': 1, 'pSport': 1},
    'beta_layer': {'H': 1, 'S': 1, 'W': 1, 'C': 1, 'Church': 1, 'pSport': 1},
    'quar_eff': {'H': 1, 'S': 1, 'W': 1, 'C': 1, 'Church': 1, 'pSport': 1},
}

popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'], contact_numbers=pars['contacts'])
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

mapping = dict(H='Households', S='Schools', W='Work', C='Community')

for i, layer in enumerate(['H', 'S', 'W', 'C']):
    ax = plt.subplot(2,2,i+1)
    hdf = sim.people.contacts[layer].to_df()

    G = nx.Graph()
    G.add_nodes_from(set(list(hdf['p1'].unique()) + list(hdf['p2'].unique())))
    f = hdf['p1']
    t = hdf['p2']
    G.add_edges_from(zip(f,t))
    print('Nodes:', G.number_of_nodes())
    print('Edges:', G.number_of_edges())

    nx.draw(G, ax=ax, node_size=10, width=0.1)
    ax.set_title(mapping[layer])
plt.savefig(fname=this_fig_path)
plt.show()

