# Archetype library

After Stage 0 classification, anchor the design to one (or a blend) of these
reference archetypes instead of designing from a blank page. Each archetype file
carries: canonical building blocks, default Databricks component map, isolation
model, known tradeoffs, and the security/cost shape.

| Archetype | When it fits | File |
|-----------|--------------|------|
| Built-On, multi-tenant analytics | End users do NOT know they're on Databricks; you embed analytics into your product | `built-on-multitenant.md` |
| Connected ISV | Customers knowingly connect their own Databricks; you integrate to the lakehouse | `connected-isv.md` *(stub)* |
| Data collaboration / monetization | You productize & distribute data via Delta Sharing / Marketplace | `data-collaboration.md` *(stub)* |

These map directly to the three PWAF partner types
(Built-On ISV / Connected ISV / Data Collaboration). A product can blend two —
note the blend and which dominates the architecture.

TODO: add archetypes for (a) GenAI/agent product on Databricks, (b) embedded ML
scoring service, as the pattern catalog matures.
