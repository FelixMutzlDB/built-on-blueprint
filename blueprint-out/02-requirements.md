# Stage 2 — Requirements & success criteria

Per building block: functional | non-functional | security | measurable success criteria | confidence.
Security column anchored to the archetype isolation model (per-brand SPN + UC row filtering).
Security analysis would invoke **`security-questionnaire`** — *SIMULATED stub* below (marked).

| # | Block | Functional reqs | Non-functional reqs | Security & isolation | Success criteria (measurable) | Conf |
|---|-------|-----------------|---------------------|----------------------|-------------------------------|------|
| B1 | Ingestion | Land Postgres CDC + ad-platform data per brand, incrementally | Freshness ≤ 1h (down from nightly); resilient to ad-API rate limits | Source creds in secret scope; per-brand landing path | New brand data appears ≤1h; zero cross-brand bleed in bronze | M |
| B2 | Modeling | Conform to gold marts (campaigns/orders/attribution) | Idempotent, backfillable; ≤ 30min full refresh per brand | Pipeline runs under platform SPN, not human creds | Gold marts pass DQ checks; reproducible | M |
| B3 | Semantic layer | Define ROAS, repeat-purchase rate, CAC, AOV as governed metrics | Single source of truth; versioned | Metric defs in UC, grant-controlled | 100% of dashboard + assistant numbers resolve to a metric def (no ad-hoc SQL) | H |
| B4 | Multi-tenancy | Map marketer→brand; enforce brand-scoped reads | Scales to 1,000 brands without per-brand infra sprawl | **UC row-level filter on brand_id; per-brand SPN**; no end-user UC accounts | Automated cross-tenant leakage test = 0 leaks across all brands | H |
| B5 | Dashboards | Embedded per-brand dashboards over governed metrics | **p95 load < 3s** at launch concurrency (A3) | Dashboard query carries brand scope via SPN | p95 < 3s @ ~50 concurrent; correct brand data 100% | M |
| B6 | Assistant | NL question → governed answer + viz over the brand's data | **p95 answer < 8s** (A3); graceful "I don't know" | Genie restricted to that brand's scoped metrics/tables only | ≥ X% answer correctness on eval set (set in S4); 0 cross-brand answers | M |
| B7 | App shell | Embed B5/B6 in Firefly React app; brand theming | Matches Firefly UX; no "Databricks UI" leakage | Session token never exposes Databricks identity to browser | Marketers never see a Databricks artifact; usability test pass | M |
| B8 | Auth bridge | Exchange marketer SSO session → per-brand SPN call | Token exchange adds < 200ms; cached | **Least-privilege SPN per brand; short-lived creds; rotation** | Pen-test: a brand-A session cannot obtain brand-B scope | H |
| B9 | Onboarding | Provision SPN + scope + marts + defaults for a new brand | New brand live in < 1 day, mostly automated | New SPN scoped to only its brand by construction | New-brand provisioning has 0 manual UC steps after Phase 2 | L |
| B10 | Cost attribution | Attribute spend per brand from system billing tables | Daily refresh | Cost view readable only by Firefly platform admins | Per-brand cost reconciles to total platform spend ± 5% | M |
| B11 | Observability | Pipeline health, query SLA, assistant quality, isolation audit | Alert within 5min of SLA/isolation breach | Audit trail attributes every query to a brand SPN | SLA + isolation dashboards live; alerts fire in test | M |
| B12 | Eval harness | Score assistant answers vs golden set; gate releases | Runs in CI + sampled in prod | Eval data carries no cross-brand PII leakage | Release blocked if correctness < threshold (S4) | M |

## SIMULATED — `security-questionnaire` invocation (stub)
> **INVOKE `security-questionnaire` here** to formalize multi-tenant isolation, secrets,
> network, and compliance posture. Representative output Firefly would get back:
- **Isolation:** per-brand SPN + UC row-level security on `brand_id` is the primary control;
  defense-in-depth = separate catalogs/schemas per brand tier if regulatory pressure rises.
- **Secrets:** ad-platform + Postgres creds in Databricks secret scopes; SPN secrets rotated ≤ 90d.
- **Network:** front-end never talks to Databricks directly; all calls broker through Firefly
  backend → Statement Execution / Genie API over private networking; egress controls on B1 connectors.
- **Compliance:** SOC2 control mapping; for EU brands, evaluate EU-region workspace +
  data-residency boundary before onboarding any EU brand (ties to A1/A2).
- **Open security question:** is PII (customer emails in order data) in scope for the assistant?
  If yes → `ai_mask` / column masking before B3. (→ decision log)

## Notes
- Dimensions 2 (security) & 1 (pattern) are rubric non-negotiables (≥4) — B4/B8 success
  criteria are written as *tests* (leakage = 0) precisely so Stage 4 can verify them.
- Several "X%" / threshold cells are intentionally deferred to Stage 4 eval design (B6/B12).
