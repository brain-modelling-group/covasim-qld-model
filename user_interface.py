import scenarios


def setup_scens(locations,
                db_name,
                epi_name='url',
                policy_change=None,
                user_pars=None,
                metapars=None):

    scens = scenarios.setup_scens(locations=locations,
                                  db_name=db_name,
                                  epi_name=epi_name,
                                  policy_change=policy_change,
                                  user_pars=user_pars,
                                  metapars=metapars)

    return scens


def run_scens(scens):
    scens = scenarios.run_scens(scens)
    return scens