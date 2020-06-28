import covasim as cv
import numpy as np
import os
import sciris as sc


def get_ndays(start_day, end_day):
    """Calculates the number of days for simulation"""
    # get start and end date
    start_day = sc.readdate(str(start_day))
    end_day = sc.readdate(str(end_day))
    n_days = (end_day - start_day).days
    return n_days


def epi_data_url():
    """Contains URL of global epi data for COVID-19"""
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    return url


def colnames():
    """Get the desired column names for the epi data"""
    names = {'date': 'date',
             'new_cases': 'new_diagnoses',
             'new_deaths': 'new_deaths',
             'new_tests': 'new_tests',
             'total_tests': 'cum_tests',
             'total_deaths': 'cum_deaths',
             'total_cases': 'cum_infections'}
    return names


def _format_paths(db_name, epi_name, root):

    # databook
    databook_path = os.path.join(root, 'data', db_name)
    if 'xlsx' not in db_name:
        databook_path += '.xlsx'

    if epi_name == 'url':
        epidata_path = 'url'
    else:
        # must be stored elsewhere
        epidata_path = os.path.join(root, 'data', epi_name)
        if 'csv' not in epi_name:
            epidata_path += '.csv'

    return databook_path, epidata_path


def get_file_paths(db_name, epi_name, root=None):

    if root is None:
        root = os.path.dirname(__file__)

    db_path, epi_path = _format_paths(db_name=db_name,
                                      epi_name=epi_name,
                                      root=root)

    return db_path, epi_path


def set_rand_seed(metapars):
    if metapars.get('seed') is None:
        seed = 1
    else:
        seed = metapars['seed']
    np.random.seed(seed)
    return


def par_keys():
    keys = ['contacts', 'beta_layer', 'quar_factor',
            'pop_size', 'pop_scale', 'rescale',
            'rescale_threshold', 'rescale_factor',
            'pop_infected', 'start_day',
            'n_days', 'iso_factor']
    return keys


def metapar_keys():
    keys = ['n_runs', 'noise']
    return keys


def extrapar_keys():
    keys = ['trace_probs', 'trace_time', 'restart_imports',
            'restart_imports_length', 'relax_day', 'future_daily_tests',
            'undiag', 'av_daily_tests', 'symp_test', 'quar_test',
            'sensitivity', 'test_delay', 'loss_prob']
    return keys


def layerchar_keys():
    keys = ['proportion', 'age_lb', 'age_ub', 'cluster_type']
    return keys


def get_dynamic_lkeys(all_lkeys=None):
    """These are the layers that are re-generated at each time step since the contact networks are dynamic.
    Layers not in this list are treated as static contact networks"""
    defaults = get_default_lkeys(all_lkeys)
    if 'C' in defaults:
        layers = ['C']
    else:
        layers = []

    return layers


def get_default_lkeys(all_lkeys=None):
    """
    These are the standard layer keys: household (H), school (S), workplace (W) and community (C)
    :return:
    """
    defaults = ['H', 'S', 'W', 'C']
    if all_lkeys is None:
        layers = defaults
    else:
        layers = list(set(all_lkeys).intersection(set(defaults)))  # only what is in common
    return layers


def get_all_lkeys():
    layers = list(set(get_default_lkeys())|set(get_dynamic_lkeys()))
    return layers


def get_custom_lkeys(all_lkeys=None):
    """Layer keys that are part of the simulation but not by default"""
    if all_lkeys is None:
        all_lkeys = get_all_lkeys()

    custom_lkeys = list(set(all_lkeys) - set(get_default_lkeys(all_lkeys)))

    return custom_lkeys


def get_lkeys(all_lkeys, dynamic_lkeys):
    # check if they are user-specified, otherwise just use hard-coded keys
    if all_lkeys is None:
        all_lkeys = get_all_lkeys()
    if dynamic_lkeys is None:
        dynamic_lkeys = get_dynamic_lkeys(all_lkeys)

    default_lkeys = get_default_lkeys(all_lkeys)
    custom_lkeys = get_custom_lkeys(all_lkeys)

    return all_lkeys, default_lkeys, dynamic_lkeys, custom_lkeys


def clean_pars(user_pars):
    par_keys = cv.make_pars().keys()

    loc_pars = {key: val for key,val in user_pars.items() if key in par_keys}
    if user_pars.get('calibration_end') is not None:
        calibration_end = user_pars['calibration_end']
    else:
        calibration_end = None
    return loc_pars, calibration_end


def subset_epidata(epidata, calibration_end):
    if calibration_end is None:
        epidata_subset = epidata.copy()
    else:
        epidata_subset = epidata.loc[epidata['date'] <= calibration_end].copy()
    return epidata_subset


def policy_plot2(scens, plot_ints=False, to_plot=None, do_save=None, fig_path=None, fig_args=None, plot_args=None,
    axis_args=None, fill_args=None, legend_args=None, as_dates=True, dateformat=None,
    interval=None, n_cols=1, font_size=18, font_family=None, grid=True, commaticks=True,
    do_show=True, sep_figs=False, verbose=1, y_lim=None):
    from matplotlib.ticker import StrMethodFormatter
    import sciris as sc
    import numpy as np
    import matplotlib.ticker as ticker
    import datetime as dt
    import pylab as pl
    from covasim import defaults as cvd

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
        to_plot = ['cum_deaths', 'new_infections', 'cum_infections']
    to_plot = sc.dcp(to_plot)  # In case it's supplied as a dict

    scen = scens['scenarios']
    epidata = scens['complete_epidata']
    calibration_end = scens['calibration_end']

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
    for rk, reskey in enumerate(to_plot):
        otherscen_days = []
        title = scen[next(iter(scen))].base_sim.results[reskey].name  # Get the name of this result from the base simulation
        if sep_figs:
            figs.append(pl.figure(**fig_args))
            ax = pl.subplot(111)
        else:
            if rk == 0:
                ax = pl.subplot(n_rows, n_cols, rk + 1)
            else:
                ax = pl.subplot(n_rows, n_cols, rk + 1, sharex=ax)

        resdata0 = scen[next(iter(scen))].results[reskey]
        resdata = {key: val for key, val in resdata0.items() if key != 'baseline'}
        colors = sc.gridcolors(len(resdata.items()))
        scennum = 0
        for scenkey, scendata in resdata.items():

            pl.fill_between(scen[next(iter(scen))].tvec, scendata.low, scendata.high, **fill_args)
            pl.plot(scen[next(iter(scen))].tvec, scendata.best, label=scendata.name, c=colors[scennum], **plot_args)
            scennum += 1
            pl.title(title)
            if rk == 0:
                pl.legend(**legend_args)

            pl.grid(grid)
            if commaticks:
                sc.commaticks()

            if scen[next(iter(scen))].base_sim.data is not None and reskey in scen[next(iter(scen))].base_sim.data:
                data_t = np.array((scen[next(iter(scen))].base_sim.data.index - scen[next(iter(scen))].base_sim['start_day']) / np.timedelta64(1, 'D'))
                pl.plot(data_t, scen[next(iter(scen))].base_sim.data[reskey], 'sk', **plot_args)

            # Optionally reset tick marks (useful for e.g. plotting weeks/months)
            if interval:
                xmin, xmax = ax.get_xlim()
                ax.set_xticks(pl.arange(xmin, xmax + 1, interval))

            # Set xticks as dates
            if as_dates:
                @ticker.FuncFormatter
                def date_formatter(x, pos):
                    return (scen[next(iter(scen))].base_sim['start_day'] + dt.timedelta(days=x)).strftime('%b-%d')

                ax.xaxis.set_major_formatter(date_formatter)
                if not interval:
                    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))


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