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
            'beta': 0.05,
            'n_days': 60}

    metapars = {'n_runs': 10,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # popdict settings
    load_popdict = False
    save_popdict = True
    popfile = 'data/popfile_v2.obj'

    policy_change = {'relax comm': {'replace': (['communication'], [['comm_relax']], [[20]])},
                     'turn off comm': {'turn_off': (['communication'], [20])}}

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

    scens.run()

    plot.plot_scens(scens, do_save=False)
