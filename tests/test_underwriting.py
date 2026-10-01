"""Tests for underwriting-agent."""

from underwriting_agent import agents, rules
from underwriting_agent.data import APPLICANTS


def test_dti_computation():
    app = APPLICANTS["app-001"]
    assert rules.dti(app) == round(1400 / (95000 / 12.0), 4)


def test_ltv_computation():
    app = APPLICANTS["app-001"]
    assert rules.ltv(app) == round(28000 / 32000, 4)


def test_credit_tiers():
    assert rules.credit_tier(780) == "prime"
    assert rules.credit_tier(700) == "near-prime"
    assert rules.credit_tier(655) == "subprime"
    assert rules.credit_tier(590) == "below-subprime"


def test_clean_applicant_approves():
    a = agents.score(APPLICANTS["app-001"])
    assert a.decision == "approve"
    assert not a.flags


def test_low_score_declines():
    a = agents.score(APPLICANTS["app-007"])
    assert a.decision == "decline"
    assert any(f.code == "LOW_SCORE" for f in a.flags)


def test_unemployed_declines():
    a = agents.score(APPLICANTS["app-008"])
    assert a.decision == "decline"
    assert any(f.code == "NO_INCOME" for f in a.flags)


def test_narration_only_mentions_measured_flags():
    a = agents.score(APPLICANTS["app-006"])
    text = agents.narrate(a)
    # app-006 is below 640 with high DTI, so both are legitimately measured
    assert "HIGH_DTI" in text
    assert "LOW_SCORE" in text
    # but app-006 is employed, so the narration must NOT fabricate an income flag
    assert "NO_INCOME" not in text


def test_advice_is_explicitly_advisory():
    a = agents.score(APPLICANTS["app-001"])
    advice = agents.advise(a)
    assert advice["advisory"] is True
    assert "final decision" in advice["disclaimer"]
