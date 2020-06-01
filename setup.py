import contacts as co
import covasim as cv
import parameters
import scenarios
import utils


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
    utils.set_rand_seed(metapars)

    # get file paths
    db_path, epi_path, pop_path = utils.get_file_paths(db_name=db_name,
                                                       epi_name=epi_name,
                                                       pop_name=pop_name)

    # setup parameters
    params = parameters.setup_params(db_path, setting, metapars)
    params.update_pars(pars)  # use user input parameters

    # setup population dictionary
    popdict = co.get_popdict(params=params,
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
