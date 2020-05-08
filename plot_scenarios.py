def plot_scenarios(scenario_number, extra_pars):
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