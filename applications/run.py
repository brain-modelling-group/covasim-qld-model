import setup
import plot

if __name__ == '__main__':

    # file names
    setting = 'victoria'
    db_name = 'vic-data'
    epi_name = 'vic-epi-data'

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

    policy_change = {'relax comm': {'replace': (['communication'], [['comm_relax']], [[20]])},
                     'turn off comm': {'turn_off': (['communication'], [20])}}

    scens = setup.setup(db_name=db_name,
                        epi_name=epi_name,
                        setting=setting,
                        policy_change=policy_change,
                        pars=pars,
                        metapars=metapars,
                        load_popdict=load_popdict,
                        save_popdict=save_popdict)

    scens.run()

    plot.plot_scens(scens, do_save=False)
