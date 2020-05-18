import data


class Parameters:
    def __init__(self,
                 setting=None,
                 pars=None,
                 metapars=None,
                 extrapars=None,
                 betavals=None):

        self.setting = setting
        self.pars = pars
        self.metapars = metapars
        self.extrapars = extrapars
        self.betavals = betavals

    def update_pars(self, newpars):
        """Update values in self.pars with those in newpars"""

        if set(newpars.keys()) != set(self.pars.keys()):
            print("Warning: new keys and values will be added to the existing parameters dictionary")

        self.pars.update(newpars)
        return

    def update_metapars(self, new_metapars):
        if set(new_metapars.keys()) != set(self.metapars.keys()):
            print("Warning: new keys and values will be added to the existing meta-parameters dictionary")

        self.metapars.update(new_metapars)
        return


def get_parameters(root, file_name, setting):
    # read all data
    pars, metapars = data.read_data(root, file_name)

    # create Parameters object & populate
    params = Parameters(setting=setting,
                        pars=pars,
                        metapars=metapars)
    return params



class PopulationData:
    def __init__(self):
        self.foo = None

