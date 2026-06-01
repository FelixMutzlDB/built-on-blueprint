# Archetype — Connected ISV  *(stub — expand)*

> Customers knowingly use their OWN Databricks; your product connects to the lakehouse.

## Defining signals
- `users_know_databricks: true`; customer brings their own workspace/UC.

## Building blocks → components (TODO expand)
- Connection & auth: OAuth / PAT / SPN against the *customer's* workspace.
- Read/write surface: Statement Execution API, DBSQL, Delta, UC volumes.
- Governance: respect the customer's UC grants — you are a guest.

## Tradeoffs (TODO)
- Least-privilege scoping; version/feature skew across customer workspaces; egress.

## Whitespace (TODO)
- Connection management UX, credential rotation, customer-side setup docs.

TODO: flesh out from PWAF "Integration & Built-On Deployment Models" + connector guidance.
