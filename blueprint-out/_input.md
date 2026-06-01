# Smoke-test input — "Firefly" (fuzzy idea, as a user would paste it)

Firefly is a B2B SaaS company selling marketing analytics to mid-market e-commerce
brands. Today brand marketers log into the Firefly web app to see a handful of
pre-canned charts; anything deeper means a CSV export into a spreadsheet. Firefly
wants to embed real per-brand analytics dashboards AND a natural-language "ask your
data" assistant directly in the product so a marketer can ask "which campaigns drove
the most repeat purchases in Q2?" and get an answer without leaving Firefly.

The current backend is a homegrown Postgres + nightly cron ETL stack that is buckling
at ~400 brands and getting slower every month. The eng team is strong on app dev
(React/Node) but thin on data engineering and has no ML people. They are weighing a
year-long internal rebuild vs. "building on" a platform. Someone suggested Databricks.
Brands must never see each other's data, and a marketer should never need to know
Databricks exists.

(No repo provided. No explicit budget. Mostly US brands, a few EU. No stated SLA.)
