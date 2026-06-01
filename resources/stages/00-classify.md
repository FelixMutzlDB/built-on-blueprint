# Stage 0 — Classify the PWAF pattern

**Why first:** this fork changes isolation model, identity, distribution mechanism,
and cost shape downstream. Do NOT skip to decomposition.

## Steps
1. From the intake `pattern_signal`, decide the dominant PWAF partner type:
   - end users don't know Databricks → **Built-On ISV** (`built-on-multitenant.md`)
   - customers bring their own Databricks → **Connected ISV** (`connected-isv.md`)
   - the product is distributed data → **Data Collaboration** (`data-collaboration.md`)
2. If it blends two, name the blend and which dominates the architecture.
3. Load the chosen archetype file. Adopt its building blocks as the starting skeleton.
4. State the classification rationale and the 1–2 most important consequences
   (e.g. "Built-On ⇒ SSO-SPN, no end-user UC accounts").

## Output → `00-classification.md`
- Chosen pattern + confidence + rationale.
- Archetype anchor (which file).
- Filled intake (with `assumptions` block).
- The ONE batched clarifying question round, if any blocking gap remains.
