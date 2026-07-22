#!/usr/bin/env python3
"""Convert results.jsonl into coding.csv for human annotation.

Each generation gets one row with blank coding columns (see codebook.md for
definitions). The `auto_trope_flag` column pre-fills a keyword-match guess at
whether the concept's canonical trope was used — an assist for the annotator,
not a verdict: record the human judgment in `canonical_trope_used`.

Idempotent: rows already coded in coding.csv are preserved verbatim on rerun;
only new results are appended.
"""
import csv, json
from pathlib import Path

HERE = Path(__file__).parent
RESULTS = HERE / "results.jsonl"
OUT = HERE / "coding.csv"

CODING_COLS = ["analogy_vehicle", "source_domain", "provenance",
               "canonical_trope_used", "congruent", "glossed", "notes"]

def main():
    concepts = {c["id"]: c for c in json.loads((HERE / "concepts.json").read_text())["concepts"]}
    existing = {}
    if OUT.exists():
        with OUT.open() as f:
            for row in csv.DictReader(f):
                existing[row["id"]] = row

    rows = []
    with RESULTS.open() as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec["id"] in existing:
                rows.append(existing[rec["id"]])
                continue
            kws = concepts[rec["concept_id"]]["trope_keywords"]
            text = rec["response"].lower()
            auto = "YES" if any(k in text for k in kws) else ("" if not kws else "no")
            rows.append({
                "id": rec["id"], "provider": rec["provider"], "model": rec["model"],
                "concept_id": rec["concept_id"],
                "stratum": rec["stratum"], "level": rec["level"], "sample": rec["sample"],
                "auto_trope_flag": auto, "response": rec["response"],
                **{c: "" for c in CODING_COLS},
            })

    fieldnames = ["id", "provider", "model", "concept_id", "stratum", "level", "sample",
                  "auto_trope_flag"] + CODING_COLS + ["response"]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    coded = sum(1 for r in rows if r.get("source_domain"))
    print(f"{OUT}: {len(rows)} rows ({coded} already coded). Open in Numbers/Excel/Sheets and code away.")

if __name__ == "__main__":
    main()
