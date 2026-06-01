#!/usr/bin/env python3
"""tenant_economics.py — per-tenant unit economics post-step (seam S5-1b).

databricks-sizing produces AGGREGATE monthly spend. But the whole point of a Built-On
product is **per-tenant unit economics** — what does one customer cost to serve, and how
does the fixed floor (always-on endpoints, baseline storage, control plane) amortize as
tenants are added? That post-processing lives nowhere in the specialist skills, so it
lives here.

Models the fixed-floor effect explicitly:
  total(n)        = fixed_monthly + variable_per_tenant * n
  per_tenant(n)   = total(n) / n          # falls as n grows — the amortization curve
  break_even(p)   = fixed / (price - variable_per_tenant)   # tenants to cover the floor

This is the number a built-on founder actually needs to price a plan. It is best-effort
and inherits the confidence of the sizing inputs (see sizing_adapter.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TenantEconomics:
    active_tenants: int
    total_monthly: float
    fixed_monthly: float
    variable_per_tenant: float
    per_tenant_cost: float
    fixed_share_pct: float            # how floor-dominated the model is at this scale
    break_even_tenants: int | None    # None if no price given
    curve: list[tuple[int, float]]    # (n, per_tenant_cost) amortization curve
    confidence: str
    notes: list[str] = field(default_factory=list)


def per_tenant(aggregate_monthly: float,
               fixed_monthly: float,
               active_tenants: int,
               price_per_tenant: float | None = None,
               confidence: str = "low") -> TenantEconomics:
    """Decompose aggregate spend into per-tenant unit economics + the fixed-floor curve."""
    if active_tenants < 1:
        raise ValueError("active_tenants must be >= 1")
    variable_total = max(aggregate_monthly - fixed_monthly, 0.0)
    variable_per_tenant = variable_total / active_tenants
    per_tenant_cost = aggregate_monthly / active_tenants
    fixed_share = (fixed_monthly / aggregate_monthly * 100) if aggregate_monthly else 0.0

    break_even = None
    notes: list[str] = []
    if price_per_tenant is not None:
        margin = price_per_tenant - variable_per_tenant
        if margin <= 0:
            notes.append(
                f"Price ${price_per_tenant:.0f}/tenant does NOT cover variable cost "
                f"${variable_per_tenant:.0f}/tenant — no break-even at any scale. Reprice or cut variable cost.")
        else:
            import math
            break_even = math.ceil(fixed_monthly / margin)
            notes.append(
                f"Break-even at {break_even} tenants (price ${price_per_tenant:.0f} − "
                f"variable ${variable_per_tenant:.0f} = ${margin:.0f} contribution covers the "
                f"${fixed_monthly:.0f} fixed floor).")

    # Amortization curve — show how per-tenant cost falls as the floor spreads.
    curve = []
    for n in sorted({1, 5, 10, 25, 50, 100, active_tenants}):
        if n >= 1:
            curve.append((n, round((fixed_monthly + variable_per_tenant * n) / n, 2)))

    if fixed_share > 60:
        notes.append(
            f"Floor-dominated ({fixed_share:.0f}% fixed): per-tenant cost is highly sensitive "
            f"to tenant count. Scale-to-zero / shared endpoints materially change the math.")

    return TenantEconomics(
        active_tenants=active_tenants,
        total_monthly=round(aggregate_monthly, 2),
        fixed_monthly=round(fixed_monthly, 2),
        variable_per_tenant=round(variable_per_tenant, 2),
        per_tenant_cost=round(per_tenant_cost, 2),
        fixed_share_pct=round(fixed_share, 1),
        break_even_tenants=break_even,
        curve=curve,
        confidence=confidence,
        notes=notes,
    )


if __name__ == "__main__":
    import json
    from dataclasses import asdict
    # Example: $18k/mo aggregate, $6k always-on floor, 25 tenants, $1,200/tenant plan.
    econ = per_tenant(aggregate_monthly=18_000, fixed_monthly=6_000,
                      active_tenants=25, price_per_tenant=1_200, confidence="low")
    print(json.dumps(asdict(econ), indent=2))
