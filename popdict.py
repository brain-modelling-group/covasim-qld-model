import contacts as co


def get_popdict(params):

    contacts, ages, uids = co.make_contacts(params)

    # create the popdict object
    popdict = {}
    popdict['contacts'] = contacts
    popdict['age'] = ages  # TODO: check this
    popdict['uid'] = uids

    return popdict
