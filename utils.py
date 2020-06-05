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
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/full_data.csv'
    return url


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
        if 'xlsx' not in epi_name:
            epidata_path += '.xlsx'

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
            'restart_imports_length', 'relax_day', 'future_daily_tests']
    return keys


def layerchar_keys():
    keys = ['proportion', 'age_lb', 'age_ub', 'cluster_type']
    return keys


def dynamic_lkeys():
    """These are the layers that are re-generated at each time step since the contact networks are dynamic.
    Layers not in this list are treated as static contact networks"""
    layers = ['C']
    return layers


def default_lkeys():
    """
    These are the standard layer keys: household (H), school (S), workplace (W) and community (C)
    :return:
    """
    layers = ['H', 'S', 'W', 'C']
    return layers


def all_lkeys():
    layers = ['H', 'S', 'W', 'C']
    return layers


def custom_lkeys():
    """Layer keys that are part of the simulation but not by default"""
    custom_lkeys = list(set(all_lkeys()) - set(default_lkeys()))
    return custom_lkeys


def get_lkeys():
    keys = {'all_lkeys': all_lkeys(),
            'default_lkeys': default_lkeys(),
            'dynamic_lkeys': dynamic_lkeys(),
            'custom_lkeys': custom_lkeys()}
    return keys
