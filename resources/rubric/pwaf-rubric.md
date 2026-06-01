# PWAF quality rubric (LLM-as-judge)

Score each dimension 1–5 with evidence. < 3 ⇒ revise & re-score. This rubric also
ships to the build team as their acceptance criteria.

| # | Dimension | What "5" looks like |
|---|-----------|--------------------|
| 1 | **Pattern grounding** | Correct PWAF classification; design anchored to a real archetype, not invented |
| 2 | **Security & isolation** | Multi-tenant isolation explicit; least-privilege; cross-tenant leakage addressed; compliance/residency honored |
| 3 | **Cost** | Sizing tied to stated scale; per-tenant unit economics; assumptions + confidence marked |
| 4 | **Reliability & operations** | SLA/availability, observability (system tables/MLflow), failure modes covered |
| 5 | **Architecture fit** | Components used idiomatically; deviations justified; no "rebuild the Databricks UI" anti-pattern |
| 6 | **Whitespace honesty** | What Databricks does NOT cover is explicit and effort-tagged; no overclaiming |
| 7 | **Buildability** | Roadmap is sequenced & testable; success criteria measurable; evals defined for AI parts |
| 8 | **Traceability** | Every claim traces to an input or a recorded assumption; decision log present |

## Scoring output
```
dimension | score (1-5) | evidence | fix applied
```
Overall gate: all dimensions ≥ 3, dimensions 1/2/6 ≥ 4 (these are non-negotiable for a
PWAF-grade spec). Record any irreducible gap explicitly.

## Wired (Step 4)
This rubric is formalized as runnable MLflow GenAI scorers + gate in
`scripts/judge_scorers.py` (`RUBRIC` is the single source of truth; the table above and the
code must stay in sync). Seed eval dataset: `resources/rubric/eval_dataset.jsonl` (the
passing Firefly reference run + two should-fail cases: rebuild-UI anti-pattern, overclaim/
no-whitespace). Run via `mlflow.genai.evaluate(data=..., scorers=pwaf_scorers())` then
`apply_gate(...)`. Composes the agent-evaluation / databricks-mlflow-evaluation skills.
