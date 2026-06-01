# Stage 5 — Whitespace map + best-effort sizing

## Whitespace — what Firefly owns, NOT the platform
| Item | Why it's whitespace | Effort | Build / Buy |
|------|---------------------|--------|-------------|
| Customer-facing app shell, embedding, brand theming (B7) | Databricks gives data+APIs+Apps, not Firefly's product UX | M | Build (reuse existing React app) |
| Marketer auth UX + SSO→SPN exchange service (B8) | Platform gives the SPN/OAuth primitives; the broker is yours | M | Build |
| Tenant onboarding/provisioning automation (B9) | UC/SPN/grants are APIs; orchestrating "new brand in <1 day" is your glue | M–L | Build (SDK/Terraform) |
| Per-brand billing / chargeback logic (B10) | System tables give cost *data*; turning it into invoices/margin is product logic | M | Build |
| Ad-platform connectors — Meta/Google/TikTok (B1) | No native Databricks connector; you own extraction + rate-limit handling | M | Build or Buy (Fivetran/Airbyte) |
| Domain documentation in marketer vocabulary | Linking to Databricks docs breaks the abstraction (archetype anti-pattern) | S | Build |
| Eval dataset curation + SME labeling (B12) | Platform runs the eval; the golden Q/A set is your domain knowledge | M (ongoing) | Build |
| Customer support tooling for embedded analytics | Out of platform scope | S–M | Build/Buy |

**Anti-pattern guardrail (from archetype):** do **not** rebuild the Databricks UI inside
Firefly. Embed governed dashboards + Genie; expose marketer-friendly controls, not a SQL editor.

## Best-effort sizing
> **INVOKE `databricks-sizing` here** with `scale.*`. Scale is largely UNKNOWN (A6–A8) →
> sizing is **LOW confidence**, against explicit assumptions. *SIMULATED output:*

**Assumptions used:** 400→1,000 brands (A6); ~3 TB growing gold data (A7); ~50 peak concurrent
marketers, bursty (A8); p95 dashboard <3s, Genie <8s (A3); AWS serverless (A5).

| Cost driver | Sizing basis | Rough monthly (LOW conf) |
|-------------|--------------|--------------------------|
| DBSQL Serverless (B5 dashboards) | 1–2 small/medium serverless WH, auto-stop, ~50 concurrent bursty | **$$ — dominant** |
| Genie / model serving (B6) | per-query inference + WH for generated SQL | **$$** |
| Lakeflow pipelines (B1/B2) | serverless, incremental ≤1h freshness, ~3 TB | **$** |
| Storage + UC | ~3 TB gold + bronze/silver retention | **$ (small)** |
| Databricks Apps (if B7 hosted there) | 1 app compute | **$ (optional)** |

**Per-tenant unit economics (the number that matters):** total platform spend ÷ active brands.
At 400 brands the fixed serverless + pipeline floor dominates → **high cost-per-brand**; it
**falls sharply as brands grow toward 1,000** (shared warehouses/pipelines amortize). → Firefly's
pricing must clear the per-brand floor at *current* count, not the optimistic future one.
*Confidence: LOW — replace with `databricks-sizing` output once A6–A8 are confirmed.*

## Effort estimate per roadmap phase (T-shirt)
| Phase | Platform build | Whitespace in that phase | Combined |
|-------|----------------|--------------------------|----------|
| P0 skeleton | S | S | **S** |
| P1 single-tenant MVP | M | M (app embed start) | **M** |
| P2 multi-tenant hardening | M | L (onboarding automation, SSO→SPN) | **L** |
| P3 scale/GA | M | M (chargeback, eval gate, theming) | **M–L** |

## Standing caveat
See `../resources/DISCLAIMER.md` (appended verbatim in `blueprint.md`). Cost/sizing here is
LOW confidence against assumed scale — planning input, not a commitment.
