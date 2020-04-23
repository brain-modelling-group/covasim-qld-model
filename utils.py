import sciris as sc



beta_eff2 = np.array((
    (1.02,    1,      1,      0.98,        1,      1), # day 15: international travellers self isolate, public events >500 people cancelled
                     (1.05,    0.75,    1,    0.9,      0.0,      1), # day 19: indoor gatherings limited to 100 people
                     (1.06,    0.5,    0.88,    0.82,      0.0,    0.0), # day 22: pubs/bars/cafes take away only, church/sport etc. cancelled
                     (1.13,    0.25,    0.67,   0.55,     0.0,    0.0), # day 29: public gatherings limited to 2 people
                     (1,1,1,1,1,1))) # go back to pre-lockdown

beta_eff_relax = np.array((
                    (1,    1,      1,      1.04,        0.0,      0.0), # day 60: relax outdoor gatherings to 10 people
                     (1,    1,    1.05,    1.27,      0.0,      0.0), # day 60: non-essential retail outlets reopen
                     (1,    1,    1.04,    1.16,      0.0,    0.0), # day 60: restaurants/cafes/bars allowed to do eat in with 4 sq m distancing
                     (1,    1,    1,    1.04,      0.0,      0.0), # day 60: relax outdoor gatherings to 200 people
                     (1,    1,    1,    1.08,      0.0,      0.0), # day 60: community sports reopen
                     (1,    1.75,    1,   1,     0.0,    0.0), # day 60: childcare and schools reopen
                     (1,    1,    1.33,   1,     0.0,    0.0), # day 60: non-essential work reopens
                     (1,    1,    1,   1,     0.0,    1), # day 60: professional sport without crowds allowed
                     (1,    1,    1,   1,     1,    0.0), # day 60: places of worship reopen
                     (1,1,1,1,1,1))) # go back to pre-lockdown

default_layers = ['H', 'S', 'W', 'C', 'Church', 'pSport']




class BetaIntervention:


    def __init__(self, **rel_betas):
        """

        Args:
            name: The name of the intervention represented by these scale factors
            beta_change: Array same length as BetaIntervention.layers with the relative change in beta
        """
        self.rel_betas = dict.fromkeys(self.layers,1) # Betas default to having 1
        assert set(rel_betas.keys()).issubset(self.layers), 'Some of the layer names do not match the recognized names (%s)' % (self.layers) # Check the arguments match
        self.rel_betas = sc.mergedicts(dict.fromkeys(self.layers,1), rel_betas)


        for k,v in rel_betas:

        assert len(beta_scale) == len(self.layers)
        self.name = name
        self.beta_scale = beta_scale


beta_interventions =

intervention_effects = {
beta_eff2 = np.array((

    'international_travel_isolation': dict(H=1.02, S=1, W=1, C=0.98, Church=1, pSport=1), # day 15: international travellers self isolate, public events >500 people cancelled
    'indoor_gatherings_100_max':(1.05,    0.75,    1,    0.9,      0.0,      1),

# day 19: indoor gatherings limited to 100 people
                     :(1.06,    0.5,    0.88,    0.82,      0.0,    0.0), # day 22: pubs/bars/cafes take away only, church/sport etc. cancelled
                     :(1.13,    0.25,    0.67,   0.55,     0.0,    0.0), # day 29: public gatherings limited to 2 people


:(1, 1, 1, 1, 1, 1)))  # go back to pre-lockdown



beta_eff_relax = np.array(((1,    1,      1,      1.04,        0.0,      0.0), # day 60: relax outdoor gatherings to 10 people
                     (1,    1,    1.05,    1.27,      0.0,      0.0), # day 60: non-essential retail outlets reopen
                     (1,    1,    1.04,    1.16,      0.0,    0.0), # day 60: restaurants/cafes/bars allowed to do eat in with 4 sq m distancing
                     (1,    1,    1,    1.04,      0.0,      0.0), # day 60: relax outdoor gatherings to 200 people
                     (1,    1,    1,    1.08,      0.0,      0.0), # day 60: community sports reopen
                     (1,    1.75,    1,   1,     0.0,    0.0), # day 60: childcare and schools reopen
                     (1,    1,    1.33,   1,     0.0,    0.0), # day 60: non-essential work reopens
                     (1,    1,    1,   1,     0.0,    1), # day 60: professional sport without crowds allowed
                     (1,    1,    1,   1,     1,    0.0), # day 60: places of worship reopen
                     (1,1,1,1,1,1))) # go back to pre-lockdown




}