import data
import parameters
import popdict


def setup(root, file_name, setting, epidata_loc='epi_data'):
    databook = data.load_databook(root, file_name)

    params = parameters.setup_params(databook, setting, epidata_loc)

    popdict.get_popdict(params)

    return params
