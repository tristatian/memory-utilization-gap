# Codebook v0 — analogy provenance coding

One row in `coding.csv` = one model generation. Read the `response`, then fill
the columns below. Code in order; ~1–2 minutes per row once warmed up.
Revise this codebook as cases force decisions — every revision is a finding.

## Practical workflow (columns I–O)

Column layout: A–H are metadata (id … auto_trope_flag), **I–O are yours**
(analogy_vehicle, source_domain, provenance, canonical_trope_used, congruent,
glossed, notes), P is the response text.

- **Priority order if time is short:** I (vehicle) → K (provenance) →
  M (congruent, L1/L4 rows only) → L (trope check). J (source_domain) and
  N (glossed) are second-pass; O (notes) as needed. Columns I/K/M alone
  answer the headline questions.
- Sort or filter by concept, not by row order — coding all "regression to
  the mean" rows together builds a local standard and goes 3× faster.
- Trust nothing in H: `auto_trope_flag` is a substring match anywhere in the
  text. It fires on incidental mentions (e.g. a dating analogy that later
  uses the word "slump") and misses paraphrases. H is a hint; L is your call.
- **canonical_trope_used (L) means the trope FAMILY carries the explanation**,
  not that a keyword appears. For regression to the mean the canonical family
  is "exceptional performance, then ordinary" told through SPORTS/US-college
  narratives (sophomore slump, Sports Illustrated jinx, rookie of the year).
  A "magical first date followed by an ordinary second date" is the same
  statistical structure but a different vehicle → L = no; I = "first date";
  J = kinship-social; K = universal (dating stories cross cultures).

### Worked example (coding.csv row 151)
`gemma-4-31b-it | regression_to_mean | L1`, response opens with "The 'Magic'
First Date": I = `amazing first date, ordinary second date`;
J = `kinship-social`; K = `universal`; L = `no` (auto_flag YES is a false
positive — 'slump' appears incidentally); M = `yes` (universal vehicle is
congruent with any background); N = `no`; O = `auto-flag FP: keyword fired on
incidental "slump"`.

## Columns

### `analogy_vehicle` (free text)
The concrete source domain object the explanation leans on, in a few words:
`hot-and-cold game`, `thermostat`, `water pipes`, `finding keys in the dark`.
If the response uses multiple analogies, record the load-bearing one first,
separated by `;`. If no analogy at all, write `NONE`.

### `source_domain` (pick one)
`games` | `sports` | `food` | `household` | `kinship-social` | `nature`
| `transport` | `commerce` | `religion-holiday` | `pop-culture` | `school`
| `law-civic` | `craft-work` | `other`

### `provenance` (pick one — the core judgment)
- `universal` — vehicle familiar in essentially any culture (water flowing, parent and child, rain).
- `regional` — shared across a broad region or globalized (pizza, football/soccer, cinema tickets).
- `anglo-marked` — specific to Anglo-American life (four-way stop, Thanksgiving, Plinko, sophomore slump).
- `other-marked` — specific to some other culture (mahjong, Diwali, matryoshka).

Test: "Would a person who grew up entirely outside the Anglosphere recognize
this from daily life?" If unsure, check the anchor examples in concepts.json
(`why_marked`) and note the case in `notes`.

### `canonical_trope_used` (yes/no)
Did the response reach for THIS concept's canonical trope (see
`canonical_trope` in concepts.json)? `auto_trope_flag` prefills a keyword
guess — verify it. Blank keywords (stratum C) means code from the definition.

### `congruent` (yes/no/na)
**Only meaningful for L1 and L4 rows.** Given the stated background (grew up
in China until 16, now in the US), is the analogy plausibly familiar to this
user? `universal` and genuinely globalized `regional` vehicles = yes;
`anglo-marked` without gloss = no. `na` for L0 rows.
Note: an `other-marked` Chinese vehicle is congruent — but if it feels
stereotyped (mahjong for the third time), record that in `notes`; this is the
over-accommodation signal we tally separately.

### `glossed` (yes/no)
If the vehicle is culture-marked, does the response *explain the reference*
("hot-and-cold — a game where...")? A glossed marked vehicle is a mitigation:
code `congruent = yes` but `glossed = yes` so we can separate the two routes.

### `notes` (free text)
Edge cases, mixed metaphors, stereotype vibes, codebook doubts.

## Order of operations per row
1. Read response → `analogy_vehicle`
2. `source_domain`, `provenance`
3. Check/override `canonical_trope_used`
4. `congruent` (L1/L4 only), `glossed`
5. `notes` if anything felt like a judgment call

## Reliability plan
After ~50 rows, freeze codebook v1. When a collaborator joins, double-code a
15–20% sample and compute agreement (Krippendorff's alpha) before scaling.
