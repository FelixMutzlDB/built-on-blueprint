# Stage 2 — (Non-)functional requirements + success criteria

For each building block from Stage 1, attach requirements and measurable success criteria.

## Steps
1. **Functional reqs** — what the block must do (testable statements).
2. **Non-functional reqs** — performance/latency, scale, availability/SLA,
   security & isolation, governance/compliance, cost ceiling, observability.
3. **Security** — invoke `security-questionnaire` for the security & compliance
   requirements; anchor multi-tenant isolation to the archetype's isolation model.
4. **Success criteria** — measurable acceptance per block (e.g. "p95 dashboard load
   < 3s at 200 concurrent tenants"). These become Stage 4 tests and Stage 6 rubric inputs.

## Output → `02-requirements.md`
Table per block: functional | non-functional | security | success criteria | confidence.
