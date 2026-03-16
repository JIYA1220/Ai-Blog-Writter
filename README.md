# AI Blog Writer — Agentic Blog Generation System

> Production-ready blog writer built as a **stateful LangGraph DAG** — structured, validated, and parallelised.

---

## Architecture

```
START
  └─► ROUTER          (adaptive: retrieval vs pure generation)
        ├─► RETRIEVER  (Tavily web search + deduplication)  ← if needed
        └─► PLANNER    (structured BlogPlan with section goals + word budgets)
              └─► DISPATCHER (fans out parallel writers via Send API)
                    ├─► WRITER [section 0]  ┐
                    ├─► WRITER [section 1]  ├─ run in PARALLEL
                    ├─► WRITER [section 2]  │
                    └─► WRITER [section N]  ┘
                          └─► REDUCER (deterministic merge + Pydantic validation)
                                └─► END (saves .md file to output/)
```

---
## Project Structure

```
blog_ai/
├── main.py              ← Entry point (run this)
├── graph.py             ← LangGraph DAG definition
```,old_string:
├── requirements.txt
├── .env.example         ← Copy to .env and fill in keys
│
├── agents/
│   ├── router.py        ← Decides retrieval vs generation
│   ├── retriever.py     ← Tavily search + deduplication
│   ├── planner.py       ← Structured blog plan
│   ├── writer.py        ← Parallel section writers (Send API)
│   └── reducer.py       ← Deterministic merger + file saver
│
├── schemas/
│   └── models.py        ← Pydantic schemas (BlogPlan, SectionPlan, etc.)
│
├── utils/
│   ├── llm.py           ← OpenRouter LLM client
│   └── logger.py        ← Rich console logger
│
└── output/              ← Generated blogs saved here as .md
```

---

## Setup (PyCharm)

### Step 1 — Clone / open the project
Open the `blog_ai/` folder in PyCharm.

### Step 2 — Create a virtual environment
```
PyCharm → Settings → Project → Python Interpreter → Add → Virtualenv
```
Or from terminal:
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set up your API keys
```bash
cp .env.example .env
```
Then open `.env` and fill in:

| Variable | Where to get it | Free? |
|---|---|---|
| `OPENROUTER_API_KEY` | https://openrouter.ai/keys | ✅ Free account |
| `TAVILY_API_KEY` | https://app.tavily.com | ✅ Free 1000 searches/mo |

### Step 5 — Choose your model (in .env)
```
# FREE models (no cost):
MODEL_NAME=meta-llama/llama-3.1-8b-instruct:free
MODEL_NAME=mistralai/mistral-7b-instruct:free

# Paid (better quality):
MODEL_NAME=openai/gpt-4o-mini
MODEL_NAME=openai/gpt-4o
```

### Step 6 — Run
```bash
python main.py
```

---

## What happens when you run it

1. **Router** analyses your topic → decides if web search is needed
2. **Retriever** (if needed) → searches Tavily, deduplicates 6 evidence snippets
3. **Planner** → creates structured plan: section goals, constraints, word budgets
4. **Dispatcher** → fans out one writer per section (run in parallel)
5. **Writers** → each section written independently, simultaneously
6. **Reducer** → sorts by section_id, assembles markdown, validates with Pydantic
7. **Output** → saved to `output/your_topic.md`

---

## Key concepts demonstrated

| Concept | Where | Why it matters |
|---|---|---|
| Stateful DAG | `graph.py` | Explicit state = debuggable system |
| Conditional routing | `router.py` | Adaptive, not hardcoded |
| Deduplication | `retriever.py` | Grounded, non-redundant evidence |
| Structured planning | `planner.py` | Writers follow a contract, not free-form |
| Parallel execution | `writer.py` (Send API) | Scale without waiting |
| Deterministic merge | `reducer.py` | Consistent ordering every time |
| Schema validation | `schemas/models.py` | Nothing malformed leaks through |

---

## Troubleshooting

**`ValueError: OPENROUTER_API_KEY not set`**
→ Make sure `.env` exists and the key is filled in (not the placeholder text)

**LLM returns bad JSON**
→ Normal occasionally — the system has fallback handlers at every node

**Tavily returns no results**
→ System degrades gracefully to pure generation — still works

**Rate limit errors**
→ Reduce `MAX_CONCURRENCY=1` in `.env` for free tier models
