# Smoke-test seam report — Firefly run (2026-05-29)

Running purpose: find where stage boundaries bend BEFORE hardening. Specialists are
simulated with clearly-marked stubs. Findings are logged here as `[Sn-k]` (stage n,
finding k) and rolled up at the end.

## Rollup — prioritized fixes (read this first)

**Verdict: the workflow held end-to-end.** All 8 stages produced their artifact, the rubric
gate passed honestly, and the deliverable is coherent. The bends are real but small — mostly
contract/archetype gaps, not structural flaws. Priority order to harden:

| Pri | Seam | Fix | Cheap? |
|-----|------|-----|--------|
| ✅ **DONE** | [S0-1]/[S0-2] | Added `interactive` + `depth` to intake `options` + a "Non-interactive runs" section | applied 2026-05-29 |
| ✅ **DONE** | [S1-1] | Split archetype into "Canonical capabilities (Stage 1)" vs "Component map (Stage 3)"; rewired stage 01/03 wording | applied 2026-05-29 |
| ✅ **DONE** | [S1-2] | Added canonical **Observability & quality** + **Evaluation harness** blocks to the archetype (capabilities + component map) | applied 2026-05-29 |
| **P2** | [S3-1] | Scope the planned retrieval service (Step 3) to cover **product-capability** facts, not just PWAF patterns; or hard-require databricks-docs per non-obvious claim | design decision for Step 3 |
| **P2** | [S5-1] | Spec `sizing_adapter.py` (scale.*→sizing inputs) **and** a per-tenant unit-economics post-step as fat scripts | medium |
| **P3** | [S2-1] | Stage 2: for AI blocks, state the *metric*; defer the *threshold* to Stage 4 (make the forward-ref intentional) | trivial wording |
| **P3** | [S6-1] | Document that cost dim is structurally capped at 3 under UNKNOWN scale (irreducible-gap hatch works) | trivial |
| **P3** | [S7-1] | Future `assemble_blueprint.py` takes `--resources-dir`; document resources/ vs output/ roots | note for Step (scripts) |

Nothing here blocks proceeding to Step 2 (placement) — these are hardening items.

## Findings (chronological)

### [S0-1] No non-interactive / smoke mode — the blocking-question round halts autonomy
Stage 0 says "ask ONE batched question round" for blocking gaps. On Firefly, `data_residency`
(EU brands → GDPR?) and all of `scale.*` are UNKNOWN and arguably blocking (a cost number
gets requested in Stage 5). In an autonomous/batch run (and in the future App backend) there
is no human to answer. **The workflow assumes an interactive human.** Need an explicit
`interactive: true|false` intake flag: when false, infer-and-flag everything, never block.
Recorded the inferred answers in the assumptions block instead of asking.

### [S0-2] Intake `options` lacks a `run_mode`/`interactive` field
`resources/intake_schema.md` `options:` only has `partner_rec` and `render_html`. Add
`interactive` (and maybe `depth: quick|full`) so [S0-1] is expressible in the contract.

### [S1-1] Archetype's "canonical building blocks" is ALREADY a block→component map
`built-on-multitenant.md` presents blocks pre-bound to Databricks components (DBSQL, Genie,
Apps…). But Stage 1 explicitly wants product-AGNOSTIC capabilities; Stage 3 is where the
component map belongs. The archetype front-loads Stage 3 into Stage 1, so Stage 1 felt like
re-deriving the same table at a different altitude. **Fix:** split the archetype into a
`capabilities:` list (Stage 1) and a `component_map:` table (Stage 3), or have Stage 1
explicitly say "strip the component column."

### [S2-1] Measurable success criteria for AI blocks can't be set until Stage 4
Stage 2 wants measurable acceptance per block, but B6's correctness threshold genuinely
can't be named until the Stage-4 eval is designed — I had to write "≥ X% (set in S4)". The
stage ordering forces forward references for any GenAI block. **Fix:** Stage 2 should say
"for AI/agent blocks, state the *metric*; the *threshold* is set in Stage 4 eval design" so
the forward-reference is intentional, not a gap.

### [S3-1] Grounding gap applies to Stage 3 (component capability), not just Stage 0
Stage 3 maps blocks to products (Lakeflow Connect Postgres CDC, Genie respecting per-SPN RLS,
etc.) on **model recall**. Stage 3 instructions say "use databricks-docs to verify," but the
planned `pwaf_retrieve.py` RAG (Step 3) is scoped to PWAF pattern grounding only. **Fix:** the
retrieval service should also serve *product-capability* facts (or Stage 3 must hard-require a
databricks-docs check per non-obvious component claim). Otherwise architecture claims are unverified.

### [S5-1] No `scale.* → databricks-sizing` adapter, and per-tenant economics is post-processing
Two seams: (a) the intake `scale.*` shape and `databricks-sizing`'s expected inputs aren't
mapped — `sizing_adapter.py` (scripts/README) is still a TODO, so the seam is hand-waved;
(b) `databricks-sizing` produces aggregate spend, but Built-On's whole point is **per-tenant
unit economics** — the skill must post-process the sizing output (÷ active tenants, model the
fixed-floor effect). That post-processing logic lives nowhere yet. **Fix:** spec the adapter +
a per-tenant economics step as a fat script.

### [S6-1] Gate works, but cost dim is structurally capped by UNKNOWN scale
Dim 3 (cost) can't exceed 3 while scale is UNKNOWN — the rubric's "irreducible gap" escape
hatch saved the gate (good, it worked as designed). But it means an autonomous run will
*always* cap cost at 3 absent confirmed scale. Confirms [S0-1]: non-interactive runs need a
way to either solicit scale or accept a permanently-soft cost score. Not a bug, but document it.

### [S7-1] Relative-path ambiguity: resources/ vs blueprint-out/
Stage files reference `../DISCLAIMER.md` and `../rubric/...` (relative to `resources/stages/`).
The output artifacts live in `./blueprint-out/`. When `assemble_blueprint.py` stitches the
final doc it must resolve DISCLAIMER/template paths against the *skill resources* dir, not the
output dir. A naive relative include breaks. **Fix:** the (future) assemble script takes an
explicit `--resources-dir`; document the two roots.

### [S1-2] Archetype has no Observability or Eval building block
The GenAI assistant (Genie) needs an eval harness + answer-quality observability, but the
archetype's canonical blocks omit both — I had to invent B11 (observability) and B12 (eval).
For a Built-On product whose headline feature is conversational analytics, eval/observability
should be canonical, not improvised. **Fix:** add them to the archetype's block list.
