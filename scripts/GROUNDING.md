# Grounding service — design (Step 3)

The biggest quality lever for Built-On Blueprint is replacing **model-recall** with
**retrieval**. The smoke test (seam **S3-1**) showed the gap is wider than first scoped:
not just PWAF *pattern* classification (Stage 0) but also Databricks *product-capability*
facts the architecture stage leans on (Stage 3 — Lakeflow Connect CDC, Genie-respects-RLS,
UC isolation semantics). Both are model-recall today; both must be grounded.

This service is also the **future App / MCP backend** (locked design decision: capability
core behind a stable interface → Claude Code skill → Databricks App). Build it once; let
every surface be a thin client.

## Two corpora, one interface

| Corpus | Source | Feeds |
|--------|--------|-------|
| **PWAF** | partner-architecture site, `resources/archetypes/`, deployment models | Stage 0 classify, Stage 1 decompose |
| **product-capability** | Databricks docs facts (curated), release notes, `resources/product_facts/` (TODO) | Stage 3 architecture, Stage 5 sizing |

Single stable entry point — `pwaf_retrieve.retrieve(query, corpus="all|pwaf|product", k)`.
Returns `Chunk{text, source, corpus, score, confidence}`. Stages cite `source`; the
decision log records every grounded claim with its `confidence`.

## Backends (graceful degradation)

1. **vector_search** — Databricks Vector Search over two UC indexes. Production path and
   App backend. Configured via `BLUEPRINT_VS_ENDPOINT` + `BLUEPRINT_VS_INDEX_{PWAF,PRODUCT}`.
2. **local** — zero-infra lexical fallback over bundled `resources/`. Runs today, low recall,
   results flagged `confidence="low"`. Lets the skill ground *something* before the index exists.

`select_backend()` auto-picks vector_search when configured, else local — never hard-fails the skill.

## Build order

1. **Curate the product-facts corpus** (`resources/product_facts/*.md`) — start with the
   ~20 capability claims Stage 3 actually makes (CDC, RLS, UC isolation, serverless, Apps auth).
   This alone lets the local backend ground Stage 3 today.
2. **Chunk + index** both corpora into Vector Search (use `databricks-vector-search` skill).
3. **Wire stages 0/1/3/5** to call `retrieve()` and cite sources instead of recalling.
4. **Expose** the same `retrieve()` behind the MCP server (`fe-mcp-servers`) and the App backend.

## Companion fat scripts

- `sizing_adapter.py` — intake `scale.*` → `databricks-sizing` inputs, with infer-and-flag (S5-1a).
- `tenant_economics.py` — aggregate spend → per-tenant unit economics + fixed-floor curve (S5-1b).
- `judge_scorers.py` — PWAF rubric → MLflow scorers + gate (Stage 6 / Step 4).

All are pure-Python, dependency-light, and runnable standalone (`python <script>.py` runs a demo).
