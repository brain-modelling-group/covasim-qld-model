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
                metapars=None):

    # for reproducible results
    utils.set_rand_seed(metapars)

    # return data relevant to each specified location in "locations"
    all_data = data.read_data(locations=locations,
                              db_name=db_name,
                              epi_name=epi_name)

    all_scens = {}
    for location in locations:
        print(f'\n Creating scenarios for "{location}"...')
        loc_data = all_data[location]
        loc_epidata = all_data[location]['epidata']
        keys = all_data[location]
        loc_pars = user_pars[location]

        # setup parameters object for this simulation
        params = parameters.setup_params(location=location,
                                         loc_data=loc_data,
                                         metapars=metapars,
                                         user_pars=loc_pars,
                                         keys=keys)

        people, popdict = co.make_people(params)


        # setup simulation for this location
        sim = cv.Sim(pars=params.pars,
                     datafile=loc_epidata,
                     popfile=people,
                     pop_size=params.pars['pop_size'],
                     load_pop=True,
                     save_pop=False)
        sim.initialize()

        # setup scenarios for this location
        scens = scenarios.define_scenarios(policy_change=policy_change,
                                           params=params,
                                           popdict=popdict)
        scens = cv.Scenarios(sim=sim,
                             metapars=metapars,
                             scenarios=scens)
        all_scens[location] = scens

    return all_scens
