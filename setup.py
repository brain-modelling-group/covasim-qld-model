import data
import parameters
import popdict


def setup(root, file_name, setting, epidata_loc='epi_data'):

    databook = data.load_databook(root, file_name)

    params = parameters.setup_params(databook, setting, epidata_loc)

    # read in a store population-related data
    age_dist, household_dist = data.read_popdata(databook)

    # get mixing matrix
    mixing_matrix, bin_lower, bin_upper = data.read_mixing_matrix(databook)

    popdict.get_popdict(household_dist,
                        age_dist,
                        params.pars['pop_size'],
                        mixing_matrix,
                        bin_lower,
                        bin_upper,
                        params.pars['contacts'])

    return params
