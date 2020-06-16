import plot
import scenarios


def setup_scens(locations,
                db_name,
                epi_name='url',
                policy_change=None,
                user_pars=None,
                metapars=None,
                policy_vals=None):
    """

    :param locations:
    :param db_name:
    :param epi_name:
    :param policy_change: Dict with the following structure
                            {'name_of_scen': {
                                            'replace': ([to_replace1, to_replace2,...], [[replacements1], [replacements2]], [[start_date1, end_date1], [start_date2, end_date2]]),
                                            'turn_off': ([pol1, pol2,...], [date1, date2,...])
                                            }
                            }`
    Note that 'replace' type can have end dates appended to the end of their date lists.
    :param user_pars:
    :param metapars:
    :param policy_vals:
    :return:
    """

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


def policy_plot(scens, scens_toplot=None, outcomes_toplot=None, plot_ints=True, do_show=True, do_save=False, fig_path=None, commaticks=True, verbose=1):
    """

    :param scens (dict): Scenarios by location (dict)
    :param scens_toplot (dict): the name of the scenarios you which to plot. Structure is {location_name: [list_of_scenarios]}
                                If None, all scenarios are plotted.
    :param outcomes_toplot: a dictionary of which specifies the plot label and the results key.
                            Eg. {'Cumulative infections': 'cum_infections'} will plot the 'cum_infections' data with the title 'Cumulative infections'.
                            If None, defaults are plotted
    :param plot_ints (Bool): Whether or not to plot intervention start dates
    :param do_show (bool): Whether or not to show the figure
    :param do_save (bool): Whether or not to save the figure
    :param fig_path (str):  Path to save the figure
    :param commaticks (bool): use commas in y-tick labels
    :return:
    """
    fig = plot.policy_plot(scens,
                           scens_toplot=scens_toplot,
                           outcomes_toplot=outcomes_toplot,
                           plot_ints=plot_ints,
                           do_show=do_show,
                           do_save=do_save,
                           fig_path=fig_path,
                           commaticks=commaticks,
                           verbose=verbose)
    return fig