import covasim as cv
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


def setup(root, databook_name, epidata_name, setting, pars=None, metapars=None):

    params = parameters.setup_params(root, databook_name, setting, metapars)
    params.update_pars(pars)

    popdict = get_popdict(params)

    return
