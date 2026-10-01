"""CLI: list applicants, underwrite one, run the edge-case eval."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import agents
from .data import APPLICANTS
from .models import Applicant


def run_underwrite(app_id: str) -> int:
    app = APPLICANTS.get(app_id)
    if app is None:
        print(f"unknown applicant: {app_id}")
        return 1
    assessment = agents.score(app)
    print(f"applicant: {app.id}  ({app.purpose}, {app.employment_status})")
    print(f"  income {app.income}  debt/mo {app.monthly_debt}  "
          f"loan {app.loan_amount}  value {app.asset_value}  score {app.credit_score}")
    print(f"  DTI {assessment.dti}  LTV {assessment.ltv}  tier {assessment.credit_tier}")
    for f in assessment.flags:
        print(f"  [{f.severity:8s}] {f.code}: {f.message}")
    print(f"  decision: {assessment.decision}  ({assessment.rationale})")
    print(f"  narration: {agents.narrate(assessment)}")
    print(f"  advisory:  {agents.advise(assessment)}")
    return 0


def run_eval(cases_path: Path) -> int:
    cases = json.loads(cases_path.read_text())
    failures = 0
    for case in cases:
        app = APPLICANTS[case["applicant"]]
        a = agents.score(app)
        ok = a.decision == case["expected_decision"]
        if not ok:
            failures += 1
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case['applicant']}: {a.decision} "
              f"(expected {case['expected_decision']})")
    print(f"\nresult: {'ALL PASS' if failures == 0 else f'{failures} FAILURE(S)'}")
    return 0 if failures == 0 else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="underwriting")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")

    u = sub.add_parser("underwrite")
    u.add_argument("app_id")

    e = sub.add_parser("eval")
    e.add_argument("--cases", default=None)

    args = p.parse_args(argv)
    if args.cmd == "list":
        for app in APPLICANTS.values():
            a = agents.score(app)
            print(f"{app.id:8s} {a.decision:22s} DTI {a.dti:.2f}  LTV {a.ltv:.2f}  score {app.credit_score}")
        return 0
    if args.cmd == "underwrite":
        return run_underwrite(args.app_id)
    if args.cmd == "eval":
        default = Path(__file__).resolve().parents[2] / "evals" / "cases.json"
        return run_eval(Path(args.cases) if args.cases else default)
    return 2


if __name__ == "__main__":
    sys.exit(main())
