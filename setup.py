import contacts as co
import parameters


def get_popdict(params):

    contacts, ages, uids = co.make_contacts(params)

    # create the popdict object
    popdict = {}
    popdict['contacts'] = contacts
    popdict['age'] = ages  # TODO: check this
    popdict['uid'] = uids

    return popdict


def setup(root, file_name, setting, pars=None, metapars=None, epidata_loc='epi_data'):

    params = parameters.setup_params(root, file_name, setting, epidata_loc)
    params.update_pars(pars)
    params.update_metapars(metapars)

    popdict = get_popdict(params)

    return
