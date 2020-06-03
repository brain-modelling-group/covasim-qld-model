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


def _get_layers(locations, databook):
    # household
    hlayer = databook.parse('layer-household', header=0, index_col=0)
    hlayer = hlayer.loc[locations].to_dict(orient='index')

    # school
    slayer = databook.parse('layer-school', header=0, index_col=0)
    slayer = slayer.loc[locations].to_dict(orient='index')

    # work
    wlayer = databook.parse('layer-work', header=0, index_col=0)
    wlayer = wlayer.loc[locations].to_dict(orient='index')

    # community
    clayer = databook.parse('layer-community', header=0, index_col=0)
    clayer = clayer.loc[locations].to_dict(orient='index')
    return hlayer, slayer, wlayer, clayer


def _get_pars(locations, databook):
    """
    Read in & format the parameters for each location.
    :return a dictionary of form (location, pars)
    """

    hlayer, slayer, wlayer, clayer = _get_layers(locations, databook)

    # the parameters that are in a different sheet
    other_pars = databook.parse('other_par', index_col=0)
    other_pars = other_pars.loc[locations].to_dict(orient='index')

    # structure the parameters for each country according to Covasim pars dictionary
    all_pars = {}
    for location in locations:
        pars = {}
        h = hlayer[location]
        s = slayer[location]
        w = wlayer[location]
        c = clayer[location]
        o = other_pars[location]
        for key in utils.par_keys():
            if key == 'n_days':
                ndays = _get_ndays(o['start_day'], o['end_day'])
                temp = {key: ndays}
            elif h.get(key) is not None:  # assume if in this, will be in S, W & C
                temp = {key: {'H': h[key],
                              'S': s[key],
                              'W': w[key],
                              'C': c[key]}
                        }
            elif o.get(key) is not None:
                temp = {key: o[key]}
            else:
                warnings.warn(f'Parameter key "{key}" not found in spreadsheet data')
            pars.update(temp)
        all_pars[location] = pars

    return all_pars


def _get_extrapars(locations, databook):

    hlayer, slayer, wlayer, clayer = _get_layers(locations, databook)

    # those in other_par sheet
    other_pars = databook.parse('other_par', index_col=0)
    other_pars = other_pars.loc[locations].to_dict(orient='index')

    all_extrapars = {}
    for location in locations:
        extrapars = {}
        h = hlayer[location]
        s = slayer[location]
        w = wlayer[location]
        c = clayer[location]
        o = other_pars[location]
        for key in utils.extrapar_keys():
            if h.get(key) is not None:  # assume is in this, will be in S, W & C
                temp = {key: {'H': h[key],
                              'S': s[key],
                              'W': w[key],
                              'C': c[key]}
                }
            elif o.get(key) is not None:
                temp = {key: o[key]}
            else:
                warnings.warn(f'Parameter key "{key}" not found in spreadsheet data')
            extrapars.update(temp)
        all_extrapars[location] = extrapars
    return extrapars


def _get_layerchars(locations, databook):

    hlayer, slayer, wlayer, clayer = _get_layers(locations, databook)

    all_layerchars = {}
    for location in locations:
        layerchars = {}
        h = hlayer[location]
        s = slayer[location]
        w = wlayer[location]
        c = clayer[location]
        for key in utils.layerchar_keys():
            if h.get(key) is not None:
                temp = {key: {'H': h[key],
                              'S': s[key],
                              'W': w[key],
                              'C': c[key]}
                }
            else:
                warnings.warn(f'Layer characteristics key "{key}" not found in spreadsheet data')
            layerchars.update(temp)
        all_layerchars[location] = layerchars
    return all_layerchars


def read_policies(locations, databook):
    """
    Read in the policies sheet
    :param databook:
    :return:
    """

    layer_keys = utils.default_layer_keys()

    start_days = databook.parse('other_par', index_col=0, header=0).to_dict(orient='index')
    pol_sheet = databook.parse('policies', index_col=[0,1], header=0)  # index by first 2 cols to avoid NAs in first col

    all_policies = {}
    for location in locations:
        start_sim = start_days[location]['start_day']
        pols = pol_sheet.loc[location]

        policies = {}
        policies['beta_policies'] = {}
        policies['import_policies'] = {}
        policies['clip_policies'] = {}
        policies['policy_dates'] = {}


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
            beta_vals = row['beta':'C']
            beta_change = beta_vals.prod()  # multiply series together
            if not math.isclose(beta_change, 1, abs_tol=1e-9):
                policies['beta_policies'][pol_name] = {}
                for layer_key in layer_keys:
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
                    policies['clip_policies'][pol_name]['layers'] = [lk for lk in layer_keys if lk in layers_to_clip]
                else:
                    policies['clip_policies'][pol_name]['layers'] = layer_keys

        all_policies[location] = policies

    return all_policies


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


def format_epidata(locations, epidata):
    """Convert the dataframe to a dictionary of dataframes, where the key is the location"""
    if isinstance(locations, str):
        locations = [locations]

    epidata_dict = {}
    for l in locations:
        this_country = epidata.loc[epidata['location'] == l]
        this_country = this_country.reset_index(drop=True)  # reset row numbers
        this_country = this_country[['date', 'new_cases', 'new_deaths', 'total_cases', 'total_deaths']]  # drop unwanted columns
        epidata_dict[l] = this_country
    return epidata_dict


def get_epi_data(locations, where, **kwargs):
    epidata = read_epi_data(where, **kwargs)
    epidata = format_epidata(locations, epidata)
    return epidata


def read_contact_matrix(locations, databook):
    """
    Load Prem et al. matrices then transform into a symmetric matrix
    :param databook:
    :return:
    """

    matrix_sheet = databook.parse('contact matrices-home', usecols="A:R", index_col=[0,1])

    all_matrices = {}

    for location in locations:
        mixing_matrix0 = matrix_sheet.loc[location]
        contact_matrix = {}
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

        all_matrices[location] = contact_matrix

    return all_matrices


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
