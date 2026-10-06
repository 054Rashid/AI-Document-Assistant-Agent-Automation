# AI Document Assistant & Agent Automation

A small practical AI project I built to learn how **RAG, AI agents, REST APIs, vector search, and automation** fit together.

Instead of making a chatbot that simply sends every question to an LLM, this project gives the assistant a couple of useful tools. It can search company documents and, when enabled, call a public JSON REST API for currency conversion.

> **Project level:** Fresher / learning project. The goal is to show an end-to-end understanding of the pieces, not to claim production-scale infrastructure.

## Why I built this

While learning Generative AI, I wanted to move beyond a simple "prompt an LLM" project. I wanted to understand the full path:

- How documents are loaded and cleaned
- How text is split into useful chunks
- How embeddings are created
- How a vector database finds relevant content
- How an agent can choose a tool
- How Python and REST APIs connect to the workflow
- How Docker can make the project easier to run
- Where n8n and Flowise fit into an automation workflow

## What it does

The project has two main paths.

### 1. Document search / RAG

```text
PDF / TXT files
      |
      v
Read + clean text
      |
      v
LangChain text splitter
      |
      v
Sentence Transformer embeddings
      |
      v
Qdrant vector database
      |
      v
Similarity search
      |
      v
Relevant document chunks
```

### 2. Simple AI-agent workflow

```text
User question
      |
      v
   AI Agent
    /    \
   /      \
Search    Currency
Docs        API
  |          |
  +----+-----+
       |
       v
  Final answer
```

When an LLM is configured, the agent decides whether it should use the document-search tool or the currency-conversion tool. Without an LLM key, the project still works in retrieval-only mode so the retrieval part can be tested first.

## Example questions

Try:

> What should I do if my laptop stops working?

> How long do I have to submit a travel claim?

> What is the meal reimbursement limit?

> Convert 40 USD to INR.

The first questions are answered from the sample company documents. The last question can use the REST API tool when agent mode is enabled.

## Tech stack

| Area | Technology |
|---|---|
| Language | Python |
| API | FastAPI |
| Agent tools | LangChain Core tools |
| Vector database | Qdrant |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Document parsing | pypdf / TXT |
| Text splitting | LangChain Text Splitters |
| LLM option | OpenAI-compatible Chat Completions API |
| REST API integration | Python `requests` + public JSON API |
| Automation | n8n workflow example |
| Visual agent workflow | Flowise setup guide |
| Deployment | Docker / Docker Compose |
| Testing | pytest |
| CI | GitHub Actions |

## Repository structure

```text
ai-document-assistant-agent-automation/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── agent.py
│       ├── chunking.py
│       ├── documents.py
│       ├── embeddings.py
│       ├── ingestion.py
│       ├── qdrant_store.py
│       └── rest_client.py
├── data/
│   └── documents/
│       ├── employee_handbook.txt
│       ├── it_support_policy.txt
│       └── travel_reimbursement_policy.txt
├── docs/
│   └── demo_questions.md
├── integrations/
│   ├── flowise_agent_setup.md
│   └── n8n_document_ingestion.json
├── scripts/
│   └── ingest_documents.py
├── tests/
│   ├── test_agent_fallback.py
│   ├── test_chunking.py
│   ├── test_documents.py
│   └── test_health.py
├── .github/workflows/ci.yml
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Run it locally

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/ai-document-assistant-agent-automation.git
cd ai-document-assistant-agent-automation
```

### 2. Create the environment file

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

The default `LLM_PROVIDER=none` lets you learn and test the retrieval layer without an LLM API key.

### 3. Start Qdrant and the API

```bash
docker compose up -d --build
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

### 4. Ingest the sample documents

Run from the project folder:

```bash
python scripts/ingest_documents.py
```

You should see counts for documents read, chunks created, and chunks stored.

### 5. Test semantic search

```bash
curl -X POST http://127.0.0.1:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"What should I do if my laptop stops working?","top_k":4}'
```

### 6. Test the agent endpoint

```bash
curl -X POST http://127.0.0.1:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the meal reimbursement limit?"}'
```

With `LLM_PROVIDER=none`, the endpoint returns the most relevant document content. This is intentional so the core RAG part is easy to inspect.

## Optional LLM agent mode

Add an OpenAI-compatible key to `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=your_model
OPENAI_BASE_URL=https://api.openai.com/v1
```

Then restart the API.

The agent exposes two tools:

1. `search_documents` - searches Qdrant for relevant company information.
2. `exchange_rate` - calls a public JSON REST API for currency conversion.

The model can decide which tool is useful for the user's question.

## n8n workflow

`integrations/n8n_document_ingestion.json` contains a small workflow that triggers the Python ingestion endpoint through an HTTP Request node.

The idea is simple:

```text
Manual trigger
      |
      v
n8n HTTP Request
      |
      v
FastAPI /api/ingest
      |
      v
Python ingestion pipeline
      |
      v
Qdrant
```

This shows where an automation platform can sit around a Python AI service.

## Flowise

`integrations/flowise_agent_setup.md` explains a beginner-friendly Flowise setup using:

```text
Chat Input
    -> Agent
    -> LLM
    -> Document Search HTTP Tool
    -> Chat Output
```

I kept this as a setup guide instead of claiming a version-specific Flowise export. The Python API remains the main part of the project.

## Testing

```bash
pytest -q
```

The tests cover text splitting, document loading, the retrieval-only fallback, and the FastAPI health endpoint.

## What I learned

The main lesson from this project was that an LLM is only one part of an AI application. The useful work around it includes preparing the data, retrieving the right information, defining tools, validating inputs, and connecting the pieces through APIs.

I also learned why retrieval should be visible and testable on its own. Seeing the matching chunks before asking an LLM to answer made it much easier to understand where a bad answer might come from.

## Limitations and next steps

This is a small learning project, so it intentionally keeps things simple. It does not include authentication, large-scale distributed processing, advanced observability, or a production deployment.

Possible next steps would be:

- Add document upload from a web UI
- Add conversation history
- Add more agent tools
- Add better evaluation for retrieval quality
- Deploy the Dockerized service with a platform such as Coolify

## How I would explain it in an interview

> "I built a small AI document assistant to understand how RAG and agents fit together. I used Python to read and clean PDF/TXT files, split the text with LangChain, generated embeddings with Sentence Transformers, and stored them in Qdrant for similarity search. I then added a simple agent layer with LangChain tools so the assistant can search documents or call a REST API when needed. FastAPI connects the Python logic, and Docker makes the setup easier to run. The project helped me understand how data processing, vector search, tools, APIs, and an LLM work together."

## Project level

**Fresher / personal learning project**

I built this project to practice the tools used in modern AI applications and to have something I could explain end to end in interviews.
