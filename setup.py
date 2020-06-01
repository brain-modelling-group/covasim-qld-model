import covasim as cv
import contacts as co
import numpy as np
import parameters
import scenarios
import sciris as sc
import utils


def get_popdict(params, popfile, load_popdict, save_popdict):
    if load_popdict:
        popdict = sc.loadobj(popfile)
    else:
        contacts, ages, uids = co.make_contacts(params)

        # create the popdict object
        popdict = {}
        popdict['contacts'] = contacts
        popdict['age'] = ages
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


def setup(db_name,
          epi_name,
          setting,
          policy_change=None,
          pars=None,
          metapars=None,
          load_popdict=True,
          save_popdict=True,
          pop_name='popfile.obj'):

    # for reproducible results
    set_rand_seed(metapars)

    # get file paths
    db_path, epi_path, pop_path = utils.get_file_paths(db_name=db_name,
                                                       epi_name=epi_name,
                                                       pop_name=pop_name)

    # setup parameters
    params = parameters.setup_params(db_path, setting, metapars)
    params.update_pars(pars)  # use user input parameters

    # setup population dictionary
    popdict = get_popdict(params=params,
                          popfile=pop_path,
                          load_popdict=load_popdict,
                          save_popdict=save_popdict)

    # setup simulation
    sim = cv.Sim(pars=params.pars,
                 datafile=epi_path,
                 popfile=pop_path,
                 pop_size=params.pars['pop_size'])
    sim.initialize(save_pop=False,
                   load_pop=True,
                   popfile=pop_path)

    # setup scenarios
    scens = scenarios.define_scenarios(policy_change=policy_change, params=params, popdict=popdict)
    scens = cv.Scenarios(sim=sim, basepars=pars, metapars=metapars, scenarios=scens)

    return scens
