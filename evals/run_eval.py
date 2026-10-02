"""Standalone eval runner for Credit Desk."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from underwriting_agent import agents  # noqa: E402
from underwriting_agent.data import APPLICANTS  # noqa: E402


def main() -> int:
    cases = json.loads((Path(__file__).parent / "cases.json").read_text())
    failures = 0
    for case in cases:
        a = agents.score(APPLICANTS[case["applicant"]])
        ok = a.decision == case["expected_decision"]
        if not ok:
            failures += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {case['applicant']}: "
              f"{a.decision} (expected {case['expected_decision']})")
    print(f"\nresult: {'ALL PASS' if failures == 0 else f'{failures} FAILURE(S)'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
