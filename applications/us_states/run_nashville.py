import user_interface as ui
import utils
import os

dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Nashville']
    # the name of the databook
    db_name = 'input_data_US_nash'
    epi_name = 'epi_data_US_nash'

    pop = 6.92e5

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Nashville': {'pop_size': int(10e4),
                              'beta': 0.1066,
                              'n_days': 310,
                              'pop_infected': 20,
                              'symp_test': 50,
                              'calibration_end': '2020-07-04'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}

    # the policies to change during scenario runs

    scen_opts = {'Nashville': {'Moderate easing of current restrictions on August 15':
                                  {'replace': (['lockdown4'], [['relax4']], [[172]]),
                                   'policies': {'relax4': {'beta': 0.85}}},

                               'Moderate easing of current restrictions on September 15':
                                   {'replace': (['lockdown4'], [['relax4']], [[203]]),
                                    'policies': {'relax4': {'beta': 0.85}}},

                               'Implement and maintain strict lockdown':
                                   {'replace': (['lockdown4'], [['lockdown5']], [[132]])},

                               'Implement strict lockdown and relax on August 15':
                                   {'replace': (['lockdown4', 'lockdown5'], [['lockdown5'], ['lockdown6']], [[132], [172]])},

                               'No changes to current lockdown restrictions':
                                   {'replace': (['lockdown4'], [['lockdown4']], [[500]])},
                               }}


    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_opts,
                           user_pars=user_pars,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)

    # run the scenarios
    scens = ui.run_scens(scens)
    scens['verbose'] = True

    new_no_release_SO = sum(
        scens['scenarios']['Nashville'].results['new_infections']['No changes to current lockdown restrictions']['best'][203:246]) * 100 * 30 / 42 / pop
    new_lockdownrelease_SO = sum(
        scens['scenarios']['Nashville'].results['new_infections']['Implement strict lockdown and relax on August 15']['best'][203:246]) * 100 * 30 / 42 / pop
    new_lockdownmaintain_SO = sum(
        scens['scenarios']['Nashville'].results['new_infections']['Implement and maintain strict lockdown']['best'][203:246]) * 100 * 30 / 42 / pop
    new_september_moderaterelease_SO = sum(
        scens['scenarios']['Nashville'].results['new_infections']['Moderate easing of current restrictions on September 15']['best'][203:246]) * 100 * 30 / 42 / pop
    new_august_moderaterelease_SO = sum(
        scens['scenarios']['Nashville'].results['new_infections']['Moderate easing of current restrictions on August 15']['best'][203:246]) * 100 * 30 / 42 / pop
    diag_no_release_SO = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][203:246]) * 100 * 30 / 42 / pop
    diag_lockdownrelease_SO = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['Implement strict lockdown and relax on August 15']['best'][203:246]) * 100 * 30 / 42 / pop
    diag_lockdownmaintain_SO = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['Implement and maintain strict lockdown']['best'][203:246]) * 100 * 30 / 42 / pop
    diag_september_moderaterelease_SO = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['Moderate easing of current restrictions on September 15']['best'][203:246]) * 100 * 30 / 42 / pop
    diag_august_moderaterelease_SO = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['Moderate easing of current restrictions on August 15']['best'][203:246]) * 100 * 30 / 42 / pop
    cum_no_release_SO = \
    scens['scenarios']['Nashville'].results['cum_infections']['No changes to current lockdown restrictions']['best'][246] / pop
    cum_lockdownrelease_SO = \
    scens['scenarios']['Nashville'].results['cum_infections']['Implement strict lockdown and relax on August 15']['best'][246] / pop
    cum_lockdownmaintain_SO = \
    scens['scenarios']['Nashville'].results['cum_infections']['Implement and maintain strict lockdown']['best'][246] / pop
    cum_september_moderaterelease_SO = \
    scens['scenarios']['Nashville'].results['cum_infections']['Moderate easing of current restrictions on September 15']['best'][246] / pop
    cum_august_moderatelrelease_SO = \
    scens['scenarios']['Nashville'].results['cum_infections']['Moderate easing of current restrictions on August 15']['best'][246] / pop

    new_no_release_ND = sum(
        scens['scenarios']['Nashville'].results['new_infections']['No changes to current lockdown restrictions']['best'][264:307]) * 100 * 30 / 42 / pop
    new_lockdownrelease_ND = sum(
        scens['scenarios']['Nashville'].results['new_infections']['Implement strict lockdown and relax on August 15']['best'][264:307]) * 100 * 30 / 42 / pop
    new_lockdownmaintain_ND = sum(
        scens['scenarios']['Nashville'].results['new_infections']['Implement and maintain strict lockdown']['best'][264:307]) * 100 * 30 / 42 / pop
    new_september_moderaterelease_ND = sum(
        scens['scenarios']['Nashville'].results['new_infections']['Moderate easing of current restrictions on September 15']['best'][264:307]) * 100 * 30 / 42 / pop
    new_august_moderaterelease_ND = sum(
        scens['scenarios']['Nashville'].results['new_infections']['Moderate easing of current restrictions on August 15']['best'][264:307]) * 100 * 30 / 42 / pop
    diag_no_release_ND = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['No changes to current lockdown restrictions']['best'][264:307]) * 100 * 30 / 42 / pop
    diag_lockdownrelease_ND = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['Implement strict lockdown and relax on August 15']['best'][264:307]) * 100 * 30 / 42 / pop
    diag_lockdownmaintain_ND = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['Implement and maintain strict lockdown']['best'][264:307]) * 100 * 30 / 42 / pop
    diag_september_moderaterelease_ND = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['Moderate easing of current restrictions on September 15']['best'][264:307]) * 100 * 30 / 42 / pop
    diag_august_moderaterelease_ND = sum(
        scens['scenarios']['Nashville'].results['new_diagnoses']['Moderate easing of current restrictions on August 15']['best'][264:307]) * 100 * 30 / 42 / pop
    cum_no_release_ND = \
    scens['scenarios']['Nashville'].results['cum_infections']['No changes to current lockdown restrictions']['best'][307] / pop
    cum_lockdownrelease_ND = \
    scens['scenarios']['Nashville'].results['cum_infections']['Implement strict lockdown and relax on August 15']['best'][307] / pop
    cum_lockdownmaintain_ND = \
    scens['scenarios']['Nashville'].results['cum_infections']['Implement and maintain strict lockdown']['best'][307] / pop
    cum_september_moderaterelease_ND = \
    scens['scenarios']['Nashville'].results['cum_infections']['Moderate easing of current restrictions on September 15']['best'][307] / pop
    cum_august_moderatelrelease_ND = \
    scens['scenarios']['Nashville'].results['cum_infections']['Moderate easing of current restrictions on August 15']['best'][307] / pop

    with open('Nashville_projections.txt', 'w') as f:
        print('30 day incidence for Sept-Oct: No changes to current lockdown restrictions =', new_no_release_SO, file=f)
        print('30 day incidence for Sept-Oct: Implement strict lockdown and relax on August 15 =', new_lockdownrelease_SO, file=f)
        print('30 day incidence for Sept-Oct: Implement and maintain strict lockdown =', new_lockdownmaintain_SO,
              file=f)
        print('30 day incidence for Sept-Oct: Moderate easing of current restrictions on September 15 =', new_september_moderaterelease_SO, file=f)
        print('30 day incidence for Sept-Oct: Moderate easing of current restrictions on on August 15 =', new_august_moderaterelease_SO,
              file=f)
        print('30 day detected cases for Sept-Oct: No changes to current lockdown restrictions =', diag_no_release_SO, file=f)
        print('30 day detected cases for Sept-Oct: Implement strict lockdown and relax on August 15 =', diag_lockdownrelease_SO, file=f)
        print('30 day detected cases for Sept-Oct: Implement and maintain strict lockdown =', diag_lockdownmaintain_SO,
              file=f)
        print('30 day detected cases for Sept-Oct: Moderate easing of current restrictions on September 15 =', diag_september_moderaterelease_SO, file=f)
        print('30 day detected cases for Sept-Oct: Moderate easing of current restrictions on on August 15 =', diag_august_moderaterelease_SO,
              file=f)
        print('Cumulative infections for Sept-Oct: No changes to current lockdown restrictions =', cum_no_release_SO, file=f)
        print('Cumulative infections for Sept-Oct: Implement strict lockdown and relax on August 15 =', cum_lockdownrelease_SO, file=f)
        print('Cumulative infections for Sept-Oct: Implement and maintain strict lockdown =', cum_lockdownmaintain_SO,
              file=f)
        print('Cumulative infections for Sept-Oct: Moderate easing of current restrictions on September 15 =', cum_september_moderaterelease_SO, file=f)
        print('Cumulative infections for Sept-Oct: Moderate easing of current restrictions on on August 15 =', cum_august_moderatelrelease_SO,
              file=f)
        print('30 day incidence for Nov-Dec: No changes to current lockdown restrictions =', new_no_release_ND, file=f)
        print('30 day incidence for Nov-Dec: Implement strict lockdown and relax on August 15 =', new_lockdownrelease_ND, file=f)
        print('30 day incidence for Nov-Dec: Implement and maintain strict lockdown =', new_lockdownmaintain_ND,
              file=f)
        print('30 day incidence for Nov-Dec: Moderate easing of current restrictions on September 15 =', new_september_moderaterelease_ND, file=f)
        print('30 day incidence for Nov-Dec: Moderate easing of current restrictions on on August 15 =', new_august_moderaterelease_ND,
              file=f)
        print('30 day detected cases for Nov-Dec: No changes to current lockdown restrictions =', diag_no_release_ND, file=f)
        print('30 day detected cases for Nov-Dec: Implement strict lockdown and relax on August 15 =', diag_lockdownrelease_ND, file=f)
        print('30 day detected cases for Nov-Dec: Implement and maintain strict lockdown =', diag_lockdownmaintain_ND,
              file=f)
        print('30 day detected cases for Nov-Dec: Moderate easing of current restrictions on September 15 =', diag_september_moderaterelease_ND, file=f)
        print('30 day detected cases for Nov-Dec: Moderate easing of current restrictions on on August 15 =', diag_august_moderaterelease_ND,
              file=f)
        print('Cumulative infections for Nov-Dec: No changes to current lockdown restrictions =', cum_no_release_ND, file=f)
        print('Cumulative infections for Nov-Dec: Implement strict lockdown and relax on August 15 =', cum_lockdownrelease_ND, file=f)
        print('Cumulative infections for Nov-Dec: Implement and maintain strict lockdown =', cum_lockdownmaintain_ND,
              file=f)
        print('Cumulative infections for Nov-Dec: Moderate easing of current restrictions on September 15 =', cum_september_moderaterelease_ND, file=f)
        print('Cumulative infections for Nov-Dec: Moderate easing of current restrictions on on August 15 =', cum_august_moderatelrelease_ND,
              file=f)
        f.close()

    # plot cumulative deaths for calibration
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                 fig_path=dirname + '/figs/New-York-calibrate' + '.png',
    #                 interval=30, n_cols=1,
    #                 fig_args=dict(figsize=(5, 5), dpi=100),
    #                 font_size=11,
    #                 # y_lim={'new_infections': 500},
    #                 legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
    #                 axis_args={'left': 0.15, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.15},
    #                 fill_args={'alpha': 0.3},
    #                 to_plot=['new_diagnoses', 'cum_deaths'])

    # plot cumulative infections to see if all the population gets infected
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs/Nashville-projections' + '.png',
                       interval=30, n_cols=1,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
                       axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.3},
                       fill_args={'alpha': 0.1},
                       to_plot=['new_infections', 'cum_infections'])