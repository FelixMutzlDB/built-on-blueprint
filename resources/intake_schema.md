# Intake contract

Normalize ANY input into this structure. Fill from what's provided; mark unknowns as
`UNKNOWN`. After filling, list everything you inferred under `assumptions`. Only the
fields marked **(blocking)** should ever trigger a question — and only if still UNKNOWN
after a genuine attempt to infer.

```yaml
idea:
  one_liner:            # what is being built, in one sentence
  problem:             # the user/business problem
  source_materials:    # [text | repo_url | spec | blog | prd | diagram] provided
  existing_code:       # repo URL/path if any; else none

pattern_signal:        # feeds Stage 0 classification
  end_users:           # who consumes the product
  users_know_databricks: true|false|UNKNOWN   # do end users knowingly use Databricks?
  data_shared_externally: true|false|UNKNOWN  # is data productized/distributed to others?

constraints:
  data_residency:      # e.g. EU / sovereign cloud / specific region  (blocking if regulated)
  compliance:          # [GDPR, DORA, HIPAA, SOC2, ...] 
  latency_sla:         # interactive / batch / streaming / UNKNOWN
  budget_envelope:     # rough $/month ceiling if any
  cloud:               # AWS | Azure | GCP | UNKNOWN

estate:
  incumbent_platform:  # current data platform / what's being replaced
  existing_databricks: # none | some workspaces | heavy
  
scale:                 # feeds sizing (Stage 5). UNKNOWN is fine — assume + flag.
  tenants:             # # of customers/orgs (multi-tenant)
  data_volume:         # rough GB/TB
  concurrency:         # peak concurrent users/queries

team:
  in_house_skills:     # data eng / ML / app dev present?  (feeds whitespace + partner-rec)
  timeline:            # target GA / milestones
  build_vs_buy:        # appetite

options:
  partner_rec: false   # OFF by default — only true if user explicitly opts in
  render_html: false   # optional HTML visualization of the blueprint
  interactive: true     # true = may ask ONE blocking-question round; false = infer-and-flag, NEVER block
  depth: full          # full | quick — quick skips optional rendering & trims per-block detail
```

## Blocking-gap rule
Ask ONE batched question round only for fields that (a) are still UNKNOWN and
(b) change the design materially — most commonly: `users_know_databricks`,
`data_residency` (if regulated), and `scale.*` (if a cost number is requested).
Everything else: assume sensibly, record in `assumptions`, move on.

## Non-interactive runs (`interactive: false`)
Autonomous, batch, or **App-backend** invocations have no human to answer. When
`interactive: false`: do NOT ask anything — infer every blocking field, record each
inference in the `assumptions` block (with impact-if-wrong + confidence), and continue.
Surface the would-have-asked questions under "Open questions for the build team" in the
decision log instead. A cost score that depends on UNKNOWN `scale.*` stays LOW-confidence
and the Stage-6 cost dimension may be capped — record that as an irreducible gap, not a failure.
