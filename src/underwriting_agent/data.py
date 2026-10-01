"""Deterministic synthetic applicant book.

Ten applicants chosen to exercise every decision branch, from clean approval
through borderline DTI/LTV to hard decline. All synthetic.
"""

from __future__ import annotations

from .models import Applicant

APPLICANTS: dict[str, Applicant] = {
    a.id: a
    for a in [
        Applicant("app-001", 95000, 1400, 28000, 32000, 780, "employed", "auto"),
        Applicant("app-002", 72000, 1100, 22000, 25000, 745, "employed", "auto"),
        Applicant("app-003", 61000, 1650, 30000, 31000, 700, "employed", "auto"),
        Applicant("app-004", 88000, 900, 26000, 28000, 690, "self-employed", "home"),
        Applicant("app-005", 54000, 1450, 24000, 24000, 655, "employed", "personal"),
        Applicant("app-006", 47000, 2000, 19000, 19000, 620, "employed", "auto"),
        Applicant("app-007", 39000, 800, 20000, 18000, 590, "employed", "auto"),
        Applicant("app-008", 67000, 1200, 21000, 22000, 720, "unemployed", "personal"),
        Applicant("app-009", 112000, 2800, 34000, 36000, 760, "employed", "home"),
        Applicant("app-010", 58000, 1000, 22000, 26000, 705, "employed", "auto"),
    ]
}
