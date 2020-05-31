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
            'n_days': 50}

    metapars = {'n_runs': 3,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # popdict settings
    load_popdict = False
    save_popdict = True
    popfile = 'data/popfile_v2.obj'

    scens = setup.setup(root=root,
                        databook_name=file_name,
                        epidata_name=epidata_name,
                        setting=setting,
                        pars=pars,
                        metapars=metapars,
                        load_popdict=load_popdict,
                        save_popdict=save_popdict,
                        popfile=popfile)

    scens.run()

    plot.plot_scens(scens, do_save=False)
    #to_plot = ['cum_infections', 'new_infections']


    fig_args = dict(figsize=(5, 5))
    this_fig_path = root + '/figures/base' + '.png'
    plot.policy_plot(scens, plot_ints=True, do_save=False, do_show=True, fig_path=this_fig_path, interval=14,
                      fig_args=fig_args,
                      font_size=8)
