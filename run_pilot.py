#!/usr/bin/env python3
"""Generation runner: sample analogy explanations across memory-steering levels.

Measures whether user-background information changes which analogies an LLM
reaches for when explaining technical concepts. Conditions form a
dose-response ladder of steering strength:

  L0 — no user information (baseline analogy distribution)
  L1 — a simulated long-term-memory block states the user's background;
       the request itself is identical to L0
  L4 — the user states their background in the request and asks for a
       familiar analogy (upper bound: what the model can do when asked)

The L4-vs-L1 difference is the "memory-utilization gap": the distance between
what the model can do and what stored memory elicits spontaneously.

Concepts and their canonical-trope metadata live in concepts.json.
Output: results.jsonl, append-only and resumable — rerunning skips any
(model, concept, level, sample) cell already present, so interrupted runs
and newly added concepts only generate what's missing.

Providers: Google Gemini API (free tier; requests throttled to stay under
free-tier rate limits) and a local model via Ollama. GEMINI_API_KEY is read
from the environment or from a .env file next to this script.

Usage:
  python3 run_pilot.py --models gemini --gemini-model gemini-3.1-flash-lite
  python3 run_pilot.py --models gemini --gemini-model gemma-4-31b-it
  python3 run_pilot.py --models ollama --ollama-model gemma3:4b --k 3 --dry-run

Note on free-tier model choice: the newest Gemini Flash tier may have a very
low free daily quota (e.g. 20 requests/day); flash-lite and gemma model ids
carry the high (~1,500/day) quota. If a model id 404s or 503s, list live ids
with client.models.list().
"""
import argparse, json, os, sys, time
from pathlib import Path

HERE = Path(__file__).parent
CONCEPTS_FILE = HERE / "concepts.json"
RESULTS_FILE = HERE / "results.jsonl"

def load_dotenv():
    """Load KEY=VALUE lines from .env (handles optional 'export ' and quotes)."""
    env = HERE / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip("'\""))

load_dotenv()

# Simulated long-term-memory block for the L1 condition. Mimics the format
# consumer assistants use when injecting saved user facts into context.
# The persona is the study's fixed experimental stimulus, not a live profile.
MEMORY_BLOCK = (
    "Saved information about the user (from previous conversations):\n"
    "- The user grew up in China and lived there until age 16, then moved to the United States.\n"
    "- The user's first language is Mandarin Chinese; they are fluent in English.\n"
    "- The user is an independent researcher interested in statistics and machine learning."
)

def build_condition(level: str, concept_prompt_name: str):
    """Returns (system_instruction_or_None, user_prompt).

    Formal ladder: L0 (no info) / L1 (memory block) / L2 (memory block +
    generic personalization instruction, mimicking product system prompts) /
    L4 (background stated in the request, tailoring demanded).

    Casual variants — the request never mentions analogies or tailoring, so
    any adaptation is spontaneous rather than instruction-following:
    L0c (casual ask, no info) / L1c (casual ask + memory block; the most
    ecologically valid approximation of a real user with product memory).
    """
    base = f"Explain {concept_prompt_name} to a layperson using an analogy from everyday life."
    casual = (
        f"hey, i never really got {concept_prompt_name}. "
        f"can you explain it in a way that actually clicks?"
    )
    if level == "0":
        return None, base
    if level == "1":
        return MEMORY_BLOCK, base
    if level == "2":
        return MEMORY_BLOCK + "\n\nPersonalize your responses to the user when helpful.", base
    if level == "4":
        return None, (
            f"I grew up in China and lived there until I was 16. Explain {concept_prompt_name} "
            f"to me using an analogy from everyday life that would be familiar to me."
        )
    if level == "0c":
        return None, casual
    if level == "1c":
        return MEMORY_BLOCK, casual
    raise ValueError(f"unknown level {level}")

# ---------------- providers ----------------

class GeminiProvider:
    name = "gemini"
    def __init__(self, model: str):
        from google import genai  # pip install google-genai
        from google.genai import types
        self._types = types
        self.model = model
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.min_interval = 7.0  # ~8.5 RPM, safely under the 10 RPM free-tier cap
        self._last = 0.0
    def generate(self, system: str | None, prompt: str) -> str:
        wait = self.min_interval - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        cfg = self._types.GenerateContentConfig(temperature=1.0, system_instruction=system)
        resp = self.client.models.generate_content(model=self.model, contents=prompt, config=cfg)
        self._last = time.time()
        return resp.text or ""

class OllamaProvider:
    name = "ollama"
    def __init__(self, model: str):
        self.model = model
        self.url = "http://localhost:11434/api/chat"
    def generate(self, system: str | None, prompt: str) -> str:
        import urllib.request
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": prompt}
        ]
        body = json.dumps({
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": 1.0},
        }).encode()
        req = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())["message"]["content"]

# ---------------- runner ----------------

def load_done() -> set:
    done = set()
    if RESULTS_FILE.exists():
        for line in RESULTS_FILE.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                done.add(rec["id"])
    return done

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="gemini,ollama", help="comma list: gemini,ollama")
    ap.add_argument("--gemini-model", default="gemini-flash-latest",
                    help="if this alias 404s, list models in AI Studio and pass the current Flash id")
    ap.add_argument("--ollama-model", default="gemma3:4b")
    ap.add_argument("--k", type=int, default=10, help="samples per cell")
    ap.add_argument("--levels", default="0,1,4")
    ap.add_argument("--dry-run", action="store_true", help="print the run plan, no API calls")
    args = ap.parse_args()

    concepts = [c for c in json.loads(CONCEPTS_FILE.read_text())["concepts"] if c["pilot"]]
    levels = [x.strip() for x in args.levels.split(",")]
    providers = []
    for m in args.models.split(","):
        if m == "gemini":
            if not args.dry_run and "GEMINI_API_KEY" not in os.environ:
                sys.exit("Set GEMINI_API_KEY (free key: https://aistudio.google.com/apikey)")
            providers.append(("gemini", args.gemini_model))
        elif m == "ollama":
            providers.append(("ollama", args.ollama_model))

    plan = [(pname, pmodel, c, lvl, i)
            for pname, pmodel in providers
            for c in concepts for lvl in levels for i in range(args.k)]
    done = load_done()
    todo = [(pn, pm, c, l, i) for pn, pm, c, l, i in plan
            if f"{pm}|{c['id']}|L{l}|{i}" not in done]
    print(f"plan: {len(plan)} generations | already done: {len(plan)-len(todo)} | to run: {len(todo)}")
    est_min = sum(7 for pn, *_ in todo if pn == "gemini") / 60
    print(f"estimated Gemini throttle time: ~{est_min:.0f} min")
    if args.dry_run:
        for pn, pm, c, l, i in todo[:10]:
            print(" ", pn, pm, c["id"], f"L{l}", i)
        return

    live = {}
    for pname, pmodel in providers:
        live[pname] = GeminiProvider(pmodel) if pname == "gemini" else OllamaProvider(pmodel)

    with RESULTS_FILE.open("a") as out:
        for n, (pn, pm, c, lvl, i) in enumerate(todo, 1):
            system, prompt = build_condition(lvl, c["prompt_name"])
            rid = f"{pm}|{c['id']}|L{lvl}|{i}"
            for attempt in range(4):
                try:
                    text = live[pn].generate(system, prompt)
                    break
                except Exception as e:
                    backoff = 20 * (attempt + 1)
                    print(f"  [{rid}] error ({e}); retry in {backoff}s", file=sys.stderr)
                    time.sleep(backoff)
            else:
                print(f"  [{rid}] FAILED after retries, skipping", file=sys.stderr)
                continue
            out.write(json.dumps({
                "id": rid, "provider": pn, "model": pm, "concept_id": c["id"],
                "stratum": c["stratum"], "level": lvl, "sample": i,
                "system": system, "prompt": prompt, "response": text,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }, ensure_ascii=False) + "\n")
            out.flush()
            print(f"[{n}/{len(todo)}] {rid} ok ({len(text)} chars)")
    print(f"done → {RESULTS_FILE}")

if __name__ == "__main__":
    main()
