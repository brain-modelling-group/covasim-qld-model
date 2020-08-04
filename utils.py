import covasim as cv
import numpy as np
import os
import sciris as sc
import utils, policy_updates
import covasim.utils as cvu
import covasim.defaults as cvd
import covasim.base as cvb


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
             'cum_infections': 'cum_diagnoses',
             'total_cases': 'cum_diagnoses',
             'hospitalised': 'n_severe'}  # either total cases or cum_infections in epi book
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
    layers = list(set(get_default_lkeys()) | set(get_dynamic_lkeys()))
    return layers


def get_custom_lkeys(all_lkeys=None):
    """Layer keys that are part of the simulation but not by default"""
    if all_lkeys is None:
        all_lkeys = get_all_lkeys()

    default_lkeys = set(get_default_lkeys(all_lkeys))
    custom_lkeys = [x for x in all_lkeys if x not in default_lkeys]  # Don't change the order, otherwise runs are not reproducible due to rng

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


def clean_pars(user_pars, locations):
    par_keys = cv.make_pars().keys()
    calibration_end = {}
    new_user_pars = {}

    for location in locations:
        user_pars_oneloc = user_pars[location]
        if user_pars_oneloc.get('calibration_end') is not None:
            calibration_end[location] = user_pars_oneloc['calibration_end']
        else:
            calibration_end[location] = None

        new_user_pars[location] = {key: val for key, val in user_pars_oneloc.items() if key in par_keys}

    return new_user_pars, calibration_end


def clean_calibration_end(locations, calibration_end):
    if calibration_end is None:  # not specified for any country
        calibration_end_all_locs = {loc: None for loc in locations}
    else:
        calibration_end_all_locs = {}
        for location in locations:
            if calibration_end.get(location) is None:  # doesn't exist or set to None
                calibration_end_all_locs[location] = None
            else:
                calibration_end_all_locs[location] = calibration_end[location]

    return calibration_end_all_locs


def policy_plot2(scens, plot_ints=False, to_plot=None, do_save=None, fig_path=None, fig_args=None, plot_args=None,
                 axis_args=None, fill_args=None, legend_args=None, as_dates=True, dateformat=None, plot_base=False,
                 interval=None, n_cols=1, font_size=18, font_family=None, grid=True, commaticks=True,
                 do_show=True, sep_figs=False, verbose=1, y_lim=None):
    from matplotlib.ticker import StrMethodFormatter
    import sciris as sc
    import numpy as np
    import matplotlib.ticker as ticker
    import datetime as dt
    import pylab as pl
    import matplotlib as mpl
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

    scens['verbose'] = True
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
        if plot_base:
            resdata = {key: val for key, val in resdata0.items()}
        else:
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

            epidata[next(iter(scen))]['validate'] = 0  # which data is for validation vs calibration
            for j in range(len(epidata[next(iter(scen))])):
                if (epidata[next(iter(scen))]['date'][j]) >= sc.readdate(calibration_end[next(iter(scen))][next(iter(scen))]):
                    epidata[next(iter(scen))].loc[j, 'validate'] = 1

            if scen[next(iter(scen))].base_sim.data is not None and reskey in scen[next(iter(scen))].base_sim.data:
                data_t = np.array((scen[next(iter(scen))].base_sim.data.index - scen[next(iter(scen))].base_sim['start_day']) / np.timedelta64(1, 'D'))
                # pl.plot(data_t, epidata.base_sim.data[reskey], 'sk', **plot_args)
                cmap, norm = mpl.colors.from_levels_and_colors(levels=[0, 1], colors=['black', 'black'], extend='max')
                pl.scatter(x=epidata[next(iter(scen))].index, y=epidata[next(iter(scen))][reskey], c=epidata[next(iter(scen))]['validate'],
                           edgecolor='none', marker='s', cmap=cmap, norm=norm, **plot_args)
                # pl.plot(epidata[next(iter(scen))].index, epidata[next(iter(scen))][reskey],
                #        sc.mergedicts({'c': epidata[next(iter(scen))]['validate'],'cmap': cmap, 'norm':norm}, plot_args))

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

        # Plot interventions
        day_projection_starts = utils.get_ndays(scen[next(iter(scen))].base_sim['start_day'],
                                                sc.readdate(calibration_end[next(iter(scen))][next(iter(scen))]))
        # pl.axvline(x=day_projection_starts, color='black', linestyle='--')
        scennum = 0
        if plot_ints:
            for scenkey, scendata in resdata.items():
                if scenkey.lower() != 'baseline':
                    for intervention in scen[next(iter(scen))].scenarios[scenkey]['pars']['interventions']:
                        if hasattr(intervention, 'days'):  # and isinstance(intervention, PolicySchedule):
                            otherscen_days = [day for day in intervention.days if day not in otherscen_days]
                        elif hasattr(intervention, 'start_day'):
                            if intervention.start_day != 0:
                                otherscen_days.append(intervention.start_day)
                        for day in otherscen_days:
                            # pl.axvline(x=day, color=colors[scennum], linestyle='--')
                            pl.axvline(x=day, color='grey', linestyle='--')
                        # intervention.plot(scen.sims[scen_name][0], ax)
                if scenkey.lower() == 'baseline':
                    if plot_base:
                        for intervention in scen[next(iter(scen))].scenarios['baseline']['pars']['interventions']:
                            if hasattr(intervention, 'days') and isinstance(intervention,
                                                                            policy_updates.PolicySchedule) and rk == 0:
                                baseline_days = [day for day in intervention.days if day not in baseline_days]
                            elif hasattr(intervention, 'start_day'):
                                if intervention.start_day not in baseline_days and intervention.start_day != 0:
                                    baseline_days.append(intervention.start_day)
                            for day in baseline_days:
                                # pl.axvline(x=day, color=colors[scennum], linestyle='--')
                                pl.axvline(x=day, color='grey', linestyle='--')
                        # intervention.plot(scen.sims[scen_name][0], ax)
                scennum += 1
        if y_lim:
            if reskey in y_lim.keys():
                ax.set_ylim((0, y_lim[reskey]))
                if y_lim[reskey] < 20:  # kind of arbitrary limit to add decimal places so that it doesn't just plot integer ticks on small ranges
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

    #
    # # Plot interventions
    # scennum = 0
    # if plot_ints:
    #     for s, scen_name in enumerate(scen.sims):
    #         if scen_name.lower() != 'baseline':
    #             for intervention in scen.sims[scen_name][0]['interventions']:
    #                 if hasattr(intervention, 'days') and isinstance(intervention, PolicySchedule):
    #                     otherscen_days = [day for day in intervention.days if day not in baseline_days and day not in otherscen_days]
    #                 elif hasattr(intervention, 'start_day'):
    #                     if intervention.start_day not in baseline_days and intervention.start_day not in otherscen_days and intervention.start_day != 0:
    #                         otherscen_days.append(intervention.start_day)
    #                     if intervention.end_day not in baseline_days and intervention.end_day not in otherscen_days and isinstance(intervention.end_day, int) and intervention.end_day < scen.sims[scen_name][0]['n_days']:
    #                         otherscen_days.append(intervention.end_day)
    #                 for day in otherscen_days:
    #                     #pl.axvline(x=day, color=colors[scennum], linestyle='--')
    #                     pl.axvline(x=day, color='grey', linestyle='--')
    #                 #intervention.plot(scen.sims[scen_name][0], ax)
    #         else:
    #             for intervention in scen.sims[scen_name][0]['interventions']:
    #                 if hasattr(intervention, 'days') and isinstance(intervention, PolicySchedule) and rk == 0:
    #                     baseline_days = [day for day in intervention.days if day not in baseline_days]
    #                 elif hasattr(intervention, 'start_day'):
    #                     if intervention.start_day not in baseline_days and intervention.start_day != 0:
    #                         baseline_days.append(intervention.start_day)
    #                 for day in baseline_days:
    #                     #pl.axvline(x=day, color=colors[scennum], linestyle='--')
    #                     pl.axvline(x=day, color='grey', linestyle='--')
    #                 #intervention.plot(scen.sims[scen_name][0], ax)
    #         scennum += 1


class SeedInfection(cv.Intervention):
    """
    Seed a fixed number of infections

    This class facilities seeding a fixed number of infections on a per-day
    basis.

    Infections will only be seeded on specified days

    """

    def __init__(self, infections: dict):
        """

        Args:
            infections: Dictionary with {day_index:n_infections}

        """
        super().__init__()
        self.infections = infections  #: Dictionary mapping {day: n_infections}

    def apply(self, sim):
        if sim.t in self.infections:
            susceptible_inds = cvu.true(sim.people.susceptible)

            if len(susceptible_inds) < self.infections[sim.t]:
                raise Exception('Insufficient people available to infect')

            targets = cvu.choose(len(susceptible_inds), self.infections[sim.t])
            target_inds = susceptible_inds[targets]
            sim.people.infect(inds=target_inds)

class test_prob_with_quarantine(cv.test_prob):

    def __init__(self, *args, swab_delay, isolation_threshold, leaving_quar_prob,**kwargs):
        super().__init__(*args, **kwargs)
        self.swab_delay = swab_delay
        self.isolation_threshold = isolation_threshold  #: Isolate people while waiting for tests after cum_diagnosed exceeds this amount
        self.isolate_while_waiting = isolation_threshold == 0  # If the threshold is 0 then isolate straight away
        self.leaving_quar_prob = leaving_quar_prob  # Test rate for people leaving quarantine

    def apply(self, sim):
        ''' Perform testing '''
        t = sim.t
        if t < self.start_day:
            return
        elif self.end_day is not None and t > self.end_day:
            return

        # TEST LOGIC
        # 1. People who become symptomatic in the general community will wait `swab_delay` days before getting tested, at rate `symp_prob`
        # 2. People who become symptomatic while in quarantine will test immediately at rate `symp_quar_test`
        # 3. People who are symptomatic and then are ordered to quarantine, will test immediately at rate `symp_quar_test`
        # 4. People who have severe symptoms will be tested
        # 5. (Optional) People that are asymptomatic test before leaving quarantine
        # 6. People that have been diagnosed will not be tested
        # 7. People that are already waiting for a diagnosis will not be retested
        # 8. People can optionally isolate while waiting for their diagnosis
        # 9. People already on quarantine while tested will not have their quarantine shortened, but if they are tested at the end of their
        #    quarantine, the quarantine will be extended

        # Construct the testing probabilities piece by piece -- complicated, since need to do it in the right order
        test_probs = np.zeros(sim.n)  # Begin by assigning equal testing probability to everyone

        # (1) People wait swab_delay days before they decide to start testing. If swab_delay is 0 then they will be eligible as soon as they are symptomatic
        symp_inds = cvu.true(sim.people.symptomatic) # People who are symptomatic
        symp_test_inds = symp_inds[sim.people.date_symptomatic[symp_inds] == t-self.swab_delay]  # People who have been symptomatic and who are eligible to test today
        test_probs[symp_test_inds] = self.symp_prob  # People with symptoms eligible to test today

        # People whose symptomatic scheduled day falls during quarantine will test at the symp_quar_prob rate
        # People who are already symptomatic, missed their test, and then enter quarantine, will test at the symp_quar_prob rate
        # People get quarantined at 11:59pm so the people getting quarantined today haven't been quarantined yet.
        # The order is
        # Day 4 - Test, quarantine people waiting for results
        # Day 4 - Trace
        # Day 4 - Quarantine known contacts
        # Day 5 - Test, nobody has entered quarantine on day 5 yet - if someone was symptomatic and untested and was quarantined *yesterday* then
        #         they need to be tested *today*

        # Someone waiting for a test result shouldn't retest. So we check that they aren't already waiting for their test.
        # Note that people are diagnosed after interventions are executed,
        # therefore if someone is tested on day 3 and the test delay is 2, on day 5 then sim.people.diagnosed will NOT
        # be true at the point where this code is executing. Therefore, they should not be eligible to retest. It's
        # like they are going to receive their results at 11:59pm so the decisions they make during the day are based
        # on not having been diagnosed yet. Hence > is used here so that on day 3+2=5, they won't retest. (i.e. they are
        # waiting for their results if the day they recieve their results is > the current day). Note that they become
        # symptomatic prior to interventions e.g. they wake up with symptoms
        if sim.t > 0:
            # If quarantined, there's no swab delay

            # (2) People who become symptomatic while quarantining test immediately
            quarantine_test_inds = symp_inds[sim.people.quarantined[symp_inds] & (sim.people.date_symptomatic[symp_inds] == t)] # People that became symptomatic today while already on quarantine
            test_probs[quarantine_test_inds] = self.symp_quar_prob  # People with symptoms in quarantine are eligible to test without waiting

            # (3) People who are symptomatic and undiagnosed before entering quarantine, test as soon as they are quarantined
            newly_quarantined_test_inds = cvu.true((sim.people.date_quarantined == (sim.t-1)) & sim.people.symptomatic & ~sim.people.diagnosed) # People that just entered quarantine, who are already symptomatic
            test_probs[newly_quarantined_test_inds] = self.symp_quar_prob  # People with symptoms that just entered quarantine are eligible to test

        # (4) People with severe symptoms that would be hospitalised are guaranteed to be tested
        test_probs[sim.people.severe] = 1.0  # People with severe symptoms are guaranteed to be tested unless already diagnosed or awaiting results

        # (5) People leaving quarantine test before leaving
        # Note that this test is irrespective of symptoms. If someone has not been tested during quarantine, they will test at this probability if they are
        # quarantining as a known contact
        if self.leaving_quar_prob:
            leaving_inds = cvu.true(sim.people.quarantined & sim.people.known_contact) # Everyone on quarantine that is a known contact.
            leaving_inds = leaving_inds[(sim.people.date_end_quarantine[leaving_inds]-self.test_delay) == sim.t] # Subset of people that might need to test today because they are leaving quarantine
            quarantine_never_tested = leaving_inds[~np.isfinite(sim.people.date_tested[leaving_inds])] # Subset that have not been tested
            quarantine_tested_before = leaving_inds[sim.people.date_tested[leaving_inds] < sim.people.date_quarantined[leaving_inds]] # Subset that were last tested before quarantine
            leaving_inds = quarantine_never_tested+quarantine_tested_before
            test_probs[leaving_inds] = np.maximum(test_probs[leaving_inds], self.leaving_quar_prob) # If they are already supposed to test at a higher rate e.g. severe symptoms, keep it

        # (6) People that have been diagnosed aren't tested
        diag_inds = cvu.true(sim.people.diagnosed)
        test_probs[diag_inds] = 0.0  # People who are diagnosed or awaiting test results don't test

        # (7) People waiting for results don't get tested
        tested_inds = cvu.true(np.isfinite(sim.people.date_tested))
        pending_result_inds = tested_inds[(sim.people.date_tested[tested_inds] + self.test_delay) > sim.t]  # People who have been tested and will receive test results after the current timestep
        test_probs[pending_result_inds] = 0.0  # People awaiting test results don't test

        # Test people based on their per-person test probability
        test_inds = cvu.true(cvu.binomial_arr(test_probs))
        sim.people.test(test_inds, test_sensitivity=self.test_sensitivity, loss_prob=self.loss_prob, test_delay=self.test_delay) # Actually test people
        sim.results['new_tests'][t] += int(len(test_inds)*sim['pop_scale']/sim.rescale_vec[t]) # If we're using dynamic scaling, we have to scale by pop_scale, not rescale_vec

        # Check the number of diagnosed people to decide whether to turn on isolation while waiting for results
        # Using >= here means an isolation threshold of 0 is a second check to ensure isolation takes place
        # (normally the `isolate_while_waiting` flag should be pre-set in the constructor)
        if (not self.isolate_while_waiting) and (sim.t > 0 and sim.results['cum_diagnoses'][t-1] >= self.isolation_threshold):
            self.isolate_while_waiting = True

        if self.isolate_while_waiting:

            # (9) If the diagnosis waiting period goes beyond an existing quarantine, extend it
            # This goes first, so that people entering quarantine below aren't included
            extend_quarantine = cvu.true((sim.people.date_tested==sim.t) & sim.people.quarantined)
            sim.people.date_end_quarantine[extend_quarantine] = np.maximum(sim.people.date_end_quarantine[extend_quarantine], sim.people.date_tested[extend_quarantine]+self.test_delay)

            # (8) If not on quarantine, isolate the period while waiting for the test result
            new_quarantine = cvu.true((sim.people.date_tested==sim.t) & ~sim.people.quarantined)
            sim.people.quarantined[new_quarantine] = True
            sim.people.date_quarantined[new_quarantine] = sim.t
            sim.people.date_end_quarantine[new_quarantine] = sim.t+self.test_delay