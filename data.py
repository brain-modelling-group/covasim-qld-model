"""Class for storing and managing project data"""
import covasim as cv
import os
import pandas as pd
import sciris as sc
import warnings


def par_keys():
    par_keys = ['contacts', 'beta_layer', 'quar_eff',
                'pop_size', 'pop_scale', 'rescale',
                'rescale_threshold', 'rescale_factor',
                'pop_infected', 'start_day', 'end_day',
                'n_days', 'diag_factor']
    return par_keys


def metapar_keys():
    metapar_keys = ['n_runs', 'noise']
    return metapar_keys


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

    pars = cv.make_pars(**pars)
    return pars


def _get_metapars():
    # TODO: ignoring spreadsheet currently, should all be set in code
    metapars = cv.make_metapars()
    return metapars


# TODO:
def _get_extrapars(databook):
    pass


def load_databook(root, file_name):
    file_path = os.path.join(root, 'data', file_name)
    file_path += '.xlsx'
    databook = pd.ExcelFile(file_path)
    return databook


def read_params(databook):
    pars = _get_pars(databook)
    metapars = _get_metapars()
    # extrapars = _get_extrapars(databook)
    return pars, metapars

def read_popdata(databook):
    pass
    # return popdata
