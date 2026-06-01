# Stage 6 — LLM-as-judge quality gate (PWAF rubric)

Applied `../resources/rubric/pwaf-rubric.md` directly (interactive run). Gate = all ≥3,
dims **1/2/6 ≥4**. Formal MLflow `@scorer` wiring is project Step 4.

| # | Dimension | Score | Evidence | Fix applied |
|---|-----------|:----:|----------|-------------|
| 1 | Pattern grounding | **5** | HIGH-conf Built-On ISV, anchored to `built-on-multitenant.md`; both end-user-unaware + not-data-product signals cited (S0) | — (note: grounding is model-recall; real PWAF retrieval = Step 3) |
| 2 | Security & isolation | **4** | Per-brand SPN + UC RLS on `brand_id`; cross-tenant leakage suite (S4); least-priv token exchange; EU residency flagged; secrets rotation (S2/S3) | PII-in-assistant left as open D3, not resolved → held at 4 not 5 |
| 3 | Cost | **3** | Sizing tied to assumed scale; **per-tenant unit economics modeled** incl. the "floor dominates at 400 brands" insight; assumptions A6–A8 + LOW conf marked (S5) | Honest but soft — bounded by UNKNOWN scale; raising requires confirmed A6–A8 (irreducible until intake answered) |
| 4 | Reliability & ops | **4** | System tables + Lakehouse Monitoring + MLflow traces; isolation-breach alert test; SLA targets (S3/S4) | DR/availability target not deeply specified — acceptable for blueprint altitude |
| 5 | Architecture fit | **5** | Idiomatic component map; deviations D1/D2 justified; "don't rebuild Databricks UI" anti-pattern called out (S3/S5) | — |
| 6 | Whitespace honesty | **5** | 8 effort-tagged whitespace items, build/buy each; anti-pattern guardrail (S5) | — |
| 7 | Buildability | **4** | 4-phase roadmap w/ exit criteria; test plan mapped to S2 criteria; eval scorers + thresholds (0.85/0.90/1.0) defined (S4) | Eval thresholds are proposed, not yet calibrated on real data → 4 |
| 8 | Traceability | **4** | Assumptions A1–A9, decisions D1–D3, measurable success criteria; decision log assembled S7 | Some Stage-2 thresholds deferred to S4 ("X%") — traceable but forward-referenced |

## Gate result: **PASS**
All dimensions ≥ 3; non-negotiables 1/2/6 = 5/4/5 (≥4). No revision loop triggered.

## Residual risks / irreducible gaps (stated plainly)
- **Cost confidence is LOW** and cannot rise without confirmed scale (A6–A8) + a real
  `databricks-sizing` run. Treat all $ as planning placeholders.
- **D3 — PII in the assistant path is unresolved.** If EU brands' order data carries PII,
  B6 GA is blocked pending column masking / `ai_mask`. Security non-negotiable risk.
- **Grounding is model-recall, not retrieved PWAF.** Classification + component claims are
  not yet verified against the live PWAF corpus or `databricks-docs` (project Steps 3).
- **Specialists were simulated** (sizing, diagram, security-questionnaire) — a production
  run must actually invoke them; their absence is why dims 2/3/7 sit at 4/3/4 not 5.
