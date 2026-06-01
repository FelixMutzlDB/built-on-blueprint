# CLAUDE.md — developing the Built-On Blueprint skill

> This file orients anyone (you, a teammate, a fresh Claude session) **developing**
> this repo. It is NOT the runtime skill — that's `SKILL.md`. Keep the split:
> `SKILL.md` = how to *run* Blueprint (the product); this file = how to *build* it.

## What this is

**Built-On Blueprint** is an AI-first Claude Code skill that turns a fuzzy product
idea / rough spec / existing repo into a high-quality, **PWAF-grounded implementation
blueprint** for building *on* Databricks. It **routes, composes, and critiques** the
specialist Databricks skills we already have — it does not reinvent them.

8-stage workflow (0→7): classify PWAF pattern · decompose into building blocks ·
(non-)functional requirements + success criteria · Databricks architecture + diagram ·
roadmap + QA/tests/evals · whitespace map + best-effort sizing · LLM-as-judge quality
gate · assemble docs.

## Core principles (do not violate)

1. **Compose, don't duplicate.** Sizing → `databricks-sizing`. Diagrams →
   `fe-architecture-diagram`. Security → `security-questionnaire`. Judge →
   `agent-evaluation` + `databricks-mlflow-evaluation`. Docs → `databricks-docs`.
   If you find yourself re-implementing a specialist skill, stop.
2. **Thin SKILL.md + fat resources/scripts.** `SKILL.md` is the map. Stage logic lives
   in `resources/stages/`, loaded only when that stage runs (progressive disclosure).
   Reusable deterministic work goes in `scripts/` so each invocation stays cheap.
3. **Stage-separated, resumable artifacts.** Each stage writes its own
   `blueprint-out/NN-name.md`. A re-run reads existing artifacts and continues.
4. **Infer, then ask only blocking questions.** Non-interactive runs infer-and-flag
   everything (never block) and record inferences in the assumptions block.
5. **Honesty is the product.** Per-claim confidence + the whitespace map + the
   assumptions block + the standing `resources/DISCLAIMER.md` are the caveat mechanism.

## Locked decisions (2026-05-29)

- **Name:** Built-On Blueprint (working name "Blueprint"; renamed from "PWAF Design Agent").
- **Audience:** both internal + external — **internal first**.
- **Partner recommendation:** pluggable and **OFF by default** (fairness / liability).
- **Deployment is layered:** capability core (sizing, PWAF+product grounding, archetypes,
  partner-rec) behind a stable interface (MCP / serving endpoint) → Surface 1 = Claude Code
  skill (ship first, internal, via go/vibe) → Surface 2 = Databricks App (external, later).
  Build Step 3's grounding as a standalone service so all surfaces are thin clients over it.

## Repo layout

| Path | Role |
|------|------|
| `SKILL.md` | Thin runtime orchestrator (the product). |
| `resources/stages/` | Per-stage prompts/checklists. Loaded on demand. |
| `resources/archetypes/` | PWAF archetypes. `built-on-multitenant` fleshed; `connected-isv` + `data-collaboration` are STUBS. |
| `resources/rubric/pwaf-rubric.md` | 8-dim PWAF quality rubric (→ becomes MLflow scorers, Step 4). |
| `resources/intake_schema.md` | Normalized intake contract. |
| `resources/output_templates/` | Spec + decision-log templates. |
| `scripts/` | Fat deterministic helpers. **Currently README-only — all scripts are TODO.** |
| `blueprint-out/` | **DISPOSABLE run output.** Do NOT park dev notes here. |

## Status

- **2026-05-29** — scaffold complete (~20 files). End-to-end **smoke test passed** on the
  Firefly multi-tenant case: all 8 stages produced artifacts; PWAF rubric gate scored
  honestly (5/4/5 on non-negotiable dims 1/2/6). 8 seams logged in
  `blueprint-out/_seam-report.md`; 3 P1 fixes applied. Workflow held — bends were
  contract/archetype gaps, not structural.
- **Not yet:** not packaged as a plugin (no `.claude-plugin/`); fat scripts unimplemented;
  grounding is model-recall only; judge is described, not wired.

## What's next (read `blueprint-out/_seam-report.md` first)

2. **Placement** — `/dupe-check`, then decide plugin home (own plugin vs `fe-workflows`;
   *not* strategist-toolbox). Scaffold `plugin.json` once decided.
3. **Wire real grounding** — RAG / Vector Search over the PWAF corpus **and**
   Databricks product-capability facts (finding **S3-1**: the gap is wider than first
   scoped — Stage-3 product claims are model-recall too). This is also the future App
   backend. Spec `pwaf_retrieve.py` + `sizing_adapter.py` + a per-tenant economics
   post-step (seam **S5-1**) as fat scripts.
4. **Wire the judge** — `resources/rubric/pwaf-rubric.md` → MLflow `@scorer` functions +
   a seed eval dataset (compose `agent-evaluation` / `databricks-mlflow-evaluation`).

Remaining P2/P3 hardening seams (S2-1, S5-1, S6-1, S7-1) live in `_seam-report.md` — fold
them in opportunistically, not as a separate pass.

## Pointers

- Concept + evolving take + status: Obsidian wiki `entities/concepts/Built-On Blueprint.md`.
  When you hit a milestone, offer to `/wiki-note` it back there.
- Grounding sources: PWAF — https://databrickslabs.github.io/partner-architecture/ ·
  Advancing Analytics "Built on Databricks: delivering multi-tenant analytics".
- Origin: `EMEA Built-On SME Group Work` (28.05.2026).
