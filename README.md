# Skunky Collect

Stateless normalization preview for extracted contact candidates. **No database writes or outbound outreach.**

`POST /v1/normalize` requires `X-Skunky-Token`, JSON `source_id`, `source_url`, `emails`, `phones`, optional ISO region and provenance.

Normalizes email casing, validates phone numbers into E.164, deduplicates within the request, and returns `consent_status=unverified`, `outreach_allowed=false`, `persisted=false`. These fields are explicit safety gates for downstream consumers, not evidence of contact consent.

Production ingestion/storage is deferred pending a lawful-basis model, retention/deletion, DNC suppression, encryption, tenant isolation and auditable provenance. Local: `pip install -r requirements.txt && SKUNKY_SERVICE_TOKEN=... uvicorn app:app --port 8000`.
