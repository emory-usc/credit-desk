"""Domain models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Applicant:
    id: str
    income: float            # annual, USD
    monthly_debt: float      # existing monthly debt service, USD
    loan_amount: float       # requested
    asset_value: float       # collateral value
    credit_score: int
    employment_status: str   # employed | self-employed | unemployed
    purpose: str             # auto | home | personal


@dataclass(frozen=True)
class Flag:
    code: str
    severity: str            # info | warning | blocking
    message: str


@dataclass(frozen=True)
class Assessment:
    applicant_id: str
    dti: float
    ltv: float
    credit_tier: str
    flags: tuple[Flag, ...] = field(default_factory=tuple)
    decision: str = "pending"
    rationale: str = ""
