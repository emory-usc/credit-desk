"""FastAPI delivery surface for the underwriting pipeline.

The pipeline itself (score / narrate / advise) is deterministic and has no side
effects; this module only exposes it over HTTP behind an API-key gate.
"""

from __future__ import annotations

import os
import secrets

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

from underwriting_agent import __version__, agents
from underwriting_agent.data import APPLICANTS

_API_KEY = os.environ.get("UNDERWRITING_API_KEY", "dev-key")

app = FastAPI(
    title="underwriting-agent",
    version=__version__,
    description=(
        "Deterministic loan-underwriting decision support. "
        "Advisory only — a licensed underwriter makes the final decision."
    ),
)


class UnderwriteRequest(BaseModel):
    applicant_id: str


class FlagModel(BaseModel):
    code: str
    severity: str
    message: str


class UnderwriteResponse(BaseModel):
    applicant_id: str
    dti: float
    ltv: float
    credit_tier: str
    flags: list[FlagModel]
    decision: str
    rationale: str
    narration: str
    advisory: bool
    disclaimer: str


def _authorized(x_api_key: str | None) -> bool:
    return x_api_key is not None and secrets.compare_digest(x_api_key, _API_KEY)


@app.get("/health", include_in_schema=False)
def health() -> dict:
    """Liveness probe. No auth by design — load balancers need it unauthenticated."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    """Readiness probe. Confirms the applicant book is loaded."""
    return {"status": "ready", "applicants": len(APPLICANTS)}


@app.post("/underwrite", response_model=UnderwriteResponse)
def underwrite(
    req: UnderwriteRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> UnderwriteResponse:
    """Run the deterministic underwriting pipeline for one applicant."""
    if not _authorized(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or invalid API key",
        )
    applicant = APPLICANTS.get(req.applicant_id)
    if applicant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"unknown applicant: {req.applicant_id}",
        )
    a = agents.score(applicant)
    return UnderwriteResponse(
        applicant_id=a.applicant_id,
        dti=a.dti,
        ltv=a.ltv,
        credit_tier=a.credit_tier,
        flags=[FlagModel(code=f.code, severity=f.severity, message=f.message) for f in a.flags],
        decision=a.decision,
        rationale=a.rationale,
        narration=agents.narrate(a),
        advisory=True,
        disclaimer="Advisory output only — a licensed underwriter makes the final decision.",
    )
