# Stage 1 — Functional building blocks

Starting skeleton = archetype canonical blocks (`built-on-multitenant.md`), adapted to
Firefly. Each block is a *capability*, not yet a Databricks product (that's Stage 3).
Tag = provisional in-platform vs whitespace.

| # | Building block (capability) | Purpose | Inputs | Outputs | Depends on | Tag |
|---|------------------------------|---------|--------|---------|-----------|-----|
| B1 | **Tenant data ingestion** | Land each brand's campaign + order/event data from Firefly's app DB and ad platforms | Postgres CDC, ad-platform APIs (Meta/Google/TikTok), Firefly event stream | Raw per-brand bronze tables | — | in-platform (ingest connectors partly whitespace) |
| B2 | **Modeling / medallion transform** | Clean + conform raw into per-brand silver/gold marts | B1 bronze | Conformed gold marts (campaigns, orders, attribution) | B1 | in-platform |
| B3 | **Semantic layer** | Define governed business metrics (ROAS, repeat-purchase rate, CAC) once | B2 gold | Metric definitions usable by dashboards + assistant | B2 | in-platform (**hard prereq** for B6) |
| B4 | **Multi-tenancy & isolation** | Guarantee brand A never sees brand B; map marketer→brand→backend identity | Firefly IdP, tenant↔brand map | Per-brand scoped data access | B2 | in-platform (lifecycle automation = whitespace) |
| B5 | **Embedded dashboards** | Render per-brand analytics inside the Firefly product | B3 metrics, B4 scope | Embedded dashboard surface | B3, B4 | in-platform (embed/app shell = whitespace) |
| B6 | **Conversational "ask your data"** | NL → governed answer over the brand's data | B3 metrics, B4 scope, NL query | Answer + supporting viz/table | B3, B4 | in-platform |
| B7 | **App shell & embedding UX** | Host dashboards/assistant inside Firefly's React app; brand theming | B5, B6 | Customer-facing UI | B5, B6 | **mostly whitespace** (Firefly owns product UX) |
| B8 | **Auth bridge (SSO→SPN)** | Translate marketer SSO session → per-brand Service Principal backend calls | Firefly IdP token, tenant map | Scoped Databricks calls | B4 | in-platform pattern, **automation = whitespace** |
| B9 | **Tenant onboarding & lifecycle** | Provision a new brand: SPN, scope, marts, defaults | new-brand signal | Ready tenant | B4, B8 | **whitespace** |
| B10 | **Per-tenant cost attribution** | Attribute platform spend to each brand for margin/chargeback | system billing tables, tenant tags | Per-tenant cost view | B4 | in-platform (chargeback logic = whitespace) |
| B11 | **Observability & quality** | Pipeline health, query SLA, assistant answer quality, isolation audit | system tables, MLflow traces, app logs | Dashboards + alerts + eval scores | B2–B6 | in-platform |
| B12 | **Assistant evaluation harness** | Measure/guard answer quality of B6 before + during prod | B6 traces, eval dataset | Scores vs thresholds | B6 | in-platform (dataset curation = shared) |

## Dependency order (build-enabling sequence)
```
B1 → B2 → B3 ─┬─→ B5 ─┐
              └─→ B6 ──┴─→ B7 (app shell)
B2 → B4 → B8 → B9            (tenancy/identity/onboarding rail, parallel to B3)
B4 → B10                     (cost attribution)
B2..B6 → B11                 (observability spans everything)
B6 → B12                     (eval gates the assistant)
```
Critical path to a usable embedded experience: **B1→B2→B3→{B5,B6}→B7**, with the
**B4→B8** identity rail as a hard gate before any tenant goes live.

## Provisional whitespace seeds (→ Stage 5)
- B7 app shell / embedding UX / brand theming (Firefly owns)
- B8 SSO→SPN automation, credential rotation
- B9 tenant onboarding/provisioning automation
- B10 chargeback/billing logic (Databricks gives the cost data, not the billing product)
- B1 non-Databricks ad-platform connectors (Meta/Google/TikTok ingestion)
