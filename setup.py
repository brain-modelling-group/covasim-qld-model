import parameters
import popdict


def setup(root, file_name, setting, epidata_loc='epi_data'):

    params = parameters.setup_params(root, file_name, setting, epidata_loc)

    popdict.get_popdict(params)

    return params
