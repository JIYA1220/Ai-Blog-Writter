# AI Blog Writer — Advanced Agentic Blog System

> A state-of-the-art blog writing system built as a **Stateful, Async LangGraph DAG** — featuring parallel execution, real-time grounding, and automated quality evaluation.

---

## 🚀 Advanced Architecture

```
START
  └─► ROUTER (Async)    ── Decide: Retrieval vs Generation
        ├─► RETRIEVER   ── Tavily Search + Deduplication
        └─► PLANNER     ── Structured BlogPlan (Section Goals)
              └─► DISPATCHER ── Parallel Fan-Out (Send API)
                    ├─► WRITER [Section 0] ┐
                    ├─► WRITER [Section 1] ├─ Parallel Async
                    └─► WRITER [Section N] ┘
                          └─► REDUCER   ── Merge & Sort
                                └─► EVALUATOR ── LLM-as-Judge (Scoring)
                                      └─► END ── Save Markdown
```

---

## Key Advanced Features

| Feature | Technical Implementation | Why it matters |
|---|---|---|
| **Async Orchestration** | `asyncio` + LangGraph `ainvoke` | High-concurrency support, non-blocking I/O |
| **Parallel Writing** | LangGraph `Send` API | Section generation in parallel (Fast!) |
| **Observability** | **LangSmith** Integration | Full trace analysis, cost tracking, debugging |
| **Evaluation Loop** | **LLM-as-Judge** Node | Automated quality scoring (1-10) and feedback |
| **Grounded Retrieval** | **Tavily AI** Search | Prevents hallucinations with real-world evidence |
| **REST API** | **FastAPI** + Pydantic | Deployable as a backend microservice |
| **Modern UI** | **Streamlit** | Interactive dashboard with past blog browser |

---

## 🛠️ Setup & Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` and fill in:
- `GOOGLE_API_KEY` or `OPENROUTER_API_KEY`
- `TAVILY_API_KEY` (Optional for web search)
- **`LANGSMITH_API_KEY`** (Optional for tracing — highly recommended)

### 3. Run the Application
You have three ways to run the system:

- **CLI Mode:**
  ```bash
  python main.py
  ```
- **Streamlit Dashboard (Best UI):**
  ```bash
  streamlit run app.py
  ```
- **API Server (Production):**
  ```bash
  python server.py
  ```

---

## 🔬 Observability & Evaluation

### LangSmith Tracing
To enable full observability:
1. Create an account at [smith.langchain.com](https://smith.langchain.com).
2. Add your `LANGSMITH_API_KEY` to the `.env` file.
3. Every run will be automatically traced, showing latency, token usage, and graph flow.

### LLM-as-Judge
The final node in the DAG is an **Evaluator**. It analyzes the finished blog against the requested topic, audience, and tone. It provides:
- **Score (1-10):** A metric of overall quality.
- **Reasoning:** Why the blog received that score.
- **Suggestions:** Actionable feedback for manual polish.

---

## Project Structure

```
blog_ai/
├── main.py              ← Async Entry point
├── server.py            ← FastAPI REST API
├── app.py               ← Streamlit Dashboard
├── graph.py             ← LangGraph DAG definition
├── requirements.txt     ← Dependencies
│
├── agents/
│   ├── router.py        ← Decides retrieval vs generation (Async)
│   ├── retriever.py     ← Tavily search + deduplication (Async)
│   ├── planner.py       ← Structured blog plan (Async)
│   ├── writer.py        ← Parallel section writers (Async)
│   ├── reducer.py       ← Deterministic merger + file saver (Async)
│   └── evaluator.py     ← LLM-as-Judge editor (Async)
│
├── schemas/
│   └── models.py        ← Pydantic schemas (BlogPlan, Evaluation, etc.)
│
├── utils/
│   ├── llm.py           ← LLM client + LangSmith config
│   └── logger.py        ← Rich console logger
│
└── output/              ← Generated blogs saved here
```

---

## RESUME POSITIONING (For MTech Freshers)

**"Built an advanced agentic blog generation system using LangGraph with stateful async DAG orchestration, parallel section writing via the Send API, and RAG-based fact grounding through Tavily. Implemented an LLM-as-judge evaluation loop for automated quality scoring and LangSmith tracing for full system observability."**
