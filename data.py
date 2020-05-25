import os
import pandas as pd
import sciris as sc
import warnings


def par_keys():
    keys = ['contacts', 'beta_layer', 'quar_eff',
            'pop_size', 'pop_scale', 'rescale',
            'rescale_threshold', 'rescale_factor',
            'pop_infected', 'start_day', 'end_day',
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


def _get_ndays(start_day, end_day):
    """Calculates the number of days for simulation"""
    # get start and end date
    start_day = sc.readdate(str(start_day))
    end_day = sc.readdate(str(end_day))
    n_days = end_day - start_day
    return n_days


def _get_pars(databook):
    """
    Read in the parameter values from the databook.
    If values are not specified in the databook, default values will be taken from Covasim

    :param databook: a pandas ExcelFile object
    :return: dictionary of complete parameter values
    """

    # read in networks (layers)
    layers = databook.parse("layers", index_col=0)
    layers = layers.to_dict(orient="dict")

    # read other_par
    other_pars = databook.parse("other_par", index_col=0)['value']
    other_pars = other_pars.to_dict()

    other_pars['n_days'] = _get_ndays(other_pars['start_day'], other_pars['end_day'])

    # retrieve values from both dicts & use to update default values
    pars = {}
    for key in par_keys():
        if layers.get(key) is not None:
            pars[key] = layers.get(key)
        elif other_pars.get(key) is not None:
            pars[key] = other_pars.get(key)
        else:
            warnings.warn(f'Parameter key "{key}" not found in spreadsheet data')

    return pars


def _get_extrapars(databook):

    # get those in the layers sheet
    layers = databook.parse('layers', index_col=0)
    layers = layers.to_dict(orient="dict")
    # those in other_par sheet
    otherpar = databook.parse('other_par', index_col=0)['value']

    extrapars = {}
    for key in extrapar_keys():
        if layers.get(key) is not None:
            extrapars[key] = layers.get(key)
        elif otherpar.get(key) is not None:
            extrapars[key] = otherpar.get(key)
        else:
            warnings.warn(f'Extra-parameter key "{key}" not found in spreadsheet data')

    return extrapars


def _get_layerchars(databook):
    """
    Read in the layer characteristics
    :param databook:
    :return: a dit of layer characteristics
    """

    layers = databook.parse('layers', index_col=0)
    layers = layers.to_dict(orient='dict')

    layerchars = {}
    for key in layerchar_keys():
        if layers.get(key) is not None:
            layerchars[key] = layers.get(key)
        else:
            warnings.warn(f'Layer characteristics key "{key}" not found in spreadsheet data')

    return layerchars


def get_layer_keys(databook):
    """
    Get the names of custom layers
    :param databook:
    :return:
    """
    layers = databook.parse('layers', index_col=0)
    allkeys = layers.index.tolist()
    default_keys = default_layer_keys()
    custom_keys = list(set(allkeys) - set(default_keys))  # remove custom keys
    all_dynamic_keys = _dynamic_layer_keys()
    dynamic_keys = list(set(all_dynamic_keys).intersection(allkeys))  # dynamic keys that are listed in spreadsheet
    return allkeys, default_keys, custom_keys, dynamic_keys


# def read_sex(databook):
#     sex = databook.parse('age_sex')
#     sex['frac_male'] = sex['Male'] / (sex['Male'] + sex['Female'])
#     sex['frac_male'] = sex['frac_male'].fillna(0.5)  # if 0, replace with 0.5


def read_popdata(databook):
    age_dist = databook.parse('age_sex')['Total']
    household_dist = databook.parse('households')['no. households']
    household_dist.index += 1  # represents the no. of people in each household
    return age_dist, household_dist


def read_tests_imported(databook):
    """Reads in the imported cases & daily tests."""

    epidata = databook.parse('epi_data')
    imported_cases = epidata['daily_imported_cases'].to_numpy()
    imported_cases = imported_cases[6:] # shift 7 days back to account for lag in reporting time
    daily_tests = epidata['new_tests'].to_numpy()
    return imported_cases, daily_tests


def read_contact_matrix(databook):
    """
    Load Prem et al. matrices then transform into a symmetric matrix
    :param databook:
    :return:
    """
    contact_matrix = {}
    mixing_matrix0 = databook.parse(sheet_name='contact matrices-home', usecols=range(17), index_col=0)
    # make symmetric with ((rowi, colj) + (rowj, coli)) / 2
    mixing_matrix = mixing_matrix0.copy()
    for i in range(len(mixing_matrix0)):
        for j in range(len(mixing_matrix0)):
            mixing_matrix.values[i, j] = (mixing_matrix0.values[i, j] + mixing_matrix0.values[j, i]) / 2.0
    age_lb = [int(x.split('-')[0]) for x in mixing_matrix.index]  # lower age in bin
    age_ub = [int(x.split('-')[1]) for x in mixing_matrix.index]  # upper age in bin

    contact_matrix['matrix'] = mixing_matrix
    contact_matrix['age_lb'] = age_lb
    contact_matrix['age_ub'] = age_ub
    return contact_matrix


def load_databook(root, file_name):
    file_path = os.path.join(root, 'data', file_name)
    file_path += '.xlsx'
    databook = pd.ExcelFile(file_path)
    return databook


def read_params(databook):
    """
    Read all the necessary parameters from the databook
    """

    pars = _get_pars(databook)
    extrapars = _get_extrapars(databook)
    layerchars = _get_layerchars(databook)
    return pars, extrapars, layerchars
