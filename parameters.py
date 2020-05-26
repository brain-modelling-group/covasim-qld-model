import data


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
                 policies=None,
                 household_dist=None,
                 age_dist=None,
                 contact_matrix=None,
                 imported_cases=None,
                 daily_tests=None,
                 beta_vals=None,
                 all_lkeys=None,
                 default_lkeys=None,
                 custom_lkeys=None,
                 dynamic_lkeys=None):

        self.setting = setting
        self.pars = pars
        self.metapars = metapars
        self.extrapars = extrapars
        self.layerchars = layerchars
        self.policies = policies
        self.household_dist = household_dist
        self.age_dist = age_dist
        self.contact_matrix = contact_matrix
        self.imported_cases = imported_cases
        self.daily_test = daily_tests
        self.beta_vals = beta_vals
        self.all_lkeys = all_lkeys
        self.default_lkeys = default_lkeys
        self.custom_lkeys = custom_lkeys
        self.dynamic_lkeys = dynamic_lkeys

    def update_pars(self, newpars, verbose=1):
        """Update values in self.pars with those in newpars"""
        if newpars is None:
            return

        if verbose:
            print("The following will be updated in the parameters dictionary...")
            for key in newpars.keys():
                print(key)

        self.pars.update(newpars)
        return

    def update_metapars(self, new_metapars, verbose=1):
        """Update values in self.metapars with those in new_metapars"""
        if new_metapars is None:
            return

        if verbose:
            print("The following will be updated in the meta-parameters dictionary...")
            for key in new_metapars.keys():
                print(key)

        self.metapars.update(new_metapars)
        return

    def print_pars(self):
        print("--- PARAMETERS ---")
        for key, value in sorted(self.pars.items()):
            print(f'- {key}: {value}')

    def print_metapars(self):
        print("--- METAPARAMETERS ---")
        for key, value in sorted(self.metapars.items()):
            print(f'- {key}: {value}')


def setup_params(root, file_name, setting, metapars):
    """Read in the required parameter types and put in container
    :return a Parameters container object"""

    databook = data.load_databook(root, file_name)

    # get the several parameter types & layer names
    pars, extrapars, layerchars = data.read_params(databook)
    all_lkeys, default_lkeys, custom_lkeys, dynamic_lkeys = data.get_layer_keys(databook)

    policies = data.read_policies(databook, all_lkeys)

    imported_cases, daily_tests = [None, None]  # data.read_tests_imported(databook)  # TODO: fix

    # read in a store population-related data
    age_dist, household_dist = data.read_popdata(databook)

    # get mixing matrix & age brackets
    contact_matrix = data.read_contact_matrix(databook)

    params = Parameters(setting=setting,
                        pars=pars,
                        metapars=metapars,
                        extrapars=extrapars,
                        layerchars=layerchars,
                        policies=policies,
                        household_dist=household_dist,
                        age_dist=age_dist,
                        contact_matrix=contact_matrix,
                        imported_cases=imported_cases,
                        daily_tests=daily_tests,
                        all_lkeys=all_lkeys,
                        default_lkeys=default_lkeys,
                        custom_lkeys=custom_lkeys,
                        dynamic_lkeys=dynamic_lkeys)
    return params
