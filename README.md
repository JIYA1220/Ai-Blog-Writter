# AI Blog Writer (Agentic Blog Generation System)

<div align="center">

<!-- BADGES / STACK (TOP) -->
<img src="https://img.shields.io/badge/LangGraph-Async%20DAG-7C3AED?style=for-the-badge" />
<img src="https://img.shields.io/badge/LangChain-LLM%20Framework-0EA5E9?style=for-the-badge" />
<img src="https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge" />
<img src="https://img.shields.io/badge/FastAPI-API-059669?style=for-the-badge" />
<img src="https://img.shields.io/badge/Tavily-Web%20Search-111827?style=for-the-badge" />
<img src="https://img.shields.io/badge/Ollama-Local%20LLMs-1F2937?style=for-the-badge" />
<img src="https://img.shields.io/badge/OpenRouter-Cloud%20LLMs-F59E0B?style=for-the-badge" />
<img src="https://img.shields.io/badge/Gemini-Google%20GenAI-2563EB?style=for-the-badge" />
<img src="https://img.shields.io/badge/Pydantic-Types%20%26%20Validation-16A34A?style=for-the-badge" />
<img src="https://img.shields.io/badge/Rich-CLI%20UI-22C55E?style=for-the-badge" />
<img src="https://img.shields.io/badge/Uvicorn-ASGI%20Server-0EA5E9?style=for-the-badge" />
<img src="https://img.shields.io/badge/pytest-Testing-14B8A6?style=for-the-badge" />

<br/><br/>

<b>An agentic, production-style blog writing system</b> built as a <b>stateful, async LangGraph DAG</b> with <b>parallel section writing</b>, optional <b>web grounding</b>, and <b>LLM-as-a-judge evaluation</b>.

<br/>

</div>

---  
Run it via **CLI**, **Streamlit UI**, or a **FastAPI server**.

---

##  Tools / Tech Stack (Top)

**Core Orchestration**
- **LangGraph** — stateful DAG orchestration (async) + parallel fan-out
- **LangChain** — LLM tooling & integrations

**LLM Providers (choose one)**
- **Ollama (local)** — run models locally (no cloud key needed)
- **OpenRouter (cloud)** — access multiple hosted models
- **Google Gemini (cloud)** — Google GenAI models

**Grounding / Search (Optional)**
- **Tavily** — web search for retrieval + reducing hallucinations

**UI / API**
- **Streamlit** — interactive app (generate + browse past blogs)
- **FastAPI** + **Uvicorn** — REST API for production use

**Observability (Optional)**
- **LangSmith** — traces, debugging, latency/cost insight (if you configure it)

**Developer Experience**
- **Pydantic v2** — typed schemas + validation
- **Rich** — clean CLI UI/logging
- **pytest** + **httpx** — testing utilities

---

##  Demo Video

> Add your demo video file to the repo (recommended path: `assets/demo.mp4`), then this embed will work:

<video src="assets/demo.mp4" controls width="100%"></video>


---

##  What it does

Given:
- a **topic**
- a **target audience**
- a **tone**

…this system:
1. decides whether the topic needs retrieval (**router**)
2. optionally retrieves grounded info via Tavily (**retriever**)
3. creates a structured multi-section plan (**planner**)
4. writes sections **in parallel** (**writer fan-out**)
5. merges sections into a final markdown blog (**reducer**)
6. evaluates the output with an LLM-based editor (**evaluator**)

Generated blogs are saved as `.md` files under `output/`.

---

##  Architecture (LangGraph DAG)

```text
START
  └─► ROUTER (Async)    ── Decide: Retrieval vs Generation
        ├─► RETRIEVER   ── Tavily Search + Deduplication (optional)
        └─► PLANNER     ── Structured BlogPlan (Section Goals)
              └─► DISPATCHER ── Parallel Fan-Out (Send API)
                    ├─► WRITER [Section 0] ┐
                    ├─► WRITER [Section 1] ├─ Parallel Async
                    └─► WRITER [Section N] ┘
                          └─► REDUCER     ── Merge & Save Markdown
                                └─► EVALUATOR ── LLM-as-Judge (Score + Feedback)
                                      └─► END
```

---

##  Installation

### 1) Clone the repo
```bash
git clone https://github.com/JIYA1220/Ai-Blog-Writter.git
cd Ai-Blog-Writter
```

### 2) Create a virtual environment (recommended)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

---

##  Environment Variables

Copy `.env.example` → `.env`:

```bash
cp .env.example .env
```

### Required (depends on your provider)
- **If using Gemini**: `GOOGLE_API_KEY`
- **If using OpenRouter**: `OPENROUTER_API_KEY`
- **If using Ollama locally**: no API key needed, but Ollama must be installed & running

### Optional (recommended)
- `TAVILY_API_KEY` — enables web retrieval/grounding
- `MAX_CONCURRENCY` — parallel section writers
- `SECTION_WORD_BUDGET` — max words per section
- *(Optional if your code supports it)* `LANGSMITH_API_KEY` — tracing/observability

Example `.env`:
```env
MODEL_NAME=ollama/qwen2.5:7b
# GOOGLE_API_KEY=your_gemini_api_key_here
# OPENROUTER_API_KEY=your_openrouter_api_key_here
# TAVILY_API_KEY=your_tavily_api_key_here

SECTION_WORD_BUDGET=300
MAX_CONCURRENCY=3
```

---

##  How to Run

You can run the system in **three modes**:

### 1) CLI Mode
```bash
python main.py
```

### 2) Streamlit UI (recommended)
```bash
streamlit run app.py
```

What you get:
- a blog generation form (topic / audience / tone)
- a sidebar to browse previously generated markdown files in `output/`
- download button for generated blogs

### 3) FastAPI Server (REST API)
```bash
python server.py
```

Server runs at:
- `http://localhost:8000`

---

##  API Usage (FastAPI)

### Health check
```bash
curl http://localhost:8000/
```

### Generate a blog
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The Rise of Agentic AI Systems in 2025",
    "target_audience": "tech-curious professionals",
    "tone": "informative and engaging"
  }'
```

Response includes:
- blog `title` + full markdown `content`
- optional evaluation `score` and `evaluation`
- `word_count`

---

##  Project Structure

```text
.
├── main.py              # CLI entry point (async)
├── server.py            # FastAPI server
├── app.py               # Streamlit UI
├── graph.py             # LangGraph DAG definition
├── list_models.py       # Utility to list/inspect configured models (if used)
├── requirements.txt     # Python dependencies
├── .env.example         # Example env vars
│
├── agents/              # Graph nodes (router/retriever/planner/writer/reducer/evaluator)
├── schemas/             # Pydantic models (state + structured outputs)
├── utils/               # LLM client config, logging helpers, etc.
└── output/              # Generated blogs saved as .md files
```

---

##  Testing (optional)

If/when you add tests:
```bash
pytest -q
```

---

##  Troubleshooting

### “.env file not found!”
Create one:
```bash
cp .env.example .env
```

### Generation fails / empty output
Common causes:
- missing API key (Gemini/OpenRouter)
- wrong `MODEL_NAME`
- provider not reachable (network issue)
- Ollama not running locally (if using `ollama/...` model)

### Ollama tips (local)
Install Ollama and ensure it’s running, then pull your model:
```bash
ollama pull qwen2.5:7b
```

## 👤 Author

Built by **@JIYA1220**.
