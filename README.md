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
concept is sampled at three steering levels:

- **L0** — no user information
- **L1** — the user's background sits in a simulated long-term-memory block
- **L4** — the user states their background and asks for a familiar analogy

The **memory-utilization gap** is the L4−L1 difference: the distance between
what the model *can* do and what memory *elicits*.

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
