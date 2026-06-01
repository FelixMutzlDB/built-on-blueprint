# Stage 3 — Map to Databricks + solution architecture

## Steps
1. Translate each Stage-1 capability to concrete Databricks components using the
   archetype's **"Component map (Stage 3)"** table as the default; deviate only with a
   stated reason.
2. Resolve cross-cutting concerns once: identity/SPN, Unity Catalog governance,
   networking/egress, secrets, observability (system tables / MLflow traces).
3. Define the data flow and component dependencies end-to-end.
4. **Draw it** — invoke `fe-architecture-diagram` (or `drawio-diagram` /
   `lucid-diagram`) to render the solution architecture from the component map.
   Do not hand-draw ASCII as the deliverable.
5. Use `databricks-docs` to verify any component capability you're unsure about.

## Output → `03-architecture.md` (+ diagram artifact)
- Building block → Databricks component table (with rationale for deviations).
- Cross-cutting decisions (identity, governance, network, secrets, observability).
- Rendered architecture diagram (link/path).
- Open architectural questions / rejected alternatives (→ decision log).
