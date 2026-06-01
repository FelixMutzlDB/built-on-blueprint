# Stage 1 — Decompose into functional building blocks

## Steps
1. Start from the archetype's **"Canonical capabilities (Stage 1)"** list — capabilities
   only, NOT the component map. Add/remove for this idea. (The component map is Stage 3.)
2. Express each block as a capability ("ingest tenant events", "serve embedded
   dashboard", "conversational Q&A"), not yet a Databricks product.
3. Draw the dependency order between blocks (what must exist before what).
4. Flag blocks that are clearly outside Databricks (seed for Stage 5 whitespace).

## Output → `01-building-blocks.md`
- Numbered building blocks, each with: purpose, inputs, outputs, dependencies.
- A simple dependency list/graph.
- Provisional in-platform vs whitespace tag per block.
