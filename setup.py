import data
import parameters


def setup(root, file_name, setting, epidata_loc='epi_data'):
    databook = data.load_databook(root, file_name)
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
    # popdata = population_data.PopulationData()
    return params # , popdata
