# Stage 0 — PWAF pattern classification

## Classification
**Pattern: Built-On ISV (multi-tenant analytics).** Confidence: **HIGH.**
Archetype anchor: `resources/archetypes/built-on-multitenant.md`.

### Rationale
- `users_know_databricks: false` — a brand marketer asks questions inside Firefly and
  must never see Databricks. This is the defining signal of Built-On ISV.
- `data_shared_externally: false` — Firefly is not distributing a data *product* to
  other orgs; each brand sees only its own embedded analytics. → **not** Data Collaboration.
- Customers do **not** bring their own Databricks workspace. → **not** Connected ISV.
- Firefly is simultaneously a data consumer (internal modeling) and a data provider
  (embedded analytics to brands) — textbook Built-On.

### Most important downstream consequences
1. **SSO-SPN identity model**: marketers authenticate via Firefly's own IdP; backend
   calls Databricks via a **per-brand Service Principal**. End users get **no** Databricks
   / Unity Catalog accounts. (Drives Stage 2 security + Stage 3 identity.)
2. **Semantic layer is mandatory, not optional**: the "ask your data" assistant (Genie)
   is only as good as the UC Metric Views beneath it. This is a hard prerequisite, not a
   nice-to-have. (Drives Stage 1 building blocks + Stage 4 sequencing.)

## Filled intake

```yaml
idea:
  one_liner: Embed per-brand marketing-analytics dashboards + a natural-language "ask your
    data" assistant inside Firefly's existing SaaS product.
  problem: Brand marketers cannot self-serve analytics; homegrown Postgres+cron ETL is
    buckling at ~400 brands; Firefly faces a year-long internal rebuild vs. building on a platform.
  source_materials: [text]
  existing_code: none (homegrown Postgres + cron ETL, to be replaced — not provided)

pattern_signal:
  end_users: brand marketers at mid-market e-commerce companies (Firefly's customers)
  users_know_databricks: false
  data_shared_externally: false

constraints:
  data_residency: UNKNOWN  # mostly US, a few EU brands → potential GDPR/EU-residency split (ASSUMPTION A1)
  compliance: UNKNOWN      # B2B SaaS → SOC2 assumed; marketing data may carry PII → GDPR for EU brands (A2)
  latency_sla: interactive # embedded dashboards + interactive Q&A → assume p95 < 3s dashboards, < 8s Genie (A3)
  budget_envelope: UNKNOWN # no ceiling stated (A4)
  cloud: UNKNOWN           # assume AWS — most common for mid-market SaaS (A5)

estate:
  incumbent_platform: homegrown Postgres + nightly cron ETL
  existing_databricks: none

scale:
  tenants: ~400 brands today; assume target 1,000 within 18mo (A6)
  data_volume: UNKNOWN     # assume low-single-digit TB of campaign/order events, growing (A7)
  concurrency: UNKNOWN     # assume ~50 peak concurrent marketers across brands at launch (A8)

team:
  in_house_skills: strong app dev (React/Node); thin data engineering; no ML
  timeline: UNKNOWN        # "avoid a year-long build" → target first tenant live < 1 quarter (A9)
  build_vs_buy: leaning build-on-platform

options:
  partner_rec: false
  render_html: false
  interactive: false       # SMOKE-TEST: no human to answer → infer-and-flag, do not block  (see seam [S0-2])
```

## Assumptions block
| # | Assumption | Why | Impact if wrong |
|---|-----------|-----|-----------------|
| A1 | US + small EU footprint; treat EU residency as a Phase-2 concern | "mostly US, a few EU" | If EU is material now, residency/isolation rises to Phase 1 |
| A2 | SOC2 in scope; GDPR for EU brands; marketing data may contain PII | B2B SaaS norm | Stronger compliance → more isolation/masking work |
| A3 | p95 dashboard < 3s; Genie answer < 8s at launch concurrency | "interactive", embedded | Tighter SLA → bigger/always-on warehouses → cost |
| A4 | No hard budget ceiling; cost must be *defensible per tenant* | none stated | A ceiling would force serverless/auto-stop tuning earlier |
| A5 | AWS | SaaS default | Azure/GCP changes networking + some SKU names only |
| A6 | 400 → 1,000 brands in 18mo | "buckling at ~400", growth implied | Higher growth → multi-warehouse routing sooner |
| A7 | Low-single-digit TB, growing | marketing/order events at mid-market scale | 10×+ data → storage + warehouse sizing shifts |
| A8 | ~50 peak concurrent marketers at launch | mid-market, embedded usage | Higher concurrency → warehouse scaling / per-tenant isolation cost |
| A9 | First tenant live < 1 quarter | "avoid year-long build" | Aggressive timeline trades off hardening depth |

## Batched clarifying question round (would-ask in an interactive run)
Because `interactive: false` for this smoke test, these are **recorded, not asked**:
1. EU data residency — is any brand contractually bound to EU-only processing **now**? (A1/A2)
2. Scale for sizing — confirm tenant count trajectory, rough data volume, and peak
   concurrent users. (A6/A7/A8 — drives Stage 5 cost confidence)
3. Is there a budget ceiling the design must respect? (A4)
