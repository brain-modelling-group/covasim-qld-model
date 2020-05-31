import os
import setup
import plot


if __name__ == '__main__':
    # file path
    root = os.path.dirname(os.path.abspath(__file__))

    # data location
    setting = 'victoria'
    file_name = 'vic-data'
    epidata_name = 'data/vic-epi-data.xlsx'

    # parameters & meta-parameters
    pars = {'pop_size': int(2e4),
            'beta': 0.04,
            'n_days': 200}

    metapars = {'n_runs': 10,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # popdict settings
    load_popdict = False
    save_popdict = True
    popfile = 'data/popfile_v2.obj'

    policy_change = {}
    cov_values = [0.4, 0.8]

    for i, cov in enumerate(cov_values):
        policy_change['Pubs/bars open with ID (' + str(round(100*cov)) + '%)'] = {'replace': (['communication', 'outdoor2'], [['comm_relax'],['outdoor10']], [[60],[60]]),
                                                                                   'turn_off': (['pub_bar0', 'social'],[60, 60])}


    scens = setup.setup(root=root,
                        databook_name=file_name,
                        epidata_name=epidata_name,
                        setting=setting,
                        policy_change=policy_change,
                        pars=pars,
                        metapars=metapars,
                        load_popdict=load_popdict,
                        save_popdict=save_popdict,
                        popfile=popfile)
    
    for i, cov in enumerate(cov_values):
        scens.scenarios['Pubs/bars open with ID (' + str(round(100 * cov)) + '%)']['pars']['interventions'][5].layers = ['pub_bar']
        scens.scenarios['Pubs/bars open with ID (' + str(round(100 * cov)) + '%)']['pars']['interventions'][5].trace_time = {'pub_bar': 0}
        scens.scenarios['Pubs/bars open with ID (' + str(round(100 * cov)) + '%)']['pars']['interventions'][5].coverage = cov
        #scens.scenarios['Pubs/bars open with ID (' + str(round(100*cov)) + '%)']['pars']['interventions'][3].trace_probs['pub_bar'] = cov
        #scens.scenarios['Pubs/bars open with ID (' + str(round(100 * cov)) + '%)']['pars']['interventions'][3].trace_time['pub_bar'] = 0
    
    scens.run()

    fig_args = dict(figsize=(5, 5))
    this_fig_path = root + '/figures/pub_bar_ID' + '.png'
    to_plot1 = ['cum_infections', 'new_infections']

    plot.policy_plot(scens, plot_ints=True, do_save=True, do_show=True, fig_path=this_fig_path, interval=28,
                     fig_args=fig_args, font_size=8,
                     y_lim={'r_eff': 3, 'cum_infections': 12000, 'new_infections': 200},
                     legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.4)},
                     axis_args={'bottom': 0.3},
                     to_plot=to_plot1)
