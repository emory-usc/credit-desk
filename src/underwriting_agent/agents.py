"""The four roles. Each is deterministic and composes the output of the one
before it. The narrative is templated from the flags the scoring role actually
raised, so it cannot describe a risk that was not measured.
"""

from __future__ import annotations

from .models import Applicant, Assessment
from . import rules


def extract(app: Applicant) -> dict:
    """Role 1: document extraction — normalize the applicant's fields."""
    return {
        "id": app.id,
        "income": app.income,
        "monthly_debt": app.monthly_debt,
        "loan_amount": app.loan_amount,
        "asset_value": app.asset_value,
        "credit_score": app.credit_score,
        "employment_status": app.employment_status,
        "purpose": app.purpose,
    }


def score(app: Applicant) -> Assessment:
    """Role 2: compute DTI, LTV, credit tier, and the decision."""
    return rules.assess(app)


def narrate(assessment: Assessment) -> str:
    """Role 3: templated risk narrative from measured flags only."""
    parts = [
        f"DTI {assessment.dti:.2f}, LTV {assessment.ltv:.2f}, "
        f"credit tier {assessment.credit_tier}."
    ]
    for f in assessment.flags:
        parts.append(f"[{f.severity}] {f.code}: {f.message}")
    if not assessment.flags:
        parts.append("No risk flags raised.")
    return " ".join(parts)


def advise(assessment: Assessment) -> dict:
    """Role 4: advisory recommendation. Explicitly NOT a decision."""
    return {
        "applicant_id": assessment.applicant_id,
        "recommendation": assessment.decision,
        "rationale": assessment.rationale,
        "advisory": True,
        "disclaimer": (
            "Advisory output only — a licensed underwriter makes the final decision."
        ),
    }
