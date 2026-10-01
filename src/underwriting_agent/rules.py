"""Deterministic underwriting rules: DTI, LTV, credit tier, decision."""

from __future__ import annotations

from .models import Applicant, Assessment, Flag


def dti(app: Applicant) -> float:
    return round(app.monthly_debt / (app.income / 12.0), 4)


def ltv(app: Applicant) -> float:
    return round(app.loan_amount / app.asset_value, 4)


def credit_tier(score: int) -> str:
    if score >= 720:
        return "prime"
    if score >= 680:
        return "near-prime"
    if score >= 640:
        return "subprime"
    return "below-subprime"


def assess(app: Applicant) -> Assessment:
    d = dti(app)
    l = ltv(app)
    tier = credit_tier(app.credit_score)
    flags: list[Flag] = []

    if app.credit_score < 640:
        flags.append(Flag("LOW_SCORE", "blocking", "credit score below 640"))
    elif app.credit_score < 680:
        flags.append(Flag("SCORE_WATCH", "warning", "credit score below 680"))

    if d > 0.50:
        flags.append(Flag("HIGH_DTI", "blocking", "DTI exceeds 0.50"))
    elif d > 0.43:
        flags.append(Flag("DTI_WATCH", "warning", "DTI exceeds 0.43"))

    if l > 1.0:
        flags.append(Flag("NEGATIVE_EQUITY", "blocking", "loan exceeds collateral value"))
    elif l > 0.90:
        flags.append(Flag("LTV_WATCH", "warning", "LTV exceeds 0.90"))

    if app.employment_status == "unemployed":
        flags.append(Flag("NO_INCOME", "blocking", "no active employment"))

    blocking = [f for f in flags if f.severity == "blocking"]
    warnings = [f for f in flags if f.severity == "warning"]

    if blocking:
        decision = "decline"
        rationale = "blocking conditions: " + "; ".join(f.code for f in blocking)
    elif warnings:
        decision = "approve-with-conditions"
        rationale = "conditions: " + "; ".join(f.code for f in warnings)
    else:
        decision = "approve"
        rationale = "all ratios within policy thresholds"

    return Assessment(
        applicant_id=app.id,
        dti=d,
        ltv=l,
        credit_tier=tier,
        flags=tuple(flags),
        decision=decision,
        rationale=rationale,
    )
