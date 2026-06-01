# Stage 6 — LLM-as-judge quality gate

Grade the assembled draft against the PWAF rubric BEFORE producing final output.

## Steps
1. Load `../rubric/pwaf-rubric.md`.
2. Score each rubric dimension (1–5) with a one-line justification + the artifact
   evidence. Use `agent-evaluation` / `databricks-mlflow-evaluation` to formalize
   this as scorers + a logged trace once the skill is productionized; for an
   interactive run, apply the rubric directly.
3. Any dimension < 3 ⇒ revise the offending stage artifact and re-score that
   dimension. Loop until all ≥ 3 or you've recorded why a gap is irreducible.
4. Record the final scorecard + what changed.

## Output → `06-judge-report.md`
- Rubric scorecard (dimension | score | evidence | fix applied).
- Residual risks / irreducible gaps, stated plainly.
