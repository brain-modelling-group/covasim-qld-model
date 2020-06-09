import plot
import scenarios


def setup_scens(locations,
                db_name,
                epi_name='url',
                policy_change=None,
                user_pars=None,
                metapars=None,
                policy_vals=None):

    scens = scenarios.setup_scens(locations=locations,
                                  db_name=db_name,
                                  epi_name=epi_name,
                                  policy_change=policy_change,
                                  user_pars=user_pars,
                                  metapars=metapars,
                                  policy_vals=policy_vals)

    return scens


def run_scens(scens):
    scens = scenarios.run_scens(scens)
    return scens


def policy_plot(scens):
    # TODO: currently only takes in a single country at a time
    plot.policy_plot(scens, do_save=False)