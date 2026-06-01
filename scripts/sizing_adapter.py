#!/usr/bin/env python3
"""sizing_adapter.py — normalize intake `scale.*` → databricks-sizing inputs (seam S5-1a).

The Blueprint intake collects scale loosely ("~5TB", "200 concurrent users", "40 tenants",
often UNKNOWN). `databricks-sizing` wants structured inputs. This adapter is the bridge,
and — critically — it carries the **honesty contract** forward: every inferred value is
flagged with impact-if-wrong + confidence, so non-interactive runs (interactive: false)
infer-and-flag rather than block (intake_schema.md "Non-interactive runs").

It does NOT compute sizing — it shapes the request. databricks-sizing owns the numbers.
Per-tenant unit economics is the separate post-step in tenant_economics.py (seam S5-1b).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

UNKNOWN = "UNKNOWN"


@dataclass
class Scale:
    """Mirrors intake `scale:` (+ a couple of design-shaping fields)."""
    tenants: str = UNKNOWN          # "40", "~50 orgs"
    data_volume: str = UNKNOWN      # "5TB", "500 GB"
    concurrency: str = UNKNOWN      # "200 users", "50 peak queries"
    latency_sla: str = UNKNOWN      # interactive | batch | streaming
    archetype: str = UNKNOWN        # built-on-multitenant | connected-isv | data-collaboration


@dataclass
class Assumption:
    field: str
    inferred: str
    rationale: str
    impact_if_wrong: str
    confidence: str  # high | medium | low


@dataclass
class SizingRequest:
    workload_profile: str
    data_volume_gb: float | None
    peak_concurrency: int | None
    tenants: int | None
    sql_warehouse_class: str          # serverless-sql | jobs-compute | mixed
    notes: list[str] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)
    confidence: str = "low"           # overall — capped low while any blocking input is UNKNOWN


def _parse_bytes_gb(s: str) -> float | None:
    if not s or s == UNKNOWN:
        return None
    m = re.search(r"([\d.]+)\s*(pb|tb|gb|mb)", s.lower())
    if not m:
        return None
    val, unit = float(m.group(1)), m.group(2)
    return val * {"pb": 1_000_000, "tb": 1_000, "gb": 1, "mb": 0.001}[unit]


def _parse_int(s: str) -> int | None:
    if not s or s == UNKNOWN:
        return None
    m = re.search(r"(\d[\d,]*)", s.replace(",", ""))
    return int(m.group(1)) if m else None


def to_sizing_inputs(scale: Scale, interactive: bool = True) -> SizingRequest:
    """Map loose intake scale → a structured databricks-sizing request, flagging inferences."""
    assumptions: list[Assumption] = []

    data_gb = _parse_bytes_gb(scale.data_volume)
    if data_gb is None:
        data_gb = 1_000.0
        assumptions.append(Assumption(
            "scale.data_volume", "1 TB",
            "No volume given; 1 TB is a conservative mid-market multi-tenant starting point.",
            "Cost scales ~linearly with storage+scan; a 10x miss moves the cost dimension a full band.",
            "low"))

    concurrency = _parse_int(scale.concurrency)
    if concurrency is None:
        concurrency = 50
        assumptions.append(Assumption(
            "scale.concurrency", "50 peak",
            "No concurrency given; 50 peak interactive users is a typical B2B analytics tier.",
            "Drives warehouse size/count; under-sizing degrades p95 latency, over-sizing wastes spend.",
            "low"))

    tenants = _parse_int(scale.tenants)
    if tenants is None and scale.archetype == "built-on-multitenant":
        tenants = 25
        assumptions.append(Assumption(
            "scale.tenants", "25",
            "Multi-tenant archetype with no tenant count; 25 is a plausible early-GA roster.",
            "Tenant count is the denominator of per-tenant economics — directly sets the fixed-floor effect.",
            "low"))

    # Latency → compute class.
    sla = (scale.latency_sla or UNKNOWN).lower()
    if "stream" in sla:
        warehouse, profile = "mixed", "streaming+interactive"
    elif "batch" in sla:
        warehouse, profile = "jobs-compute", "batch"
    elif "interactive" in sla:
        warehouse, profile = "serverless-sql", "interactive-analytics"
    else:
        warehouse, profile = "serverless-sql", "interactive-analytics"
        assumptions.append(Assumption(
            "constraints.latency_sla", "interactive",
            "No SLA given; conversational/BI built-on products are interactive by default.",
            "Wrong here flips the whole compute model (serverless SQL vs jobs vs streaming).",
            "medium"))

    blocking_unknown = any(a.confidence == "low" for a in assumptions)
    req = SizingRequest(
        workload_profile=profile,
        data_volume_gb=data_gb,
        peak_concurrency=concurrency,
        tenants=tenants,
        sql_warehouse_class=warehouse,
        assumptions=assumptions,
        confidence="low" if blocking_unknown else "medium",
    )
    if blocking_unknown and not interactive:
        req.notes.append(
            "Non-interactive run: scale inferred, not confirmed. Cost dimension (rubric dim 3) "
            "stays low-confidence and may be capped at 3 — record as an irreducible gap, not a failure.")
    return req


if __name__ == "__main__":
    import json
    from dataclasses import asdict
    demo = Scale(tenants="40 brands", data_volume="5TB", concurrency="200 users",
                 latency_sla="interactive", archetype="built-on-multitenant")
    print(json.dumps(asdict(to_sizing_inputs(demo)), indent=2))
