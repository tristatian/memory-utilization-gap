# The Memory-Utilization Gap: cultural provenance of LLM-generated analogies

**→ [Read the full write-up with results and figures: REPORT.md](REPORT.md)**

Modern assistants keep long-term memory about their users — yet when Gemini,
which knew from memory that I grew up in China, explained maximum likelihood
estimation to me, it reached for the "hot-and-cold" parlor game: an
Anglo-American folklore reference I had never encountered. This repo measures
that phenomenon.

**Question.** When an LLM explains a technical concept with an analogy, does
stored knowledge of the user's cultural background change which analogy it
picks — and how much steering does it take?

**Design.** Concepts are stratified by *trope gravity* — whether English
pedagogy has a canonical, culturally marked analogy for them (stratum A:
p-values → courtroom, gradient descent → hot-and-cold; B: canonical but
globalized, e.g. circuits → water pipes; C: no canonical analogy). Each
concept is sampled at six steering levels, built from two ingredients — a
simulated **memory note** ("Saved information about the user: grew up in
China until 16, first language Mandarin, researcher interested in stats/ML")
placed in the system prompt, and a **question** asked either formally
("Explain X to a layperson using an analogy from everyday life") or casually
("hey, i never really got X. can you explain it in a way that actually
clicks?"):

- **L0** — formal question, no user information. Baseline: what analogies
  does the model reach for when it knows nothing about you?
- **L0c** — the same, casually phrased. Control for register: does
  formal wording itself suppress adaptation? (It doesn't.)
- **L1** — formal question, with the memory note present. The model knows
  the background; nothing asks it to use it.
- **L1c** — casual question + memory note. The most realistic condition:
  how a real user with product memory actually types.
- **L2** — formal question + memory note + a system line, "Personalize your
  responses to the user when helpful." Mimics how deployed products are
  actually configured.
- **L4** — no memory note; the user says it outright: "I grew up in China
  until I was 16 — explain X using an analogy that would be familiar to me."
  The ceiling: what the model does when adaptation is explicitly demanded.

L1, L1c and L2 measure what memory elicits *spontaneously*; L4 measures what
the model *can* do on demand. The **memory-utilization gap** is the distance
between the two.

**Headline result (all 1,339 outputs coded):** personalization is bang-bang.
With the user's background in simulated memory, culturally tailored analogies
occur in 0-2 of 220 responses per condition — even under an explicit
"personalize" system instruction, and even with naturalistic casual prompts —
while an explicit in-request demand flips 73% of responses to Chinese-specific
vehicles, overshooting into stereotype. Models use the same memory eagerly for
expertise-tailoring, so the missing wiring is specifically cultural.
Full findings, figures, and honest limitations: [REPORT.md](REPORT.md).

## Reproduce

```bash
pip install google-genai
echo 'GEMINI_API_KEY=<your key>' > .env   # free, no card: https://aistudio.google.com/apikey
python3 run_pilot.py --models gemini --gemini-model gemini-3.1-flash-lite
python3 run_pilot.py --models gemini --gemini-model gemma-4-31b-it
python3 coding_sheet.py    # build/refresh the annotation CSV
python3 analysis.py        # trope rates, congruence, the gap
```

Runs are resumable: rerunning skips completed (model, concept, level, sample)
cells, so interruptions and newly added concepts are cheap. The whole pilot
fits inside the Gemini API free tier. A local arm via Ollama is also
supported (`--models ollama`).

Note: the newest Flash tier may carry a very low free daily quota (~20/day);
`-lite` and `gemma-*` model ids carry the high (~1,500/day) quota.

## Files

| file | purpose |
|---|---|
| `concepts.json` | concept list with strata, canonical tropes, detection keywords |
| `run_pilot.py` | generation runner (Gemini API + Ollama), resumable |
| `coding_sheet.py` | builds `coding.csv` for human annotation |
| `codebook.md` | annotation instructions (source domain, provenance, congruence) |
| `analysis.py` | trope rates by level, memory-utilization gap |
| `results.jsonl` | raw generations |

## Coding notes

Cultural provenance requires native-informant judgment: e.g. this study
initially tagged "thermostat" as Anglo-marked; a rater who grew up in China
judged it familiar (urban climate-control panels), and it was reclassified as
a globalized vehicle (see `why_marked` in concepts.json). Contributions of
familiarity ratings from other cultural backgrounds are very welcome — open
an issue or PR.
