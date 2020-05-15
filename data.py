"""Class for storing and managing project data"""
import covasim as cv
import pandas as pd


class Data:
    def __init__(self, setting=None):
        self.setting = setting
        self.pars = {}
        self.metapars = {}
        self.popdata = {}
        self.policies = {}
        self.other_pars = {}
        self.parnames = ['contacts', 'beta_layer', 'quar_eff']

    def read_pars(self, databook):
        """Read parameter values from databook"""

        # read in networks (layers)
        layers = databook.parse("layers", index_col=0)
        layers = layers.to_dict(orient="dict")

        # create parameters dict
        self.pars = {key: layers.get(key) for key in self.parnames}
        return

    def read_metapars(self, databook):
        # TODO
        return

    def update_pars(self, newpars):
        """Update values in self.pars with those in newpars"""

        if set(newpars.keys()) != set(self.pars.keys()):
            print("Warning: new keys and values will be added to the existing parameters dictionary")

        self.pars.update(newpars)
        return

    def update_metapars(self, new_metapars):
        """Update values in self.metapars with those in new_metapars"""

        if set(new_metapars.keys()) != set(self.metapars.keys()):
            print("Warning: new keys and values will be added to the existing meta-parameters dictionary")

        self.metapars.update(new_metapars)
        return

def _get_pars(dataobj, databook):
    """"""
    dataobj.read_pars(databook)
    pars = cv.make_pars(**dataobj.pars)
    dataobj.update_pars(pars)
    return dataobj

# TODO: usage of such strutures needs to be rethought.
# TODO: Perhaps splitting up spreadsheet differently will help
# def _get_metapars(dataobj, databook):

#     metapars = cv.make_metapars()  # defaults
#     other_pars = databook.parse("other_par", index_col=0)['value']
#     other_pars = other_pars.to_dict()
#     metapars['n_runs'] = other_pars
#     return


def load_databook(file_path, file_name):
    databook = pd.ExcelFile(f'{file_path}/{file_name}.xlsx')
    return databook


def setup_dataobj(file_path, file_name, setting):
    databook = load_databook(file_path, file_name)
    dataobj = Data(setting)
    dataobj = _get_pars(dataobj, databook)
    # dataobj = _get_metapars(dataobj, databook)
    return dataobj