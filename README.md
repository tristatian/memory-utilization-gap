# The Memory-Utilization Gap: cultural provenance of LLM-generated analogies

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

**Pilot result (preliminary, keyword-flagged; human coding in progress):**
across 660 generations (Gemini Flash-Lite, Gemma 31B), culturally tailored
analogy vehicles appear in 0.5% of responses at L0, 0.5% at L1, and 29% at
L4 — background in memory produced no detectable change over baseline, while
the identical fact stated in the request moved behavior ~30 points. The
strongest canonical trope (gradient descent's foggy-mountain hiker, 60/60
generations) survives even explicit steering: models re-skin it with local
proper nouns ("like Huangshan or Taishan") rather than select a different
analogy.

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
