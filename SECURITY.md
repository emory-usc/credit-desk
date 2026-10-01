# Security Policy

## Reporting a vulnerability

Report security issues privately rather than opening a public issue. Include a
description, reproduction steps, and any proposed fix. Do not include real
customer data or credentials in any report.

## Security posture

- **Deterministic math, advisory narration.** Every number (DTI, LTV, credit
  tier, decision) is computed in pure Python. The narrative is templated from
  the flags the scoring role actually raised, so it cannot describe a risk
  that was not measured. No LLM is called and no external service is reached.
- **Advisory only.** Outputs carry `advisory: true` and a disclaimer. This is
  decision support, not a lending decision, and it says so on every response.
- **API-key gate.** The `/underwrite` endpoint requires `X-API-Key`
  (constant-time compare). `/health` and `/ready` are intentionally open for
  probes. The default key is a documented dev-only value — set
  `UNDERWRITING_API_KEY` for anything beyond localhost.
- **Synthetic data only.** The applicant book is deterministic synthetic data.
  No real customer data is involved.
- **No secrets in the repo or image.** The only configurable credential is the
  API key, which comes from the environment at runtime.

## Supported versions

Only the latest `main` branch is supported for security fixes.
