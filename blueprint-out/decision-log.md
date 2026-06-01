# Decision log — Firefly Built-On Blueprint

## Assumptions (inferred, not confirmed)
| # | Assumption | Stage | Impact if wrong | Confidence |
|---|-----------|-------|-----------------|------------|
| A1 | US + small EU footprint; EU residency is a Phase-2 concern | 0 | EU-now → residency/isolation rises to Phase 1 | M |
| A2 | SOC2 in scope; GDPR for EU brands; marketing data may carry PII | 0 | Stronger compliance → more isolation/masking | M |
| A3 | p95 dashboard <3s, Genie <8s at launch | 0 | Tighter SLA → bigger/always-on WH → cost | M |
| A4 | No hard budget ceiling; cost must be defensible per tenant | 0 | A ceiling forces earlier serverless tuning | L |
| A5 | AWS | 0 | Azure/GCP changes networking + some SKU names | L |
| A6 | 400 → 1,000 brands in 18mo | 0 | Higher growth → multi-WH routing sooner | L |
| A7 | ~3 TB gold, growing | 0 | 10×+ data shifts storage + WH sizing | L |
| A8 | ~50 peak concurrent marketers at launch | 0 | Higher concurrency → scaling/isolation cost | L |
| A9 | First tenant live < 1 quarter | 0 | Aggressive timeline trades hardening depth | L |

## Decisions & rejected alternatives
| # | Decision | Alternatives considered | Why chosen |
|---|----------|------------------------|------------|
| D1 | Shared gold + UC row-level security on `brand_id` | Per-brand catalogs/schemas | Object-count sanity at ≤1,000 brands; revisit per-catalog for hard-isolation brands |
| D2 | Keep Firefly's React shell, call Genie + Statement Execution APIs | Databricks Apps as the shell | Firefly has app-dev strength; Apps is the fallback if they don't want to host |
| D3 | **OPEN** — PII handling in the assistant path | mask at B3 vs exclude PII columns vs allow | Unresolved; blocks B6 GA if EU PII in scope |
| D4 | Per-brand Service Principal (SSO→SPN exchange) | End-user UC accounts; shared SPN | Archetype isolation model; audit traces to correct tenant; no end-user Databricks identity |
| D5 | Lakeflow Declarative Pipelines for medallion | Hand-rolled Spark jobs; keep cron | Declarative + serverless fits thin data-eng team |

## Open questions for the build team
| # | Question | Why it matters | Owner |
|---|----------|----------------|-------|
| Q1 | Any brand contractually EU-only **now**? | Forces EU-region workspace + residency boundary into Phase 1 | Firefly + Legal |
| Q2 | Confirm tenant trajectory, data volume, peak concurrency (A6–A8) | Raises cost confidence above LOW; sizes warehouses | Firefly |
| Q3 | Budget ceiling? | Determines serverless auto-stop aggressiveness | Firefly |
| Q4 | Is PII in order data in scope for the assistant? (D3) | Blocks B6 GA; decides masking strategy | Firefly + Security |
| Q5 | Build vs buy ad-platform connectors (Fivetran/Airbyte)? | B1 whitespace effort + cost | Firefly |
