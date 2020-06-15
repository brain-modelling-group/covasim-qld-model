import datetime as dt
import matplotlib.ticker as ticker
import numpy as np
import pylab as pl
import sciris as sc

from covasim import defaults as cvd
from matplotlib.ticker import StrMethodFormatter
from policy_updates import PolicySchedule


def policy_plot(scens, plot_ints=False, to_plot=None, do_save=None, fig_path=None, fig_args=None, plot_args=None,
    axis_args=None, fill_args=None, legend_args=None, as_dates=True, dateformat=None,
    interval=None, n_cols=1, font_size=18, font_family=None, grid=True, commaticks=True,
    do_show=True, sep_figs=False, verbose=1, y_lim=None):

    '''
    Plot the results -- can supply arguments for both the figure and the plots.

    Args:
        scen        (covasim Scenario): Scenario with results to be plotted
        scen_name   (str):  Name of the scenario with intervention start dates to plot
        plot_ints   (Bool): Whether or not to plot intervention start dates
        to_plot     (dict): Dict of results to plot; see default_scen_plots for structure
        do_save     (bool): Whether or not to save the figure
        fig_path    (str):  Path to save the figure
        fig_args    (dict): Dictionary of kwargs to be passed to pl.figure()
        plot_args   (dict): Dictionary of kwargs to be passed to pl.plot()
        axis_args   (dict): Dictionary of kwargs to be passed to pl.subplots_adjust()
        fill_args   (dict): Dictionary of kwargs to be passed to pl.fill_between()
        legend_args (dict): Dictionary of kwargs to be passed to pl.legend()
        as_dates    (bool): Whether to plot the x-axis as dates or time points
        dateformat  (str):  Date string format, e.g. '%B %d'
        interval    (int):  Interval between tick marks
        n_cols      (int):  Number of columns of subpanels to use for subplot
        font_size   (int):  Size of the font
        font_family (str):  Font face
        grid        (bool): Whether or not to plot gridlines
        commaticks  (bool): Plot y-axis with commas rather than scientific notation
        do_show     (bool): Whether or not to show the figure
        sep_figs    (bool): Whether to show separate figures for different results instead of subplots
        verbose     (bool): Display a bit of extra information

    Returns:
        fig: Figure handle
    '''

    sc.printv('Plotting...', 1, verbose)

    if to_plot is None:
        to_plot = cvd.get_scen_plots()
    to_plot = sc.dcp(to_plot)  # In case it's supplied as a dict

    # one location per column
    ncols = len(scens.keys())
    nrows = len(to_plot)

    fig, axes = pl.subplots(nrows=nrows, ncols=ncols)

    # plot each location as a column
    for i, loc in enumerate(scens):

        scen = scens[loc]
        axes[0, i].set_title(loc)  # column title

        # plot each outcome in to_plot as a row
        for j, subplot_title in enumerate(to_plot):
            baseline_days = []
            otherscen_days = []

            axes[j,0].set_ylabel(subplot_title)

            this_subplot = axes[j, i]

            reskey = to_plot[subplot_title]
            if isinstance(reskey, list):  # if it came from an odict
                reskey = reskey[0]

            resdata = scen.results[reskey]
            colors = sc.gridcolors(len(resdata.items()))

            # plot the outcomes for each scenario
            for k, scenname in enumerate(resdata):
                scendata = resdata[scenname]
                this_subplot.plot(scen.tvec, scendata.best, c=colors[k])

            if plot_ints:
                scennum = 0
                for s, scenname in enumerate(scen.sims):
                    if scenname.lower() != 'baseline':
                        for intervention in scen.sims[scenname][0]['interventions']:
                            if hasattr(intervention, 'days') and isinstance(intervention, PolicySchedule):
                                otherscen_days = [day for day in intervention.days if
                                                  day not in baseline_days and day not in otherscen_days]
                            elif hasattr(intervention, 'start_day'):
                                if intervention.start_day not in baseline_days and intervention.start_day not in otherscen_days and intervention.start_day != 0:
                                    otherscen_days.append(intervention.start_day)
                                if intervention.end_day not in baseline_days and intervention.end_day not in otherscen_days and isinstance(
                                        intervention.end_day, int) and intervention.end_day < scen.sims[scenname][0][
                                    'n_days']:
                                    otherscen_days.append(intervention.end_day)
                            for day in otherscen_days:
                                this_subplot.axvline(x=day, color=colors[scennum], linestyle='--')
                    else:
                        for intervention in scen.sims[scenname][0]['interventions']:
                            if hasattr(intervention, 'days') and isinstance(intervention, PolicySchedule):
                                baseline_days = [day for day in intervention.days if day not in baseline_days]
                            elif hasattr(intervention, 'start_day'):
                                if intervention.start_day not in baseline_days and intervention.start_day != 0:
                                    baseline_days.append(intervention.start_day)
                            for day in baseline_days:
                                this_subplot.axvline(x=day, color=colors[scennum], linestyle='--')
                    scennum += 1

    pl.show()

    return fig


def plot_scens(scens, fig_path=None, do_save=True, do_show=True, figsize=(5, 10), for_powerpoint=False):
    if do_save and fig_path is None:
        fig_path = '/figures/baseline_v2.png'

    fig_args = {'figsize': figsize}
    if for_powerpoint:
        to_plot = scens.results['new_infections']
    else:
        to_plot = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

    policy_plot(scens,
                plot_ints=True,
                do_save=do_save,
                do_show=do_show,
                fig_path=fig_path,
                interval=14,
                fig_args=fig_args,
                font_size=8,
                to_plot=to_plot)

    return

