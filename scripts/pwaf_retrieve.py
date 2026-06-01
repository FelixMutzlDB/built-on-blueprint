#!/usr/bin/env python3
"""pwaf_retrieve.py — grounding retrieval for Built-On Blueprint.

Replaces model-recall with retrieval over TWO corpora (per seam S3-1, the grounding
gap is wider than PWAF patterns alone):

  1. PWAF corpus       — partner well-architected patterns, archetypes, deployment models
                         (https://databrickslabs.github.io/partner-architecture/).
  2. Product-capability — Databricks product facts the architecture stage leans on
                         (Lakeflow Connect CDC, Genie-respects-RLS, UC isolation, etc.).
                         Stage 3 maps blocks→components; those claims must be grounded too.

This is also the **future App / MCP backend**: keep the public surface (`retrieve`) stable
so a Claude Code skill, a Databricks App, and an MCP server are all thin clients over it.

Backends (auto-selected, override with --backend):
  * vector_search — Databricks Vector Search (production path). Requires env config below.
  * local         — zero-infra lexical fallback over the bundled resources/ corpus so the
                    skill runs today. Lower recall; flagged in results as low-confidence.

Env config (vector_search backend):
  BLUEPRINT_VS_ENDPOINT        Vector Search endpoint name
  BLUEPRINT_VS_INDEX_PWAF      UC index for the PWAF corpus      (catalog.schema.index)
  BLUEPRINT_VS_INDEX_PRODUCT   UC index for product-capability facts
  DATABRICKS_HOST / _TOKEN     standard SDK auth

CLI:
  python pwaf_retrieve.py "per-tenant isolation for multi-tenant analytics" --corpus all --k 5
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal

Corpus = Literal["all", "pwaf", "product"]
RESOURCES = Path(__file__).resolve().parent.parent / "resources"

# Local fallback corpus roots. product_facts/ is a TODO corpus (see GROUNDING.md) —
# it may not exist yet; the local backend degrades gracefully when it's empty.
LOCAL_SOURCES = {
    "pwaf": [RESOURCES / "archetypes", RESOURCES / "rubric"],
    "product": [RESOURCES / "product_facts"],
}


@dataclass
class Chunk:
    text: str
    source: str            # file path or UC index id
    corpus: str            # "pwaf" | "product"
    score: float           # backend-native relevance (cosine for VS, lexical for local)
    confidence: str        # "high" (vector_search) | "low" (local lexical fallback)


# --------------------------------------------------------------------------- #
# Backend protocol
# --------------------------------------------------------------------------- #
class RetrievalBackend:
    name = "base"

    def search(self, query: str, corpus: Corpus, k: int) -> list[Chunk]:
        raise NotImplementedError


class VectorSearchBackend(RetrievalBackend):
    """Databricks Vector Search. The production / App-backend path."""

    name = "vector_search"

    def __init__(self) -> None:
        self.endpoint = os.environ["BLUEPRINT_VS_ENDPOINT"]
        self.indexes = {
            "pwaf": os.environ["BLUEPRINT_VS_INDEX_PWAF"],
            "product": os.environ["BLUEPRINT_VS_INDEX_PRODUCT"],
        }
        # Imported lazily so the local backend has zero dependencies.
        from databricks.vector_search.client import VectorSearchClient  # type: ignore

        self._client = VectorSearchClient(disable_notice=True)

    def search(self, query: str, corpus: Corpus, k: int) -> list[Chunk]:
        targets = ["pwaf", "product"] if corpus == "all" else [corpus]
        out: list[Chunk] = []
        for c in targets:
            idx = self._client.get_index(self.endpoint, self.indexes[c])
            res = idx.similarity_search(
                query_text=query,
                columns=["text", "source"],
                num_results=k,
            )
            rows = res.get("result", {}).get("data_array", []) or []
            for row in rows:
                text, source, score = row[0], row[1], float(row[-1])
                out.append(Chunk(text, source, c, score, confidence="high"))
        out.sort(key=lambda ch: ch.score, reverse=True)
        return out[:k]


class LocalBackend(RetrievalBackend):
    """Zero-infra lexical fallback over bundled markdown. Low recall, always available."""

    name = "local"

    def search(self, query: str, corpus: Corpus, k: int) -> list[Chunk]:
        targets = ["pwaf", "product"] if corpus == "all" else [corpus]
        terms = _tokenize(query)
        scored: list[Chunk] = []
        for c in targets:
            for root in LOCAL_SOURCES[c]:
                if not root.exists():
                    continue
                for md in root.rglob("*.md"):
                    for para in _paragraphs(md.read_text(encoding="utf-8")):
                        s = _lexical_score(terms, para)
                        if s > 0:
                            scored.append(
                                Chunk(para.strip(), str(md), c, s, confidence="low")
                            )
        scored.sort(key=lambda ch: ch.score, reverse=True)
        return scored[:k]


# --------------------------------------------------------------------------- #
# Lexical helpers (local backend only)
# --------------------------------------------------------------------------- #
def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def _paragraphs(md: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", md) if len(p.strip()) > 40]


def _lexical_score(terms: set[str], para: str) -> float:
    toks = _tokenize(para)
    if not toks:
        return 0.0
    hits = len(terms & toks)
    return hits / (len(terms) or 1)  # fraction of query terms present


# --------------------------------------------------------------------------- #
# Public surface
# --------------------------------------------------------------------------- #
def select_backend(name: str | None = None) -> RetrievalBackend:
    if name == "local":
        return LocalBackend()
    if name == "vector_search" or (name is None and os.getenv("BLUEPRINT_VS_ENDPOINT")):
        try:
            return VectorSearchBackend()
        except Exception as e:  # missing config/deps → fall back, never hard-fail the skill
            print(f"[pwaf_retrieve] vector_search unavailable ({e}); using local.",
                  file=sys.stderr)
    return LocalBackend()


def retrieve(query: str, corpus: Corpus = "all", k: int = 5,
             backend: str | None = None) -> list[Chunk]:
    """Stable entry point. Skill stages and the App/MCP backend both call this."""
    return select_backend(backend).search(query, corpus, k)


def _main() -> None:
    ap = argparse.ArgumentParser(description="Retrieve PWAF + product grounding.")
    ap.add_argument("query")
    ap.add_argument("--corpus", choices=["all", "pwaf", "product"], default="all")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--backend", choices=["vector_search", "local"], default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    chunks = retrieve(a.query, a.corpus, a.k, a.backend)
    if a.json:
        print(json.dumps([asdict(c) for c in chunks], indent=2))
        return
    if not chunks:
        print("(no grounding found — product_facts/ corpus may be unbuilt; see GROUNDING.md)")
    for c in chunks:
        print(f"\n[{c.corpus} · {c.confidence} · {c.score:.2f}] {c.source}\n{c.text[:400]}")


if __name__ == "__main__":
    _main()
