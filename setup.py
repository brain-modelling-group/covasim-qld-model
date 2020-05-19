import data
import parameters


def setup(root, file_name, setting, betavals=None, epi_loc='epi_data'):
    databook = data.load_databook(root, file_name)
    pars, metapars, extrapars = data.read_params(databook)
    params = parameters.Parameters(setting=setting,
                                   pars=pars,
                                   metapars=metapars,
                                   extrapars=extrapars,
                                   epi_loc=epi_loc)
    # popdata = population_data.PopulationData()
    return params # , popdata
