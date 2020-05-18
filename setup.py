import data
import parameters


def setup(root, file_name, setting):
    databook = data.load_databook(root, file_name)
    pars, metapars = data.read_params(databook)
    params = parameters.Parameters(setting=setting,
                                   pars=pars,
                                   metapars=metapars)
    # popdata = population_data.PopulationData()
    return params # , popdata
