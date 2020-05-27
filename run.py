import os
import setup
import numpy as np


if __name__ == '__main__':
    np.random.seed(1) # Help with testing
    # file path
    root = os.path.dirname(os.path.abspath(__file__))

    # data location
    setting = 'victoria'
    file_name = 'vic-data'
    epidata_name = 'data/vic-epi-data.xlsx'

    # parameters & meta-parameters
    pars = {'pop_size': 100,
            'beta': 0.11,
            'n_days': 60}
    metapars = {'n_runs': 10,
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
