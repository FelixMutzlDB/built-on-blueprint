# scripts/ — fat deterministic helpers (thin-skill principle)

Per the thin-SKILL + fat-script principle, reusable deterministic work lives here so each
skill invocation stays cheap. These are the parts that move behind a shared service
(MCP / serving endpoint) so a Databricks App surface can reuse them — see `GROUNDING.md`.

All scripts are dependency-light and runnable standalone (`python <name>.py` runs a demo).

| Script | Purpose | Seam |
|--------|---------|------|
| `pwaf_retrieve.py` | Grounding retrieval over the PWAF corpus **and** Databricks product-capability facts (Vector Search, with a zero-infra local fallback). The future App/MCP backend. | S3-1 |
| `sizing_adapter.py` | Normalize intake `scale.*` → `databricks-sizing` inputs, infer-and-flag for non-interactive runs. | S5-1a |
| `tenant_economics.py` | Aggregate spend → per-tenant unit economics + fixed-floor amortization curve + break-even. | S5-1b |
| `judge_scorers.py` | PWAF rubric → MLflow GenAI `@scorer` functions (1–5 per dimension) + the pass/gate logic. | Stage 6 |
| `GROUNDING.md` | Design doc for the grounding service (two corpora, backends, build order). | S3-1 |

### Still TODO (pure file assembly, no LLM)
- `assemble_blueprint.py` — stitch stage artifacts (00–06) into `blueprint.md` from the
  template; build the decision log. Takes an explicit `--resources-dir` (seam S7-1: resolve
  DISCLAIMER/template paths against the skill resources dir, not the output dir).
- `render_html.py` — render `blueprint.html` (architecture + roadmap + scorecard).

### Corpus TODO
- `resources/product_facts/*.md` — the curated product-capability corpus `pwaf_retrieve.py`
  retrieves over. Start with the ~20 capability claims Stage 3 makes (see `GROUNDING.md`).
