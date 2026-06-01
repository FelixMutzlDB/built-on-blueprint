# Stage 3 — Databricks solution architecture

## Building block → Databricks component
Default = archetype component map; deviations carry a stated reason.

| # | Block | Databricks component(s) | Rationale / deviation |
|---|-------|--------------------------|------------------------|
| B1 | Ingestion | **Lakeflow Connect** (Postgres CDC) + **Auto Loader** for ad-platform extracts landed to a volume; non-DB connectors pull into cloud storage first | Managed CDC avoids rebuilding cron; ad-platform APIs have no native connector → whitespace shim (S5) |
| B2 | Modeling | **Lakeflow Declarative Pipelines (SDP/DLT)**, medallion bronze→silver→gold | Declarative + serverless fits a thin data-eng team; idempotent/backfillable by design |
| B3 | Semantic layer | **Unity Catalog Metric Views** | Archetype hard-prereq; one definition feeds both B5 and B6 |
| B4 | Multi-tenancy | **UC row-level security** (filter on `brand_id`) + **per-brand Service Principal** | Archetype isolation model; no end-user UC accounts |
| B5 | Dashboards | **AI/BI Dashboards** embedded; served via **DBSQL Serverless Warehouse** | Serverless = fast start, auto-stop → cost control at variable concurrency |
| B6 | Assistant | **Genie** grounded on B3 Metric Views + a Knowledge Store | Quality ∝ semantic-layer quality; do not hand-roll a text-to-SQL |
| B7 | App shell | **Databricks Apps** OR Firefly's existing React app calling APIs | **Deviation:** Firefly already has a React/Node product → keep their shell, call Genie + Statement Execution APIs; use Databricks Apps only if they want to avoid hosting. (→ decision log) |
| B8 | Auth bridge | Firefly backend exchanges IdP token → **per-brand SPN** OAuth (M2M) | SSO-SPN pattern; browser never holds Databricks creds |
| B9 | Onboarding | Automation over **SDK/Terraform**: create SPN, grants, RLS binding, pipeline params | Whitespace automation built on platform APIs |
| B10 | Cost attribution | **System tables** (`system.billing.usage`) tagged by brand/SPN | Native; Firefly builds the chargeback view on top |
| B11 | Observability | **System tables** + **Lakehouse Monitoring** + **MLflow traces** (for B6) | One observability fabric across data + AI |
| B12 | Eval harness | **MLflow 3 GenAI evaluate** + scorers, dataset in UC | Composes `databricks-mlflow-evaluation`; gates B6 |

## Cross-cutting decisions (resolved once)
- **Identity:** Firefly IdP (e.g. Auth0) authenticates marketers. Firefly backend holds the
  tenant↔brand↔SPN map and performs OAuth M2M token exchange to the **per-brand SPN**. End
  users have **no** Databricks identity. *(Consequence of Stage 0 classification.)*
- **Governance:** single UC metastore; one catalog, per-brand schemas **or** shared gold +
  RLS on `brand_id`. **Recommend shared-gold + RLS** at ≤1,000 brands (fewer objects to manage);
  revisit per-catalog isolation if a brand demands hard physical separation (→ decision log).
- **Networking:** browser → Firefly backend → Databricks APIs over private connectivity; no
  direct browser→Databricks path; egress controls on B1 connectors.
- **Secrets:** ad-platform/Postgres creds + SPN secrets in UC-backed secret scopes; rotation ≤90d.
- **Observability:** system tables for SLA/cost/audit; MLflow traces for every Genie answer (feeds B12).

## Data flow (end-to-end)
```
Ad platforms ─┐
Firefly app DB ┼─(B1 Lakeflow Connect/Auto Loader)→ Bronze
               ┘
Bronze ─(B2 SDP medallion)→ Silver → Gold marts
Gold ─(B3 UC Metric Views)→ governed metrics
                              │
Marketer ─SSO→ Firefly backend ─OAuth M2M→ per-brand SPN
                              │                       │
                              ├─(B5)→ DBSQL Serverless → AI/BI embedded dashboard
                              └─(B6)→ Genie (RLS-scoped to brand) → answer+viz
All queries → system tables/MLflow (B10 cost, B11 obs, B12 eval)
```

## SIMULATED — `fe-architecture-diagram` invocation (stub)
> **INVOKE `fe-architecture-diagram` here** with the component map + data flow above to render
> the deliverable diagram. Placeholder: `./blueprint-out/diagram.drawio` (NOT generated in
> smoke test). The ASCII above is scaffolding for the diagram, not the deliverable.

## Open architectural questions / rejected alternatives (→ decision log)
- **D1** Per-brand schema vs shared-gold+RLS. *Chose* shared+RLS for object-count sanity at
  scale; *rejected* per-brand catalogs as default (revisit for hard-isolation brands).
- **D2** Firefly React shell vs Databricks Apps for B7. *Leaning* keep Firefly's shell
  (they have app-dev strength); Databricks Apps is the fallback if they don't want to host.
- **D3** PII masking in the assistant path — open (from Stage 2 security stub). Blocks B6 GA if EU PII in scope.
