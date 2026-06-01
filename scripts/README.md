# scripts/ — fat deterministic helpers (thin-skill principle)

Per the thin-SKILL + fat-script principle, push reusable deterministic work here so
each invocation stays cheap. Candidates as the skill productionizes:

- `assemble_blueprint.py` — stitch stage artifacts (00–06) into `blueprint.md` from
  the template; build the decision log. Pure file assembly, no LLM.
- `render_html.py` — render `blueprint.html` (architecture + roadmap + scorecard).
- `sizing_adapter.py` — normalize intake `scale.*` → `databricks-sizing` inputs.
- `pwaf_retrieve.py` — retrieve the relevant PWAF section/archetype (later: RAG /
  Vector Search over the PWAF corpus) instead of relying on model recall.

These are the parts that should eventually move behind a shared service (MCP /
serving endpoint) so a Databricks App surface can reuse them. TODO: implement.
