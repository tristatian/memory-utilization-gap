#!/usr/bin/env python3
"""Analysis: canonical-trope rates by steering level and the memory-utilization gap.

Reads coding.csv. Human codes (`canonical_trope_used`, `congruent`) are used
where present; trope rates fall back to `auto_trope_flag` on uncoded rows, and
the output reports how many rows in each cell are hand-verified so automatic
and human numbers are never silently mixed.

Reported per model:
  trope rate by level (stratum A) — does the canonical trope lose grip as steering increases?
  congruence rate by level        — human-coded rows only
  memory-utilization gap          = congruence(L4) − congruence(L1)
  per-concept trope rate at L0    — which canonical tropes exert the strongest pull
"""
import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent

def rate(rows, pred):
    rows = list(rows)
    return (sum(1 for r in rows if pred(r)) / len(rows), len(rows)) if rows else (None, 0)

def fmt(r, n):
    return f"{r*100:5.1f}% (n={n})" if r is not None else f"    — (n={n})"

def main():
    with (HERE / "coding.csv").open() as f:
        data = list(csv.DictReader(f))
    providers = sorted({r["model"] for r in data})
    levels = sorted({str(r["level"]) for r in data})

    print("=== Canonical trope rate by model, stratum A (auto flag; hand-coded rows use your judgment) ===")
    for p in providers:
        print(f"\n{p}:")
        for lvl in levels:
            cell = [r for r in data if r["model"] == p and str(r["level"]) == lvl and r["stratum"] == "A"]
            def used_trope(r):
                return (r["canonical_trope_used"].strip().lower() in ("yes", "y", "1", "true")
                        if r["canonical_trope_used"].strip() else r["auto_trope_flag"] == "YES")
            r_, n = rate(cell, used_trope)
            hand = sum(1 for r in cell if r["canonical_trope_used"].strip())
            print(f"  L{lvl}: trope rate {fmt(r_, n)}  [{hand}/{n} hand-verified]")

    print("\n=== Congruence rate by level (hand-coded rows only) ===")
    gaps = {}
    for p in providers:
        print(f"\n{p}:")
        by_level = {}
        for lvl in levels:
            cell = [r for r in data if r["model"] == p and str(r["level"]) == lvl
                    and r["congruent"].strip()]
            r_, n = rate(cell, lambda r: r["congruent"].strip().lower() in ("yes", "y", "1", "true"))
            by_level[lvl] = r_
            print(f"  L{lvl}: congruent {fmt(r_, n)}")
        if by_level.get('4') is not None and by_level.get('1') is not None:
            gaps[p] = by_level['4'] - by_level['1']
            print(f"  → memory utilization gap (L4−L1): {gaps[p]*100:+.1f} points")

    print("\n=== Per-concept trope rates at L0 (which tropes have the strongest gravity?) ===")
    for cid in sorted({r["concept_id"] for r in data if r["stratum"] == "A"}):
        cell = [r for r in data if r["concept_id"] == cid and str(r["level"]) == "0"]
        r_, n = rate(cell, lambda r: r["auto_trope_flag"] == "YES")
        print(f"  {cid:24s} {fmt(r_, n)}")

if __name__ == "__main__":
    main()
