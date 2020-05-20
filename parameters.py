class Parameters:
    """
    The Parameters class is a container for the various types of parameters
    required for an application of Covasim.
    Some parameter attributes are used directly by Covasim while others
    are used both prior to and during the simulation to provide greater
    resolution than Covasim currently provides.

    Args:
        pars (dict): parameters used directly by Covasim
        metapars (dict): meta-parameters used directly by Covasim
        extrapars (dict): additional parameters that allow greater layer resolution
        layerchars (dict): network characteristics that determine from which subset of the population the layers are generated
    """

    def __init__(self,
                 setting=None,
                 pars=None,
                 metapars=None,
                 extrapars=None,
                 layerchars=None,
                 imported_cases=None,
                 daily_tests=None,
                 betavals=None,
                 epidata_loc=None):

        self.setting = setting
        self.pars = pars
        self.metapars = metapars
        self.extrapars = extrapars
        self.layerchars = layerchars
        self.imported_cases = imported_cases
        self.daily_test = daily_tests
        self.betavals = betavals
        self.epidata_loc = epidata_loc

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
