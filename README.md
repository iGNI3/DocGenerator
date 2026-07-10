# Agent DocX Builder

Autonomous document-generation agent that plans, writes, self-checks, and renders professional Word documents from natural-language requests.

## Supported LLM Providers

| Provider | API Key Env Var | Default Model | Free Tier |
|---|---|---|---|
| **Groq** | `GROQ_API_KEY` | `llama-3.3-70b-versatile` | ✅ |
| **OpenAI** | `OPENAI_API_KEY` | `gpt-4o` | ❌ |
| **Google Gemini** | `GOOGLE_API_KEY` | `gemini-2.5-flash` | ✅ |
| **Anthropic** | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` | ❌ |
| **OpenRouter** | `OPENROUTER_API_KEY` | `llama-3.3-70b-instruct` | Partial |
| **DeepInfra** | `DEEPINFRA_API_KEY` | `Llama-3.3-70B-Instruct` | Partial |

Set **any one** API key — the provider is auto-detected. Override with `LLM_PROVIDER` and `LLM_MODEL` env vars if needed.

## Architecture

```
POST /agent {"request": "..."}
        │
        ▼
 ┌─────────────────┐
 │ 1. VALIDATE      │  Pydantic: reject empty / too-short requests
 └────────┬─────────┘
          ▼
 ┌─────────────────┐
 │ 2. PLAN          │  LLM call #1 → doc_type, title, assumptions,
 │   (tool: plan)   │  task_list, section outline
 └────────┬─────────┘
          ▼
 ┌─────────────────┐
 │ 3. WRITE         │  LLM call #2 → full section content
 │  (tool: write)   │  (paragraphs, bullets, optional tables)
 └────────┬─────────┘
          ▼
 ┌─────────────────┐
 │ 4. REFLECT       │  LLM call #3 → {status: pass/revise, notes[]}
 │ (tool: reflect)  │  if "revise": ONE corrective re-run of step 3
 └────────┬─────────┘
          ▼
 ┌─────────────────┐
 │ 5. RENDER        │  Deterministic Python (python-docx)
 │ (tool: render)   │  Title, Heading 1/2, bullets, tables
 └────────┬─────────┘
          ▼
   Return JSON + downloadable .docx
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- An API key from any supported provider (see table above)

### 2. Setup

```bash
cd agent-docx-builder
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env — uncomment and set ONE provider's API key
```

### 3. Run

```bash
uvicorn main:app --reload --port 8000
```

### 4. Test

**Standard request:**
```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{"request": "Create a project plan for launching a new mobile banking app onboarding feature, including timeline, team roles, and risks."}'
```

**Complex / ambiguous request:**
```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{"request": "We need something for the client about our Q3 initiative — make it look professional and include next steps, but I do not have exact numbers yet."}'
```

**Download a generated document:**
```bash
curl -O http://localhost:8000/documents/<filename>.docx
```

### 5. API Endpoints

| Method | Path                      | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/health`                 | Liveness probe                     |
| POST   | `/agent`                  | Generate a document from a request |
| GET    | `/documents/{filename}`   | Download a generated .docx file    |

## Project Structure

```
agent-docx-builder/
├── .env.example          # Environment variable template (all providers)
├── requirements.txt      # Dependencies
├── main.py               # FastAPI application + routes
├── agent/
│   ├── __init__.py
│   ├── providers.py      # LLM provider registry + auto-detection
│   ├── models.py         # Pydantic schemas (request, response, pipeline)
│   ├── llm_client.py     # Multi-provider LLM client + retry/backoff
│   ├── planner.py        # LLM call #1 — structured plan generation
│   ├── writer.py         # LLM call #2 — full content generation
│   ├── reflector.py      # LLM call #3 — self-check / quality review
│   ├── renderer.py       # Deterministic DOCX rendering (no LLM)
│   └── orchestrator.py   # Pipeline engine + tool registry
├── outputs/              # Generated .docx files
└── README.md
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `*_API_KEY` | One required | API key for your chosen provider |
| `LLM_PROVIDER` | Optional | Force a specific provider (e.g. `google`) |
| `LLM_MODEL` | Optional | Override the default model |

### Adding a New Provider

Any OpenAI-compatible provider can be added in 5 lines — just add an entry
to `PROVIDER_REGISTRY` in `agent/providers.py`:

```python
"my_provider": ProviderConfig(
    name="My Provider",
    provider_type=ProviderType.OPENAI_COMPATIBLE,
    api_key_env="MY_PROVIDER_API_KEY",
    base_url="https://api.myprovider.com/v1",
    default_model="model-name",
),
```

## Key Design Decisions

- **Multi-provider** — auto-detect from env, no vendor lock-in
- **No LangChain / CrewAI** — plain Python for full transparency
- **Reflection loop** — self-check improves output quality with one corrective pass
- **Deterministic rendering** — formatting reliability over LLM flexibility
- **Tool registry** — named callables for inspectable, extensible orchestration

## License

MIT
