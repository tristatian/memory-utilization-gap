#!/usr/bin/env python3
"""Per-concept summary of what analogies actually surfaced, by steering level.

For each concept and level, reports: number of runs, the expected canonical
trope and how often it surfaced (keyword flag), and the distribution of
analogy *vehicles* that actually appeared — extracted heuristically by
bucketing responses against a vehicle lexicon (first bucket to appear in the
text wins) with a bold-title fallback for unmatched responses.

Heuristic, for triage before human coding — not a substitute for it.

Output: summary.md (tables) + a console digest.
"""
import json, re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent

# Vehicle lexicon: bucket -> keywords. A response is assigned the bucket whose
# keyword appears EARLIEST in the text (analogies are announced up front).
VEHICLES = {
    "mountain/hiking/fog": ["mountain", "hiker", "hiking", "foggy", "fog ", "valley", "downhill", "uphill", "summit", "blindfold"],
    "hot-and-cold game": ["hot-and-cold", "hot and cold", "you're getting warmer", "warmer!", "getting warmer"],
    "thermostat/AC": ["thermostat", "air condition", " ac ", "furnace", "heater"],
    "cooking/tasting/recipe": ["cook", "recipe", "soup", "seasoning", "taste", "chef", "dish", "stir-fry", "wok", "dumpling", "hot pot", "hotpot", "tea "],
    "courtroom/trial": ["courtroom", "trial", "judge", "jury", "defendant", "innocent until", "guilty", "prosecutor"],
    "detective/investigation": ["detective", "sherlock", "clue", "investigat", "suspect"],
    "water/pipes/plumbing": ["water pipe", "plumbing", "hose", "water flow", "water pressure", "pipe"],
    "mail/delivery": ["mail", "letter", "envelope", "postal", "post office", "courier", "package", "parcel", "delivery"],
    "traffic/roads/intersection": ["traffic", "intersection", "four-way", "stop sign", "highway", "road", "crossroad"],
    "doorway/politeness standoff": ["doorway", "after you", "both wait", "narrow door"],
    "market/bargaining/shopping": ["market", "bargain", "vendor", "stall", "shopping", "grocery", "store"],
    "exam/school/students": ["exam", "test score", "student", "gaokao", "class", "studying", "school"],
    "sports": ["basketball", "baseball", "soccer", "football", "athlete", "batting", "sports", "ping pong", "ping-pong", "badminton"],
    "game show/doors": ["game show", "monty", "three doors", "door number", "goat"],
    "gambling/dice/lottery": ["casino", "roulette", "lottery", "dice", "coin flip", "coin toss", "mahjong", "poker", "slot machine"],
    "farming/gardening": ["farmer", "farming", "garden", "crop", "harvest", "plant"],
    "guessing/darts/target": ["dart", "target practice", "guessing game", "archery", "bullseye"],
    "bathtub/shower/kitchen": ["shower", "bathtub", "faucet", "kettle", "sink"],
    "body/temperature/health": ["body temperature", "fever", "thirst", "hunger", "sweat"],
    "family/household": ["parent", "child ", "family", "sibling", "household chores"],
    "queue/line/waiting": ["queue", "waiting in line", "line up"],
    "music/instrument": ["piano", "guitar", "tuning", "orchestra", "instrument"],
}

GENERIC_BOLD = re.compile(r"^(step|the situation|why|how|note|first|second|third|in short|summary|key|goal|analogy)\b", re.I)

def bucket_of(text: str):
    low = text.lower()
    best, pos = None, len(low) + 1
    for name, kws in VEHICLES.items():
        for kw in kws:
            i = low.find(kw)
            if 0 <= i < pos:
                best, pos = name, i
    return best

def bold_title(text: str):
    for m in re.findall(r"\*\*(.{4,70}?)\*\*", text):
        if not GENERIC_BOLD.match(m.strip()):
            return m.strip()
    return None

def main():
    concepts = {c["id"]: c for c in json.loads((HERE / "concepts.json").read_text())["concepts"]}
    recs = [json.loads(l) for l in (HERE / "results.jsonl").read_text().splitlines() if l.strip()]
    recs = [r for r in recs if r["model"] in ("gemini-3.1-flash-lite", "gemma-4-31b-it")]

    lines = ["# Pilot summary: what surfaced, by concept and steering level",
             "", "Heuristic vehicle bucketing — triage aid, not human coding.", ""]
    for cid, c in concepts.items():
        rows = [r for r in recs if r["concept_id"] == cid]
        if not rows:
            continue
        lines += [f"## {c['name']}  (stratum {c['stratum']})",
                  f"Expected canonical trope: **{c['canonical_trope']}**", "",
                  "| level | runs | canonical surfaced | top vehicles that actually surfaced |",
                  "|---|---|---|---|"]
        for lvl in ("0", "0c", "1", "1c", "2", "4"):
            cell = [r for r in rows if str(r["level"]) == lvl]
            if not cell:
                continue
            kws = c["trope_keywords"]
            hits = sum(1 for r in cell if kws and any(k in r["response"].lower() for k in kws))
            buckets = Counter()
            for r in cell:
                b = bucket_of(r["response"])
                if b is None:
                    t = bold_title(r["response"])
                    b = f"«{t[:40]}»" if t else "(unclassified)"
                buckets[b] += 1
            top = ", ".join(f"{b} ×{n}" for b, n in buckets.most_common(4))
            trope_cell = f"{hits}/{len(cell)}" if kws else "n/a (no canonical)"
            lines.append(f"| L{lvl} | {len(cell)} | {trope_cell} | {top} |")
        lines.append("")
    out = HERE / "summary.md"
    out.write_text("\n".join(lines))
    print(f"wrote {out} ({len(lines)} lines)")

if __name__ == "__main__":
    main()
