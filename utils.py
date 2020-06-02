import numpy as np
import os


def epi_data_url():
    """Contains URL of global epi data for COVID-19"""
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/full_data.csv'
    return url


def _format_paths(db_name, epi_name, pop_name, root):

    # databook
    databook_path = os.path.join(root, 'data', db_name)
    if 'xlsx' not in db_name:
        databook_path += '.xlsx'

    # epidata
    epidata_path = os.path.join(root, 'data', epi_name)
    if 'xlsx' not in epi_name:
        epidata_path += '.xlsx'

    # pop_name
    pop_path = os.path.join(root, 'data', pop_name)
    if 'obj' not in pop_name:
        pop_path += '.obj'

    return databook_path, epidata_path, pop_path


def get_file_paths(db_name, epi_name, pop_name, root=None):

    if root is None:
        root = os.path.dirname(__file__)

    db_path, epi_path, pop_path = _format_paths(db_name=db_name,
                                                epi_name=epi_name,
                                                pop_name=pop_name,
                                                root=root)
    return db_path, epi_path, pop_path


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


def _dynamic_layer_keys():
    """These are the layers that are re-generated at each time step since the contact networks are dynamic.
    Layers not in this list are treated as static contact networks"""

    layers = ['C', 'beach', 'entertainment',
              'cafe_restaurant', 'pub_bar', 'transport',
              'national_parks', 'public_parks', 'large_events']
    return layers


def default_layer_keys():
    """
    These are the standard layer keys: household (H), school (S), workplace (W) and community (C)
    :return:
    """
    layers = ['H', 'S', 'W', 'C']
    return layers
