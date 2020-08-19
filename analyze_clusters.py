import covasim as cv
import numpy as np
from functools import partial
import outbreak


def get_clusters(sim: cv.Sim, t: int) -> dict:
    """
    Get observed infection clusters

    A cluster is a collection of people linked by known disease transmission, where
    only one person has an unknown (or seed) infection. It is essentially a tree starting
    with an index case.

    In CovaSim there is exactly one 'ground truth' cluster per seed infection. However,
    due to some people being undiagnosed and some contacts not being traced, it might be
    the case that different members of a large cluster are diagnosed independently and
    treated as index cases of their own clusters until the intermediate cases linking
    the infections is found. Similarly, a cluster won't yet include anyone that hasn't
    been diagnosed.

    Note that in cases where a household has 2 members that were infected by different
    clusters, and then a third household member becomes infected, in practice these might
    be considered the cluster merging if the source of the infection was not known.
    On the other hand, genetic testing would reveal which of the two clusters infected the
    third household member. Since CovaSim captures who the infection source was, the clusters
    will never merge and the third household member would be definitively assigned to the
    cluster of the person that infected them.

    Clusters are labeled using the one index case in each cluster. This means that as clusters
    connect, the labelling remains stable.

    Clusters are generated based on diagnoses and tracing at time index `t` so for instance
    if the trace time is 5 days, it will be 5 days after infection before the edge is used
    in the cluster graph.

    Args:
        sim: A cv.Sim obj
        t: Time index at which to check diagnosed and traced contacts

    Returns: {person_index: {indices of cluster members}} e.g. {1:{1,2,3}}

    """

    import networkx as nx

    G = nx.DiGraph()

    for infection in sim.people.infection_log:
        # if infection['date'] > t:
        #     break
        ind = infection['target']
        G.add_node(ind, date_known_contact=sim.people.date_known_contact[ind],date_diagnosed=sim.people.date_diagnosed[ind])
        if infection['source'] is not None:
            G.add_edge(infection['source'], infection['target'], date=infection['date'])

    def filter_diagnosed_nodes(n1, G, t):
        # Return True if the person was diagnosed by day t
        return G.nodes[n1]['date_diagnosed'] <= t

    def filter_known_edges(n1,n2,G, t):
        # Return True if the infection edge was known by day t
        #
        return G.nodes[n2]['date_known_contact'] <= t

    # diagnosed_graph = nx.subgraph_view(G,partial(filter_diagnosed_nodes,G=G,t=t)) # Include everyone diagnosed but don't filter by tracing
    traced_graph = nx.subgraph_view(G,partial(filter_diagnosed_nodes,G=G,t=t),partial(filter_known_edges,G=G,t=t)) # Filter by both diagnosis and tracing

    clusters = {}
    for cluster in nx.weakly_connected_components(traced_graph):
        for node in cluster:
            if traced_graph.in_degree[node] == 0:
                label = node
                break
        else:
            raise Exception('No cluster root was identified')

        if label in clusters:
            raise Exception('Multiple clusters with the same root were found')
        clusters[label] = cluster

    return clusters

def plot_clusters(sim: cv.Sim, max_clusters=200):
    """
    Plot clusters for a simulation

    Some simulations might have many clusters that would make plotting with matplotlib slow.
    The `max_clusters` argument will prevent accidental rendering of figures if there are
    are too many clusters. It's purely for performance, it could be safely set to `np.inf`
    if desired.

    Args:
        sim: The sim to plot clusters for
        max_clusters: An error is raised if there are more than this many clusters

    Returns: A Matplotlib figure

    """

    cluster_sizes = {i: np.zeros(sim.npts) for i in range(sim.n)}
    for t in range(sim.npts):
        clusters = get_clusters(sim, t)
        for idx, members in clusters.items():
            cluster_sizes[idx][t] = len(members)

    cluster_sizes = {k:v for k,v in cluster_sizes.items() if np.any(v)}

    if len(cluster_sizes) == 0:
        raise Exception('No clusters were found (not enough infections?)')

    if len(cluster_sizes) > max_clusters:
        raise Exception('Too many clusters to plot, increase `max_clusters` if desired (plotting may be slow)')

    fig, ax = plt.subplots()
    ax.stackplot(sim.tvec, cluster_sizes.values(),colors=sc.gridcolors(len(cluster_sizes)))
    ax.set_xlabel('Day')
    ax.set_ylabel('Infections')
    ax.set_title('Cumulative infections, coloured by cluster')

    return fig


if __name__ == '__main__':
    # Running this file directly produces an example Sim with contact tracing enabled
    # and uses it to plot clusters
    import covasim.utils as cvu
    import matplotlib.pyplot as plt
    import sciris as sc

    packages = outbreak.load_packages()
    params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, n_infected=2, n_days=60)

    # The commands below artifically increase clustering for development purposes
    params.extrapars['trace_probs'] = {k: 1 for k in params.extrapars['trace_probs']}  # Perfect contact tracing
    params.extrapars['trace_time'] = {k: 1 for k in params.extrapars['trace_time']} # Instant contact tracing
    params.test_prob = {
        'symp_prob': 1.0,  # Someone who has symptoms has this probability of testing on any given day
        'asymp_prob': 0.00,  # Someone who is asymptomatic has this probability of testing on any given day
        'symp_quar_prob': 1.0,  # Someone who is quarantining and has symptoms has this probability of testing on any given day
        'asymp_quar_prob': 1.0,
        'test_delay': 2,  # Number of days for test results to be processed
        'swab_delay': 2,  # Number of days people wait after symptoms before being tested
        'isolation_threshold': 0,
        'leaving_quar_prob': 0.0,
    }

    sim = outbreak.get_australia_outbreak(1, params, packages['Large events only'])
    # sim.pars['interventions'].insert(0,cv.test_prob(1,1,1,1))
    sim.run()

    plot_clusters(sim, max_clusters=np.inf)
