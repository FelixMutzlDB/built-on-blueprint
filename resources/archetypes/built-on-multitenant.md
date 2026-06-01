# Archetype — Built-On, multi-tenant analytics

> Databricks is the load-bearing foundation; end users interact only with your
> domain-specific product and never have a Databricks account. Reference:
> Advancing Analytics "Built on Databricks: delivering multi-tenant analytics".

## Defining signals
- `users_know_databricks: false`
- You are both a data consumer (internally) and a data provider (to customers).
- Goal: avoid a year-long internal build by standing on the platform.

## Canonical capabilities (Stage 1 — product-agnostic)
Adopt these as the Stage-1 building-block skeleton; add/remove for the specific idea.
Keep them as *capabilities* — do NOT bind to Databricks products here (that's Stage 3).
- **Tenant data ingestion** — land each org's data incrementally.
- **Modeling / medallion transform** — conform raw into per-tenant gold marts.
- **Semantic layer** — define governed business metrics once. *(Hard prerequisite.)*
- **Multi-tenancy & isolation** — map end-user→org→backend identity; guarantee no cross-tenant reads.
- **Embedded dashboards** — per-tenant analytics inside your product.
- **Conversational analytics** — NL → governed answer over the tenant's data.
- **App shell & embedding UX** — host the above inside your product (mostly whitespace).
- **Auth bridge (SSO→SPN)** — exchange end-user session → per-org backend identity.
- **Tenant onboarding & lifecycle** — provision identity, scope, marts, defaults per org.
- **Per-tenant cost attribution** — attribute platform spend per org for margin/chargeback.
- **Observability & quality** — pipeline health, query SLA, answer quality, isolation audit.
- **Evaluation harness** — score/guard conversational-analytics answers before & during prod.

## Component map (Stage 3 — bind capabilities to Databricks)
| Capability | Databricks component | Notes |
|----------------|----------------------|-------|
| Identity / multi-tenancy | **SSO-SPN pattern**: end users auth via their IdP (Entra/Okta/Auth0); backend calls use a **per-organization Service Principal** | End user has NO Databricks account / no UC provisioning |
| Governance & isolation | **Unity Catalog** — row/column-level security, lineage, external locations | Reuse UC's model; do not rebuild access control |
| Query surface (SQL) | **DBSQL Warehouse** via the org's SPN | |
| Conversational analytics | **Genie** grounded in Metric Views + Knowledge Store | Quality == upstream semantic modeling quality |
| Embedded dashboards | **AI/BI Dashboards** reading governed metric definitions | |
| Custom domain UX / workflows | **Databricks Apps** | Avoids parallel hosting infra |
| Semantic layer | **Unity Catalog Metric Views** | Hard prerequisite for good Genie |
| Observability & quality | **System tables** + **Lakehouse Monitoring** + **MLflow traces** | One fabric across data + AI |
| Evaluation harness | **MLflow 3 GenAI evaluate** + `@scorer`s, dataset in UC | Gates the conversational block |

## Three-layer administration (do NOT merge)
- **End users** — product consumers, no admin.
- **Tenant admins** — customer-side, manage their org's users; must NOT need to learn UC.
- **Platform admins** — you; SPN provisioning + workspace/tenant mapping.

## Isolation model
Per-org SPN ⇒ audit trails trace to the correct tenant; UC row-level filtering
prevents cross-tenant leakage; user identity preserved in *application* logs, not
Databricks system tables.

## Known tradeoffs / failure modes (surface these in Stage 5 whitespace)
- **Abstraction vs flexibility** — resist "rebuilding the Databricks UI"; a poor
  imitation is the classic anti-pattern.
- **Semantic-layer investment is mandatory**, not optional.
- **Documentation must use customer-domain vocabulary** — linking to Databricks docs
  breaks the abstraction.

## Whitespace (you own, not the platform)
Customer-facing app shell & auth UX, tenant onboarding/billing, domain documentation,
SPN lifecycle automation, per-tenant cost attribution & chargeback.

## Cost shape (for Stage 5)
Dominant drivers: DBSQL warehouse concurrency × tenant count, Genie/serving usage,
Apps compute. Multi-tenant ⇒ model per-tenant unit economics, not just aggregate.
