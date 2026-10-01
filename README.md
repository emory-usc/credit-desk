# Underwriting Agent

[![CI](https://github.com/emory-usc/underwriting-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/emory-usc/underwriting-agent/actions/workflows/ci.yml)

A deterministic, multi-role loan-underwriting pipeline with a FastAPI delivery
surface. It demonstrates a pattern that matters for governed AI systems:

**the math is Python; the narration is advisory.**

Four narrow roles run in sequence, none of which can invent a number:

| Role | What it does |
|---|---|
| `extract` | Normalizes applicant fields (the document-extraction step) |
| `score` | Computes DTI, LTV, and a credit tier — pure deterministic math |
| `narrate` | Produces a templated risk narrative from the flags the scorer actually raised |
| `advise` | Emits a recommendation, labeled **advisory, not a decision** |

The decision is a deterministic function of the computed ratios, not an LLM
opinion. The narrative is templated from measured flags, so it can never
describe a risk that wasn't measured.

## Decision rules

| Condition | Outcome |
|---|---|
| credit score < 640 | decline |
| DTI > 0.50 | decline |
| LTV > 1.0 | decline |
| unemployed | decline |
| DTI > 0.43, or LTV > 0.90, or score < 680 | approve with conditions |
| otherwise | approve |

## Quick start

```bash
pip install -e ".[web]"
underwriting list            # CLI view of the whole book
underwriting eval            # edge-case decision eval
uvicorn underwriting_agent.server:app --port 8000   # the API
```

### API

```
GET  /health                   liveness (unauthenticated, for probes)
GET  /ready                    readiness (applicant book loaded)
POST /underwrite               run the pipeline for one applicant
     headers: X-API-Key: <key>   (constant-time compare; dev default: dev-key)
```

```bash
curl -X POST http://localhost:8000/underwrite \
  -H "X-API-Key: dev-key" -H "Content-Type: application/json" \
  -d '{"applicant_id": "app-001"}'
```

## Wrapping as a LangChain tool

The pipeline is a pure function, so exposing it to an agent is one decorator:

```python
from langchain_core.tools import tool
from underwriting_agent import agents
from underwriting_agent.data import APPLICANTS

@tool
def underwrite_applicant(applicant_id: str) -> str:
    """Run the deterministic underwriting pipeline for an applicant. Advisory only."""
    a = agents.score(APPLICANTS[applicant_id])
    return f"{a.decision}: {a.rationale}"
```

The agent can narrate the result, but the number it narrates was computed in
Python — the pattern this repo exists to demonstrate.

## Deployment

- `Dockerfile` — multi-stage uv build, slim non-root runtime, healthcheck.
- `infra/main.bicep` — Container Apps with scale-to-zero, Log Analytics +
  App Insights, `/health` liveness probe, API key injected as a secure
  parameter. Compiles clean (`az bicep build`).
- `.github/workflows/deploy.yml` — GHCR build/push, Trivy scan (blocking on
  CRITICAL/HIGH), OIDC Bicep deploy on version tags.

## Security posture

See `SECURITY.md`. The short version: deterministic math, advisory-only
outputs, API-key gate, synthetic data, no secrets in the repo.

## Honest note

No LLM is called. The "agent" roles are deterministic Python functions. In a
production build they would be wired to a real model for the narrative step
only, with the scoring role remaining pure code — which is exactly the
separation this repo is built to demonstrate.
