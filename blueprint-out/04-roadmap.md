# Stage 4 — Implementation roadmap, QA & evals

## Phased roadmap
| Phase | Scope (blocks landed) | Exit criteria | Depends on |
|-------|------------------------|---------------|-----------|
| **P0 · Walking skeleton** | B1(one source)→B2(one mart)→B3(one metric)→B5(one dashboard) for **one pilot brand**, hard-coded scope | A real ROAS number renders in a dashboard from gold via a metric view | — |
| **P1 · Single-tenant MVP** | Full B1–B3 marts; B5 dashboards; B6 Genie on the pilot brand; B11 basic obs | Pilot brand self-serves dashboards + asks 10 canonical questions correctly | P0 |
| **P2 · Multi-tenant hardening** | B4 RLS + B8 per-brand SPN + B9 onboarding automation; isolation tests | **0 cross-tenant leaks** across ≥3 brands; new brand provisioned with 0 manual UC steps | P1 |
| **P3 · Scale / GA** | B7 embed in Firefly product; B10 cost attribution; B12 eval gate in CI; SLA tuning | p95 dashboard <3s & Genie <8s at target concurrency; eval gate enforced; cost-per-brand reported | P2 |

Critical gate: **no brand goes live before P2 isolation tests pass.**

## Test plan (derived from Stage 2 success criteria)
| Test | Type | Verifies (block / criterion) |
|------|------|------------------------------|
| Gold-mart DQ checks | unit/data | B2 reproducible, DQ pass |
| Metric resolution check | integration | B3 — every dashboard/assistant number maps to a metric def |
| **Cross-tenant leakage suite** | **isolation/security** | B4/B8 — brand-A SPN cannot read brand-B rows; run across ALL brands in CI |
| Token-exchange scope test | security | B8 — brand-A session cannot mint brand-B scope (pen-test style) |
| Dashboard load perf | performance | B5 — p95 <3s @ ~50 concurrent |
| Assistant latency | performance | B6 — p95 <8s |
| Onboarding dry-run | integration | B9 — new brand live, 0 manual UC steps |
| Cost reconciliation | data | B10 — per-brand cost = total ±5% |
| Isolation-breach alert | ops | B11 — alert fires within 5min in fault injection |

## Eval plan for AI components (B6 assistant) — composes `agent-evaluation` + `databricks-mlflow-evaluation`
> **INVOKE `agent-evaluation` / `databricks-mlflow-evaluation` here** to stand up the harness.
> *SIMULATED design* (real wiring is Step 4 of the project):

- **Eval dataset shape:** ~50–100 golden Q→A pairs per brand archetype (e-commerce verticals),
  each with: question, expected metric(s) invoked, gold answer, brand scope. Seed from the 10
  canonical P1 questions, expand with SME review.
- **Scorers:**
  - `Correctness` — answer matches gold (Guidelines/Correctness judge).
  - `RetrievalGroundedness` — answer grounded only in the brand's scoped metrics/tables.
  - **Custom `@scorer` `no_cross_tenant`** — answer contains zero data outside brand scope (hard fail = security, not just quality).
  - `Safety` — no PII leakage in answer.
  - Latency scorer — p95 < 8s.
- **Acceptance thresholds (release gate):** Correctness ≥ 0.85; Groundedness ≥ 0.90;
  `no_cross_tenant` = 1.0 (zero tolerance); Safety pass. **Below threshold ⇒ release blocked.**
- **Where it runs:** CI on every prompt/metric change + sampled continuously in prod via MLflow traces (B11/B12).

## Note
The eval thresholds here (0.85 / 0.90 / 1.0) are *proposed*; they become the seed values for
the formal MLflow scorers + seed eval dataset in project Step 4 and tie back to the rubric (S6).
