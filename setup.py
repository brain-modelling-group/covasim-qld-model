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
          pars=None,
          metapars=None,
          load_popdict=True,
          save_popdict=True,
          popfile='data/popfile_v2.obj'):

    set_rand_seed(metapars)

    params = parameters.setup_params(root, databook_name, setting, metapars)
    params.update_pars(pars)

    popdict = get_popdict(params=params,
                          popfile=popfile,
                          load_popdict=load_popdict,
                          save_popdict=save_popdict)

    sim = cv.Sim(pars=params.pars,
                 datafile=epidata_name,
                 popfile=popfile,
                 pop_size=params.pars['pop_size'])
    sim.initialize(save_pop=False,
                   load_pop=True,
                   popfile=popfile)

    # TODO: currently only doing baseline scenarios
    base_scenarios, base_policies = scenarios.set_baseline(params, popdict)
    scens = cv.Scenarios(sim=sim,
                         basepars=sim.pars,
                         metapars=metapars,
                         scenarios=base_scenarios)
    return scens
