import covasim as cv
import covasim_australia.utils as utils
import pytest
import sciris as sc
import numpy as np

intervention_args = {
    'symp_prob': 0.5,
    'asymp_prob': 0,
    'symp_quar_prob': 0.9,
    'asymp_quar_prob': 0,
    'test_delay': 2,
    'swab_delay': 3,
    'test_isolation_compliance': 0.8,
    'leaving_quar_prob': 0.75,
}

t = 10
_sim = cv.Sim(pop_size=1, pop_infected=0)
_sim.initialize()
_sim.t = t

@pytest.fixture
def intervention():
    return utils.test_prob_with_quarantine(**intervention_args)

@pytest.fixture
def sim():
    return sc.dcp(_sim)


def check_prob(sim, intervention, expected_probability):
    test_probs = intervention.apply(sc.dcp(sim))
    assert test_probs[0] == expected_probability


def test_swab_delay(sim, intervention):
    # 1. People who become symptomatic in the general community will wait `swab_delay` days before getting tested, at rate `symp_prob`
    sim.people.symptomatic[0] = True
    sim.people.date_symptomatic[0] = 10-intervention_args['swab_delay'] # They became symptomatic swab_delay days ago
    check_prob(sim, intervention,intervention_args['symp_prob'])

    sim.people.date_symptomatic[0] += 1 # They became symptomatic one day layer
    check_prob(sim, intervention,intervention_args['asymp_prob'])

    sim.people.date_symptomatic[0] -= 4 # They became symptomatic much earlier and missed their test chance
    check_prob(sim, intervention,intervention_args['asymp_prob'])


def test_quar_test_rate(sim, intervention):
    # 2. People who become symptomatic while in quarantine will test immediately at rate `symp_quar_test`
    sim.people.symptomatic[0] = True
    sim.people.date_symptomatic[0] = t # They became symptomatic today

    sim.people.quarantined[0] = True
    sim.people.date_quarantined[0] = t-5 # They were quarantined some time ago
    sim.people.date_end_quarantine[0] = t+5 # They aren't scheduled to leave quarantine for a while

    check_prob(sim, intervention,intervention_args['symp_quar_prob'])


def test_quar_with_symptoms(sim, intervention):
    # 3. People who are symptomatic and then are ordered to quarantine, will test immediately at rate `symp_quar_test`
    sim.people.symptomatic[0] = True
    sim.people.date_symptomatic[0] = t-5 # They became symptomatic some time ago

    sim.people.quarantined[0] = True
    sim.people.date_quarantined[0] = t-1  # Quarantining happens at the end of a timestep. People who have 'just entered quarantine' would have done so yesterday
    sim.people.date_end_quarantine[0] = t+10 # They aren't scheduled to leave quarantine for a while

    check_prob(sim, intervention,intervention_args['symp_quar_prob'])

def test_severe_symptoms(sim, intervention):
    # 4. People who have severe symptoms will be tested
    sim.people.severe[0] = True
    check_prob(sim, intervention,1)

    # What if they're in quarantine as well?
    sim.people.quarantined[0] = True
    sim.people.date_quarantined[0] = t-1  # Quarantining happens at the end of a timestep. People who have 'just entered quarantine' would have done so yesterday
    sim.people.date_end_quarantine[0] = t+10 # They aren't scheduled to leave quarantine for a while
    check_prob(sim, intervention,1)

    # What if they're about to leave quarantine?
    sim.people.quarantined[0] = True
    sim.people.date_quarantined[0] = t-5
    sim.people.date_end_quarantine[0] = t-intervention_args['test_delay']
    check_prob(sim, intervention,1)
#
#
def test_leaving_quarantine(sim, intervention):
    # 5. People test before leaving quarantine at rate `leaving_quar_prob` (set to 1 to ensure everyone leaving quarantine must have been tested)

    # ASYMPTOMATIC AND LEAVING QUARANTINE
    sim.people.quarantined[0] = True
    sim.people.date_quarantined[0] = 5
    sim.people.date_end_quarantine[0] = t+intervention_args['test_delay']
    check_prob(sim, intervention,intervention_args['leaving_quar_prob'])

    # People can miss their chance to test because it's too late...
    sim.people.date_end_quarantine[0] = t+intervention_args['test_delay']-1
    check_prob(sim, intervention,intervention_args['asymp_quar_prob'])

    # ...or too early
    sim.people.date_end_quarantine[0] = t+intervention_args['test_delay']+1
    check_prob(sim, intervention,intervention_args['asymp_quar_prob'])

    # If they have already been tested during quarantine, then they don't need to be re-tested
    sim.people.date_tested[0] = 6
    sim.people.date_end_quarantine[0] = t+intervention_args['test_delay']
    check_prob(sim, intervention,intervention_args['asymp_quar_prob'])

    # If they were tested before quarantine, they still get tested
    sim.people.date_tested[0] = 4
    check_prob(sim, intervention,intervention_args['leaving_quar_prob'])

    # Now suppose they were already tested during quarantine, but they developed severe symptoms today
    # They should test at the severe rate (1) since this is the higher rate
    sim.people.severe[0] = True
    sim.people.date_severe[0] = t
    sim.people.date_tested[0] = 6
    check_prob(sim, intervention,1)

    # Suppose they are waiting for test results
    sim.people.date_tested[0] = t-1 # Tested yesterday
    check_prob(sim, intervention,0)

def test_already_diagnosed(sim, intervention):
    # 6. People that have been diagnosed will not be tested
    sim.people.symptomatic[0] = True
    sim.people.date_symptomatic[0] = 10-intervention_args['swab_delay'] # They became symptomatic swab_delay days ago
    sim.people.diagnosed[0] = True
    check_prob(sim, intervention,0)


def test_pending_diagnosis(sim, intervention):
    # 7. People that are already waiting for a diagnosis will not be retested
    sim.people.symptomatic[0] = True
    sim.people.date_symptomatic[0] = 10-intervention_args['swab_delay'] # They became symptomatic swab_delay days ago
    sim.people.date_tested[0] = t-1 # They were tested yesterday so they haven't recieved results yet
    check_prob(sim, intervention,0)

    sim.people.date_tested[0] = 0  # They were tested a long time ago (e.g. they came out of quarantine and then subsequently were tested, so they've already recieved a negative result previously)
    check_prob(sim, intervention,intervention_args['symp_prob'])

    return


# def test_isolation_compliance(sim, intervention):
#     # 8. People quarantine while waiting for their diagnosis with compliance `test_isolation_compliance`
#     test_probs = intervention.apply(sim)
#     assert test_probs[0] == 1
#     return
#
#
# def test_quarantine_extension(sim, intervention):
#     # 9. People already on quarantine while tested will not have their quarantine shortened, but if they are tested at the end of their
#     #    quarantine, the quarantine will be extended
#     test_probs = intervention.apply(sim)
#     assert test_probs[0] == 1
#     return

