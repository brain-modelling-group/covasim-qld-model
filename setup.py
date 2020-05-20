import data
import parameters


def setup(root, file_name, setting, epidata_loc='epi_data'):

    databook = data.load_databook(root, file_name)

    # read in and store parameters
    pars, metapars, extrapars, layerchars = data.read_params(databook)
    imported_cases, daily_tests = data.read_tests_imported(databook)
    params = parameters.Parameters(setting=setting,
                                   pars=pars,
                                   metapars=metapars,
                                   extrapars=extrapars,
                                   layerchars=layerchars,
                                   imported_cases=imported_cases,
                                   daily_tests=daily_tests,
                                   epidata_loc=epidata_loc)

    # read in a store population-related data
    age_dist, household_dist = data.read_popdata(databook)
    # transform data

    # popdata = population_data.PopulationData()
    return params # , popdata
