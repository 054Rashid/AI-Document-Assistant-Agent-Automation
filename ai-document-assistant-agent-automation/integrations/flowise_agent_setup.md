# Flowise agent setup (learning version)

This project keeps the main business logic in Python and uses Flowise as a visual way to understand agent orchestration.

Create a simple Flowise chatflow with these pieces:

1. Chat Input
2. Agent / Conversational Agent
3. LLM node
4. Custom Tool for document search
5. HTTP tool pointing to `POST /api/search`
6. Chat Output

For the HTTP tool, send JSON like:

```json
{
  "query": "{{question}}",
  "top_k": 4
}
```

The useful learning point is the separation of responsibilities:

- Flowise: visual agent workflow
- FastAPI: Python backend
- Qdrant: vector search
- Sentence Transformers: embeddings

This file is a setup guide rather than a version-specific Flowise export because Flowise export formats can change between releases.
