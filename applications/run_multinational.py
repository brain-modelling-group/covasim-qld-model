import user_interface as ui
import utils



if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Australia']
    # the name of the databook
    db_name = 'input_data_countryX'
    epi_name = 'epi_data_countryX'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Australia': {'pop_size': int(2e4),
                               'beta': 0.04,
                               'n_days': 200,
                               'symp_test': 20,
                               'calibration_end': '2020-03-09'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    scen_opts = {'Australia': {'relax lockdown': {'replace':  (['lockdown'], [['lockdown_relax']], [[20]]),
                                                  'policies': {'lockdown': {'beta': 0.6, 'H': 0.5}},
                                                  'tracing_policies': {'tracing_app': {'coverage': [0.1, 0.2], 'days': [5, 25]}}}}}

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

   # utils.policy_plot2(scens)
    import os
    dirname = os.path.dirname(__file__)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=False, do_show=True, fig_path=dirname + '/Lima_v1' + '.png',
                       interval=30,
                       fig_args=dict(figsize=(10, 5), dpi=50),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                       axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.2},
                       fill_args={'alpha': 0.3},
                       to_plot=['cum_deaths', 'new_diagnoses'])
