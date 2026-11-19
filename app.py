"""Deterministic privacy-aware contact normalization preview; no persistence."""
from __future__ import annotations

import hmac
import os
import re

import phonenumbers
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Skunky Collect", version="0.1.0")
EMAIL = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.I)


def authorize(token: str | None = Header(default=None, alias="X-Skunky-Token")):
    expected = os.environ.get("SKUNKY_SERVICE_TOKEN", "")
    if not expected or token is None or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Service authentication required")


class NormalizeRequest(BaseModel):
    source_id: str = Field(min_length=1, max_length=100)
    source_url: HttpUrl
    emails: list[str] = Field(default_factory=list, max_length=25)
    phones: list[str] = Field(default_factory=list, max_length=25)
    region: str = Field(default="ZA", pattern=r"^[A-Z]{2}$")
    provenance: str = Field(default="caller-supplied-html", max_length=60)


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "collect"}


@app.post("/v1/normalize", dependencies=[Depends(authorize)])
def normalize(body: NormalizeRequest):
    emails = sorted({
        e.strip().lower() for e in body.emails
        if len(e.strip()) <= 254 and EMAIL.fullmatch(e.strip())
    })
    phones = set()
    for raw in body.phones:
        if len(raw) > 40:
            continue
        try:
            number = phonenumbers.parse(raw, body.region)
            if phonenumbers.is_valid_number(number):
                phones.add(phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164))
        except phonenumbers.NumberParseException:
            continue

    return {
        "source_id": body.source_id,
        "source_url": str(body.source_url),
        "emails": emails,
        "phones": sorted(phones),
        "provenance": body.provenance,
        "consent_status": "unverified",
        "outreach_allowed": False,
        "persisted": False,
        "deduplication": "within-request",
    }
