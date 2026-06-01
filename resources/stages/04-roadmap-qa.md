# Stage 4 — Implementation roadmap + QA / tests / evals

## Steps
1. **Roadmap** — sequence the build into phases (e.g. Walking skeleton → Single-tenant
   MVP → Multi-tenant hardening → Scale/GA). Each phase: scope, exit criteria,
   dependencies, the building blocks it lands.
2. **QA & tests** — derive test cases from Stage 2 success criteria: unit, integration,
   isolation/security tests (cross-tenant leakage!), performance tests at target scale.
3. **Evals** — for any GenAI/Genie/agent block, define an evaluation harness with
   `agent-evaluation` + `databricks-mlflow-evaluation`: scorers, eval dataset shape,
   acceptance thresholds. These ship to the build team as their acceptance gate.

## Output → `04-roadmap.md`
- Phased roadmap table.
- Test plan mapped to success criteria.
- Eval plan (scorers + thresholds) for AI components.
