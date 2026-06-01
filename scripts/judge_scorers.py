#!/usr/bin/env python3
"""judge_scorers.py — PWAF rubric → MLflow GenAI scorers + gate (Stage 6, seam S6-1).

Formalizes resources/rubric/pwaf-rubric.md as runnable MLflow `@scorer` functions so the
LLM-as-judge stage is *wired*, not just described. Composes the agent-evaluation /
databricks-mlflow-evaluation skills.

Each of the 8 PWAF dimensions becomes a numeric (1–5) judge scorer. A composite gate
applies the rubric's pass rule:
    PASS  ⟺  every dimension ≥ 3  AND  dims 1/2/6 (non-negotiable) ≥ 4.
Dimension 3 (cost) may be capped at 3 under UNKNOWN scale — that is an *irreducible gap*,
recorded, not a hard failure (seam S6-1, intake_schema "Non-interactive runs").

Usage:
    import mlflow
    from judge_scorers import pwaf_scorers, apply_gate
    results = mlflow.genai.evaluate(data=eval_df, scorers=pwaf_scorers())
    gate = apply_gate(results.tables["eval_results"])   # -> {"passed": bool, ...}

Judge model is configurable: env BLUEPRINT_JUDGE_ENDPOINT (default a Databricks FM endpoint).
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

DEFAULT_JUDGE_ENDPOINT = os.getenv("BLUEPRINT_JUDGE_ENDPOINT", "databricks-claude-sonnet-4")


@dataclass(frozen=True)
class Dimension:
    key: str
    num: int
    name: str
    what_5: str
    min_score: int            # gate floor for this dimension
    non_negotiable: bool      # dims 1/2/6


# Mirrors resources/rubric/pwaf-rubric.md exactly. Single source of truth in code.
RUBRIC: list[Dimension] = [
    Dimension("pattern_grounding", 1, "Pattern grounding",
              "Correct PWAF classification; design anchored to a real archetype, not invented.",
              4, True),
    Dimension("security_isolation", 2, "Security & isolation",
              "Multi-tenant isolation explicit; least-privilege; cross-tenant leakage addressed; "
              "compliance/residency honored.", 4, True),
    Dimension("cost", 3, "Cost",
              "Sizing tied to stated scale; per-tenant unit economics; assumptions + confidence marked.",
              3, False),
    Dimension("reliability_ops", 4, "Reliability & operations",
              "SLA/availability, observability (system tables/MLflow), failure modes covered.", 3, False),
    Dimension("architecture_fit", 5, "Architecture fit",
              "Components used idiomatically; deviations justified; no 'rebuild the Databricks UI' "
              "anti-pattern.", 3, False),
    Dimension("whitespace_honesty", 6, "Whitespace honesty",
              "What Databricks does NOT cover is explicit and effort-tagged; no overclaiming.", 4, True),
    Dimension("buildability", 7, "Buildability",
              "Roadmap sequenced & testable; success criteria measurable; evals defined for AI parts.",
              3, False),
    Dimension("traceability", 8, "Traceability",
              "Every claim traces to an input or a recorded assumption; decision log present.", 3, False),
]

_JUDGE_PROMPT = """You are a Databricks Partner Well-Architected Framework (PWAF) reviewer.
Score the blueprint below on ONE dimension only.

Dimension {num} — {name}
A score of 5 looks like: {what_5}

Scoring (integer 1–5):
  5 fully meets the bar · 4 minor gaps · 3 adequate, notable gaps ·
  2 significant gaps · 1 absent or wrong.
Be strict: reward grounded, specific, honest content; penalize hand-waving and overclaiming.
If the blueprint explicitly records an *irreducible gap* (e.g. cost under UNKNOWN scale),
do not penalize below 3 for that gap alone.

Return ONLY JSON: {{"score": <int 1-5>, "rationale": "<one sentence citing the evidence>"}}

--- BLUEPRINT ---
{blueprint}
--- END ---
"""


def _judge_call(prompt: str, endpoint: str) -> str:
    """Single chat completion against a Databricks serving endpoint. Stable SDK surface."""
    from mlflow.deployments import get_deploy_client

    client = get_deploy_client("databricks")
    resp = client.predict(
        endpoint=endpoint,
        inputs={"messages": [{"role": "user", "content": prompt}], "temperature": 0.0,
                "max_tokens": 400},
    )
    return resp["choices"][0]["message"]["content"]


def _parse_judge(raw: str) -> tuple[int, str]:
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return 1, f"unparseable judge output: {raw[:120]}"
    try:
        d = json.loads(m.group(0))
        return int(d["score"]), str(d.get("rationale", ""))
    except Exception as e:  # noqa: BLE001
        return 1, f"judge parse error: {e}"


def _make_scorer(dim: Dimension, endpoint: str):
    """Build one MLflow @scorer for a rubric dimension. Returns a 1–5 Feedback."""
    from mlflow.genai.scorers import scorer
    from mlflow.entities import Feedback

    @scorer(name=f"pwaf_{dim.num}_{dim.key}")
    def _s(outputs) -> Feedback:  # outputs = the generated blueprint (str or dict)
        blueprint = outputs if isinstance(outputs, str) else json.dumps(outputs)
        prompt = _JUDGE_PROMPT.format(num=dim.num, name=dim.name, what_5=dim.what_5,
                                      blueprint=blueprint)
        score, rationale = _parse_judge(_judge_call(prompt, endpoint))
        return Feedback(value=score, rationale=f"[min {dim.min_score}"
                        f"{', non-negotiable' if dim.non_negotiable else ''}] {rationale}")

    return _s


def pwaf_scorers(endpoint: str = DEFAULT_JUDGE_ENDPOINT) -> list:
    """All 8 dimension scorers, ready for mlflow.genai.evaluate(scorers=...)."""
    return [_make_scorer(d, endpoint) for d in RUBRIC]


def apply_gate(per_dimension: dict[str, int]) -> dict:
    """Apply the rubric gate to a {dimension_key: score} mapping.

    PASS ⟺ all ≥ min_score AND dims 1/2/6 ≥ 4. Returns failures + irreducible-gap notes.
    """
    failures, irreducible = [], []
    for d in RUBRIC:
        score = per_dimension.get(d.key)
        if score is None:
            failures.append(f"dim {d.num} {d.name}: no score")
            continue
        if score < d.min_score:
            failures.append(f"dim {d.num} {d.name}: {score} < {d.min_score}"
                            + (" (NON-NEGOTIABLE)" if d.non_negotiable else ""))
        elif d.key == "cost" and score == 3:
            # Passes the floor, but cost stuck at 3 usually means scale was UNKNOWN.
            # Document the cap so a soft cost score reads as a known limit, not silence (S6-1).
            irreducible.append("dim 3 Cost: capped at 3 — likely UNKNOWN scale; "
                               "confirm scale to lift, else accept as an irreducible gap")
    return {
        "passed": not failures,
        "failures": failures,
        "irreducible_gaps": irreducible,
        "verdict": "PASS" if not failures else "REVISE & RE-SCORE",
    }


if __name__ == "__main__":
    # Demo the gate logic with no MLflow/endpoint dependency.
    sample = {"pattern_grounding": 5, "security_isolation": 4, "cost": 3, "reliability_ops": 4,
              "architecture_fit": 5, "whitespace_honesty": 5, "buildability": 4, "traceability": 4}
    print(json.dumps(apply_gate(sample), indent=2))
