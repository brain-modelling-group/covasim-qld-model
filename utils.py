def handle_paths(root, databook_name, epidata_name, popfile):
    pass


def par_keys():
    keys = ['contacts', 'beta_layer', 'quar_eff',
            'pop_size', 'pop_scale', 'rescale',
            'rescale_threshold', 'rescale_factor',
            'pop_infected', 'start_day',
            'n_days', 'diag_factor']
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
