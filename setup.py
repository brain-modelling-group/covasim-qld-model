import covasim as cv
import contacts as co
import numpy as np
import parameters
import scenarios
import sciris as sc


def get_popdict(params, popfile, load_popdict, save_popdict):
    if load_popdict:
        popdict = sc.loadobj(popfile)
    else:
        contacts, ages, uids = co.make_contacts(params)

        # create the popdict object
        popdict = {}
        popdict['contacts'] = contacts
        popdict['age'] = ages  # TODO: check this
        popdict['uid'] = uids
        if save_popdict:
            sc.saveobj(popfile, popdict)

    return popdict


def set_rand_seed(metapars):
    if metapars.get('seed') is None:
        seed = 1
    else:
        seed = metapars['seed']
    np.random.seed(seed)


def setup(root,
          databook_name,
          epidata_name,
          setting,
          policy_change=None,
          pars=None,
          metapars=None,
          load_popdict=True,
          save_popdict=True,
          popfile='data/popfile_v2.obj'):

    # for reproducible results
    set_rand_seed(metapars)

    # setup parameters
    params = parameters.setup_params(root, databook_name, setting, metapars)
    params.update_pars(pars)  # use user input parameters

    # setup population dictionary
    popdict = get_popdict(params=params,
                          popfile=popfile,
                          load_popdict=load_popdict,
                          save_popdict=save_popdict)

    # setup simulation
    sim = cv.Sim(pars=params.pars,
                 datafile=epidata_name,
                 popfile=popfile,
                 pop_size=params.pars['pop_size'])
    sim.initialize(save_pop=False,
                   load_pop=True,
                   popfile=popfile)

    # setup scenarios
    scens = scenarios.define_scenarios(policy_change=policy_change, params=params, popdict=popdict)
    scens = cv.Scenarios(sim=sim, basepars=pars, metapars=metapars, scenarios=scens)

    return scens
