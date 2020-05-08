def plot_scenarios(scenario_number, extra_pars):
    '''
    The required structure for the torun dict is:
    torun[scen_name] = {
                        'turn_off': {'off_pols': [off_pol_1, ..., off_pol_n], 'dates': [day_1, ..., day_n]},
                        'turn_on': {on_pol_1: [start_day_1, end_day_1], ..., on_pol_m: [start_day_m, end_day_m]},
                        'replace': {old_pol_1: {'replacements': [new_pol_11, ..., new_pol_1p], 'dates': [start_day_11, ..., start_day_1p, end_day_1]},
                                    ...
                                    old_pol_q: {'replacements': [new_pol_q1, ..., new_pol_qr], 'dates': [start_day_q1, ..., start_day_qr, end_day_q]}}
                        }

    The baseline scenario is automatically added to the scenarios first.
    The relax all policies scenario must be added to the torun dict as the key 'Full relaxation' or 'Full relax'.
    Adding policies to the turn_off dict must be added as a list of policies and a list of days to turn them off. Works with beta layer, import and clip edges policies.
    The policy being turned off must be on in the baseline or nothing will happen.
    Adding policies to the turn_on dict must be input as a dict of {policy_name: [start_day, end_day]} for each policy,
    with end_day being optional and n_days being used if it is not included. Import policies don't really work here as of yet.
    To add a policy it must either not be running in baseline, or end before start_day otherwise it will not be added (the scenario will still run).
    Adding policies to the replace dict must be input as a dict of dicts in the form
    {policy_name: {'replacements': [policy_1,...,policy_n], 'dates': [start_day_1,..., start_day_n, end_day]}} for each policy,
    with end_day being optional and n_days being used if it is not included. I think import policies work here, but testing hasn't been expansive.
    To add a replacement policy it must either not be running in baseline, or end before start_day otherwise it will not be added (the scenario will still run).

    The function check_policy_changes reads the scenario being run from torun and checks for clashes between policies being turned off/policies being replaced
    and policies being turned on/policies being replaced. It removes clashing policy changes, prioritising replacements over turning policies off/on.
    For example, if the pub_bar0 policy (running from day 21 to n_day) was set in the turn_off dict with a date of day 70 AND it was set
    in the replace dict (as an old_pol) with a date of day 100 then it would be removed from the turn_off dict. I haven't figured out how to check
    consistencies across the replacement policies so please check that they are sensible (e.g., don't replace the same policy twice in the same scenario etc).
    Other checks for whether policies are off/on before being turned off/on are included within the turn_off_policies, turn_on_policies and replace_policies functions.
    '''


    # Show basic range of services
    scenarios = {}
    torun1 = {}
    torun1['Cafes/restaurants open'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun1['Cafes/restaurants open']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    torun1['Cafes/restaurants open']['turn_off'] = {'off_pols': ['cafe_restaurant0'], 'dates': [extra_pars['relax_day']]}
    torun1['Pubs/bars open'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun1['Pubs/bars open']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    torun1['Pubs/bars open']['turn_off'] = {'off_pols': ['pub_bar0'], 'dates': [extra_pars['relax_day']]}
    torun1['Schools'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun1['Schools']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    torun1['Schools']['turn_off'] = {'off_pols': ['schools'], 'dates': [extra_pars['relax_day']]}
    torun1['Non-essential workers'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun1['Non-essential workers']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    torun1['Non-essential workers']['turn_off'] = {'off_pols': ['NE work'], 'dates': [extra_pars['relax_day']]}
    torun1['Non-essential workers'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun1['Non-essential workers']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    torun1['Non-essential workers']['turn_off'] = {'off_pols': ['NE work'], 'dates': [extra_pars['relax_day']]}
    torun1['Community sports start'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun1['Community sports start']['turn_off'] = {'off_pols': ['cSports'], 'dates': [extra_pars['relax_day']]}
    torun1['Community sports start']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    torun1['Social gatherings <10'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun1['Social gatherings <10']['turn_off'] = {'off_pols': ['social'], 'dates': [extra_pars['relax_day']]}
    torun1['Social gatherings <10']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}
    torun1['Large events'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun1['Large events']['turn_off'] = {'off_pols': ['large_events'], 'dates': [extra_pars['relax_day']]}
    torun1['Large events']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    scenarios['1'] = torun1

    torun2 = {}
    torun2['Pubs/bars open with app'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun2['Pubs/bars open with app']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}
    torun2['Pubs/bars open with app']['turn_off'] = {'off_pols': ['pub_bar0'], 'dates': [extra_pars['relax_day']]}
    torun2['Pubs/bars open'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun2['Pubs/bars open']['turn_off'] = {'off_pols': ['pub_bar0', 'tracing_app'], 'dates': [extra_pars['relax_day'], extra_pars['relax_day']+1]}
    torun2['Pubs/bars open']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}

    scenarios['2'] = torun2

    torun = {}
    # torun['Full relax'] = {}
    # torun['test1'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['test1']['turn_off']['Schools'] = ['schools']
    # torun['test1']['turn_off']['Pubs'] = ['pub_bar0']
    # torun['test1']['turn_off']['schools + pubs'] = ['schools', 'pub_bar0']
    # torun['test1']['turn_off']['Border opening'] = ['travel_dom']
    # torun['test1']['turn_off'] = {'off_pols': ['schools', 'retail', 'pub_bar0', 'travel_dom'], 'dates': [60, 60, 65, 70]}
    # torun['test1']['turn_on']['child_care'] = [60, 150]
    # torun['test1']['turn_on']['NE_health'] = [60, 120]
    # torun['test1']['turn_on']['schools'] = [80, 200]
    # torun['test1']['replace']['outdoor2'] = {'replacements': ['outdoor10', 'outdoor200'], 'dates': [60, 90, 150]}
    # torun['test1']['replace']['NE_work'] = {'replacements': ['church_4sqm'], 'dates': [70, 150]}
    # torun['Relax physical distancing'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Relax physical distancing']['replace']['communication'] = {'replacements': ['comm2'], 'dates': [60]}

    # torun['Schools open'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Schools open']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}
    # torun['Schools open']['turn_off'] = {'off_pols': ['schools'], 'dates': [extra_pars['relax_day']]}
    torun['Pubs open'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun['Pubs open']['replace']['communication'] = {'replacements': ['comm_relax'],
                                                      'dates': [extra_pars['relax_day']]}
    torun['Pubs open']['turn_off'] = {'off_pols': ['pub_bar0'], 'dates': [extra_pars['relax_day']]}
    # torun['Community sports start'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Community sports start']['turn_off'] = {'off_pols': ['cSports', 'communication'], 'dates': [extra_pars['relax_day'], extra_pars['relax_day']]}
    # torun['Cafe/restaurant open with 4sqm'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Cafe/restaurant open with 4sqm']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}
    # torun['Cafe/restaurant open with 4sqm']['replace']['cafe_restaurant0'] = {'replacements': ['cafe_restaurant_4sqm'], 'dates': [extra_pars['relax_day']]}
    # torun['Large events'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Schools + relax']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [60]}
    # torun['Large events']['turn_off'] = {'off_pols': ['large_events'], 'dates': [60]}
    # torun['Large events']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}
    # torun['Return non-essential workers'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Return non-essential workers']['turn_off'] = {'off_pols': ['NE_work'], 'dates': [extra_pars['relax_day']]}
    # torun['Social gatherings <10'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Social gatherings <10']['turn_off'] = {'off_pols': ['social'], 'dates': [extra_pars['relax_day']]}
    # torun['Social gatherings <10']['replace']['communication'] = {'replacements': ['comm_relax'], 'dates': [extra_pars['relax_day']]}
    # torun['Pub+cafe+events+sport'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Pub+cafe+events+sport']['turn_off'] = {'off_pols': ['large_events', 'pub_bar0', 'cafe_restaurant0', 'cSports'], 'dates': [60,90,120,150]}
    # torun['Pub+cafe+events+sport']['replace']['communication'] = {'replacements': ['comm_relax'],'dates': [extra_pars['relax_day']]}

    # torun['Trace app off then replace schools'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    # torun['Trace app off'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}
    torun['pub bar no app'] = {'turn_off': {}, 'turn_on': {}, 'replace': {}}

    # torun['Trace app off then replace schools']['turn_off'] = {'off_pols': ['tracing_app'], 'dates': [100]}
    # torun['Trace app off then replace schools']['replace']['schools'] = {'replacements': ['tracing_app'], 'dates': [120]}
    # torun['Trace app off']['turn_off'] = {'off_pols': ['tracing_app'], 'dates': [100]}
    torun['pub bar no app']['turn_off'] = {'off_pols': ['pub_bar0', 'tracing_app'],
                                           'dates': [extra_pars['relax_day'], extra_pars['relax_day'] + 1]}
    torun['pub bar no app']['replace']['communication'] = {'replacements': ['comm_relax'],
                                                           'dates': [extra_pars['relax_day']]}
    # torun['Trace app off then on']['turn_on'] = {'tracing_app': [60]}

    torun = scenarios[scenario_number]
    return torun