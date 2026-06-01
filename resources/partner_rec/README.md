# Partner recommendation — PLUGGABLE, OFF BY DEFAULT

**Do not run unless `options.partner_rec: true` AND the user explicitly opted in.**

## Why gated
Steering business to named partners carries fairness and liability exposure. This
module is decoupled so it can be disabled or removed via a single flag without
touching the core spec-generation loop.

## Rules when enabled
1. **Transparent, stated criteria** — match on capability/region/specialization/
   archetype fit. Print the criteria used.
2. **Never a ranked endorsement** — present a shortlist as *candidates to evaluate*,
   not "the best partner."
3. **No warranty** — explicitly state Databricks does not guarantee partner outcomes;
   the customer runs their own due diligence.
4. Prefer pulling partner data from an authoritative source (PWAF partner directory /
   internal partner catalog) over model recall. TODO: wire the data source.

## Output (appended as spec section 10)
- Selection criteria used.
- Candidate shortlist (capabilities, region, relevant archetype experience).
- Explicit "evaluate independently — no warranty" note.

TODO: decide data source + whether this ships internal-only initially.
