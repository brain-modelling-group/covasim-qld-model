import datetime as dt
import matplotlib.ticker as ticker
import numpy as np
import pylab as pl
import sciris as sc

from covasim import defaults as cvd
from matplotlib.ticker import StrMethodFormatter
from policy_updates import PolicySchedule


def policy_plot(scen, plot_ints=False, to_plot=None, do_save=None, fig_path=None, fig_args=None, plot_args=None,
    axis_args=None, fill_args=None, legend_args=None, as_dates=True, dateformat=None,
    interval=None, n_cols=1, font_size=18, font_family=None, grid=True, commaticks=True,
    do_show=True, sep_figs=False, verbose=None, y_lim=None):

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

    if verbose is None:
        verbose = scen['verbose']
    sc.printv('Plotting...', 1, verbose)

    if to_plot is None:
        to_plot = cvd.get_scen_plots()
    to_plot = sc.dcp(to_plot)  # In case it's supplied as a dict

    # Handle input arguments -- merge user input with defaults
    fig_args = sc.mergedicts({'figsize': (16, 14)}, fig_args)
    plot_args = sc.mergedicts({'lw': 3, 'alpha': 0.7}, plot_args)
    axis_args = sc.mergedicts(
        {'left': 0.15, 'bottom': 0.1, 'right': 0.95, 'top': 0.90, 'wspace': 0.25, 'hspace': 0.25}, axis_args)
    fill_args = sc.mergedicts({'alpha': 0.2}, fill_args)
    legend_args = sc.mergedicts({'loc': 'best'}, legend_args)

    if sep_figs:
        figs = []
    else:
        fig = pl.figure(**fig_args)
    pl.subplots_adjust(**axis_args)
    pl.rcParams['font.size'] = font_size
    if font_family:
        pl.rcParams['font.family'] = font_family

    n_rows = np.ceil(len(to_plot) / n_cols)  # Number of subplot rows to have
    baseline_days = []

    for rk, title in enumerate(to_plot):
        reskey = to_plot[rk][0]
        otherscen_days = []
        if sep_figs:
            figs.append(pl.figure(**fig_args))
            ax = pl.subplot(111)
        else:
            if rk == 0:
                ax = pl.subplot(n_rows, n_cols, rk + 1)
            else:
                ax = pl.subplot(n_rows, n_cols, rk + 1, sharex=ax)

        resdata = scen.results[reskey]
        colors = sc.gridcolors(len(resdata.items()))
        scennum = 0
        for scenkey, scendata in resdata.items():

            pl.fill_between(scen.tvec, scendata.low, scendata.high, **fill_args)
            pl.plot(scen.tvec, scendata.best, label=scendata.name, c=colors[scennum], **plot_args)
            scennum += 1
            pl.title(title)
            if rk == 0:
                pl.legend(**legend_args)

            pl.grid(grid)
            if commaticks:
                sc.commaticks()

            if scen.base_sim.data is not None and reskey in scen.base_sim.data:
                data_t = np.array((scen.base_sim.data.index - scen.base_sim['start_day']) / np.timedelta64(1, 'D'))
                pl.plot(data_t, scen.base_sim.data[reskey], 'sk', **plot_args)

            # Optionally reset tick marks (useful for e.g. plotting weeks/months)
            if interval:
                xmin, xmax = ax.get_xlim()
                ax.set_xticks(pl.arange(xmin, xmax + 1, interval))

            # Set xticks as dates
            if as_dates:
                @ticker.FuncFormatter
                def date_formatter(x, pos):
                    return (scen.base_sim['start_day'] + dt.timedelta(days=x)).strftime('%b-%d')

                ax.xaxis.set_major_formatter(date_formatter)
                if not interval:
                    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # Plot interventions
        scennum = 0
        if plot_ints:
            for s, scen_name in enumerate(scen.sims):
                if scen_name.lower() != 'baseline':
                    for intervention in scen.sims[scen_name][0]['interventions']:
                        if hasattr(intervention, 'days') and isinstance(intervention, PolicySchedule):
                            otherscen_days = [day for day in intervention.days if day not in baseline_days and day not in otherscen_days]
                        elif hasattr(intervention, 'start_day'):
                            if intervention.start_day not in baseline_days and intervention.start_day not in otherscen_days and intervention.start_day != 0:
                                otherscen_days.append(intervention.start_day)
                            if intervention.end_day not in baseline_days and intervention.end_day not in otherscen_days and isinstance(intervention.end_day, int) and intervention.end_day < scen.sims[scen_name][0]['n_days']:
                                otherscen_days.append(intervention.end_day)
                        for day in otherscen_days:
                            pl.axvline(x=day, color=colors[scennum], linestyle='--')
                        #intervention.plot(scen.sims[scen_name][0], ax)
                else:
                    for intervention in scen.sims[scen_name][0]['interventions']:
                        if hasattr(intervention, 'days') and isinstance(intervention, PolicySchedule) and rk == 0:
                            baseline_days = [day for day in intervention.days if day not in baseline_days]
                        elif hasattr(intervention, 'start_day'):
                            if intervention.start_day not in baseline_days and intervention.start_day != 0:
                                baseline_days.append(intervention.start_day)
                        for day in baseline_days:
                            pl.axvline(x=day, color=colors[scennum], linestyle='--')
                        #intervention.plot(scen.sims[scen_name][0], ax)
                scennum += 1
        if y_lim:
            if reskey in y_lim.keys():
                ax.set_ylim((0, y_lim[reskey]))
                if y_lim[reskey] < 20: # kind of arbitrary limit to add decimal places so that it doesn't just plot integer ticks on small ranges
                    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))

    # Ensure the figure actually renders or saves
    if do_save:
        if fig_path is None:  # No figpath provided - see whether do_save is a figpath
            fig_path = 'covasim_scenarios.png'  # Just give it a default name
        fig_path = sc.makefilepath(fig_path)  # Ensure it's valid, including creating the folder
        pl.savefig(fig_path)

    if do_show:
        pl.show()
    else:
        pl.close(fig)

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

