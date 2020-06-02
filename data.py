import math
import pandas as pd
import sciris as sc
import utils
import warnings


def _get_ndays(start_day, end_day):
    """Calculates the number of days for simulation"""
    # get start and end date
    start_day = sc.readdate(str(start_day))
    end_day = sc.readdate(str(end_day))
    n_days = (end_day - start_day).days
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
    for key in utils.par_keys():
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
    for key in utils.extrapar_keys():
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
    for key in utils.layerchar_keys():
        if layers.get(key) is not None:
            layerchars[key] = layers.get(key)
        else:
            warnings.warn(f'Layer characteristics key "{key}" not found in spreadsheet data')

    return layerchars


def read_policies(databook, all_lkeys):
    """
    Read in the policies sheet
    :param databook:
    :return:
    """
    policies = {}
    policies['beta_policies'] = {}
    policies['import_policies'] = {}
    policies['clip_policies'] = {}
    policies['policy_dates'] = {}

    pols = databook.parse('policies', index_col=0, skiprows=1)
    start_sim = databook.parse("other_par", index_col=0)['value']['start_day']
    for pol_name, row in pols.iterrows():

        # get the number of days til policy starts and ends (relative to simulation start)
        start_pol = row['Date implemented (implicitly or explicitly)']
        end_pol = row['Date ended/replaced']
        if not pd.isna(start_pol):
            days_to_start = _get_ndays(start_sim, start_pol)
            n_days = [days_to_start]
            if not pd.isna(end_pol):
                days_to_end = _get_ndays(start_sim, end_pol)
                n_days.append(days_to_end)
            policies['policy_dates'][pol_name] = n_days

        # check if there is a change in beta values on this layer (i.e. change in transmission risk)
        beta_vals = row['beta':'aged_care']
        beta_change = beta_vals.prod()  # multiply series together
        if not math.isclose(beta_change, 1, abs_tol=1e-9):
            policies['beta_policies'][pol_name] = {}
            for layer_key in all_lkeys:
                beta = row['beta']
                beta_layer = row[layer_key]
                policies['beta_policies'][pol_name][layer_key] = beta * beta_layer

        # policies impacting imported cases
        imports = row['imported_infections']
        if imports > 0:
            policies['import_policies'][pol_name] = {'n_imports': imports}

        # policies that remove people from layers
        to_clip = [row['clip_edges_layer'], row['clip_edges']]
        percent_to_clip = to_clip[1]
        if not pd.isna(percent_to_clip):
            policies['clip_policies'][pol_name] = {}
            policies['clip_policies'][pol_name]['change'] = percent_to_clip
            layers_to_clip = to_clip[0]
            if not pd.isna(layers_to_clip):
                policies['clip_policies'][pol_name]['layers'] = [lk for lk in all_lkeys if lk in layers_to_clip]
            else:
                policies['clip_policies'][pol_name]['layers'] = all_lkeys

    # TODO: this needs to go in spreadsheet
    # add in tracing policies, currently just app
    policies['trace_policies'] = {
        'tracing_app': {'layers': ['H', 'S', 'C', 'Church', 'pSport', 'cSport', 'entertainment', 'cafe_restaurant',
                                   'pub_bar', 'transport', 'national_parks', 'public_parks', 'large_events',
                                   'social'],
                        # Layers which the app can target, excluding beach, child_care and aged_care
                        'coverage': [0.05],  # app coverage at time in days
                        'dates': [60],  # days when app coverage changes
                        'trace_time': 0,
                        'start_day': 60,
                        'end_day': None}}
    policies['policy_dates']['tracing_app'] = [policies['trace_policies']['tracing_app']['start_day']]

    return policies


def get_layer_keys(databook):
    """
    Get the names of custom layers
    :param databook:
    :return:
    """
    layers = databook.parse('layers', index_col=0)
    allkeys = layers.index.tolist()
    default_keys = utils.default_layer_keys()
    custom_keys = list(set(allkeys) - set(default_keys))  # remove custom keys
    all_dynamic_keys = utils._dynamic_layer_keys()
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


def read_epi_data(where, **kwargs):
    """By default, will return daily global data from URL below"""
    if where == 'url':
        url = utils.epi_data_url()
        epidata = pd.read_csv(url, **kwargs)
    else:
        epidata = pd.read_csv(where, **kwargs)
    return epidata


def format_epidata(epidata):
    """Convert the dataframe to a dictionary of dataframes, where the key is the location"""
    epidata_dict = {}
    countries = epidata['location'].unique()
    for c in countries:
        this_country = epidata.loc[epidata['location'] == c]
        this_country = this_country.reset_index(drop=True)  # reset row numbers
        this_country = this_country[['date', 'new_cases', 'new_deaths', 'total_cases', 'total_deaths']]  # drop unwanted columns
        epidata_dict[c] = this_country
    return epidata_dict


def get_epi_data(where='url', **kwargs):
    epidata = read_epi_data(where=where, **kwargs)
    epidata = format_epidata(epidata)
    return epidata


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


def load_databook(db_path):
    databook = pd.ExcelFile(db_path)
    return databook


def read_params(databook):
    """
    Read all the necessary parameters from the databook
    """

    pars = _get_pars(databook)
    extrapars = _get_extrapars(databook)
    layerchars = _get_layerchars(databook)
    return pars, extrapars, layerchars
