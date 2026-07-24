# Documentation Q&A Bot (RAG)

Local Retrieval-Augmented Generation app: upload a PDF/Word document and ask questions answered **only from that document**, with **page-number citations**.

No Docker. No cloud account required (Ollama + local embeddings by default).

## Stack

| Layer | Tech |
|---|---|
| UI | React + Vite |
| API | FastAPI (async) |
| RAG | LlamaIndex |
| LLM | Ollama (Llama 3) — optional OpenAI |
| Embeddings | HuggingFace `BAAI/bge-small-en-v1.5` — optional OpenAI |
| Metadata | SQLite |
| Vectors | On-disk LlamaIndex indexes |
| Jobs | FastAPI `BackgroundTasks` |
| Cache | In-memory TTL |

## Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com)

## Run locally

### 1. Ollama

```bash
ollama pull llama3
```

### 2. Backend

```bash
python -m venv .venv
source .venv/Scripts/activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:3000

### 4. Use it

1. Upload a `.pdf` or `.docx`
2. Wait until status is **Ready**
3. Ask questions — answers include page citations

First indexing run downloads the embedding model (one-time).

## Optional: OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_PROVIDER=openai
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Project layout

```
app/           # FastAPI + RAG pipeline
frontend/      # React chat UI
tests/         # API / unit tests
data/          # SQLite DB + vector indexes (runtime)
uploads/       # Uploaded files (runtime)
```

## Troubleshooting

| Issue | Fix |
|---|---|
| Cannot reach Ollama | Start the Ollama app |
| `model not found` | `ollama pull llama3` |
| First embed is slow | Normal — HuggingFace model download |
| `npm run` path errors on Windows | Scripts already use `node node_modules/...` (folder names with `&`) |

## License

MIT
