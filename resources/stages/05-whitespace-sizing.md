# Stage 5 — Whitespace map + best-effort sizing

## Whitespace (the most valuable, most honest section)
List everything the build team must own that Databricks does NOT provide:
customer-facing app shell & auth UX, tenant onboarding/billing/chargeback, domain
documentation, SPN/credential lifecycle automation, non-Databricks integrations,
support tooling. Pull seeds from the archetype's whitespace section and Stage 1 tags.
For each: why it's whitespace, rough effort (S/M/L), and a build-vs-buy note.

## Best-effort sizing
1. Invoke `databricks-sizing` with `scale.*` from intake.
2. If scale is UNKNOWN, state explicit assumptions, size against them, and mark
   **LOW confidence**. Never present an assumed number as firm.
3. Model **per-tenant unit economics** for multi-tenant, not just aggregate spend.
4. Produce a rough effort estimate (T-shirt size per phase + whitespace).

## Output → `05-whitespace-sizing.md`
- Whitespace table (item | why | effort | build/buy).
- Sizing summary with assumptions + per-claim confidence.
- Effort estimate per roadmap phase.
- Standing caveat (`../DISCLAIMER.md`).
