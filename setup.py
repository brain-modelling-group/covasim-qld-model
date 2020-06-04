import contacts as co
import covasim as cv
import data
import parameters
import scenarios
import utils

def setup_scens(locations,
                db_name,
                epi_name='url',
                policy_change=None,
                user_pars=None,
                metapars=None,
                load_popdict=False,
                save_popdict=False,
                pop_name='popfile.obj'):

    # for reproducible results
    utils.set_rand_seed(metapars)

    # return data relevant to each specified location in "locations"
    all_data = data.read_data(locations=locations,
                              db_name=db_name,
                              epi_name=epi_name,
                              pop_name=pop_name)

    all_scens = {}
    for location in locations:
        loc_data = all_data[location]
        loc_pars = user_pars[location]

        params = parameters.setup_params(location=location,
                                         loc_data=loc_data,
                                         metapars=metapars,
                                         user_pars=loc_pars)

        # popdict = co.get_popdict(params=params,
        #                          popfile=pop_path,
        #                          load_popdict=load_popdict,
        #                          save_popdict=save_popdict)
        #
        # # setup simulation
        # sim = cv.Sim(pars=params.pars,
        #              datafile=epi_path,
        #              popfile=pop_path,
        #              pop_size=params.pars['pop_size'],
        #              save_pop=False,
        #              load_pop=True)
        # sim.initialize()
        #
        # # setup scenarios
        # scens = scenarios.define_scenarios(policy_change=policy_change, params=params, popdict=popdict)
        # scens = cv.Scenarios(sim=sim, metapars=metapars, scenarios=scens) # TODO: want to pass basepars here/correct ones to pass?
        #
        # all_scens[location] = scens
