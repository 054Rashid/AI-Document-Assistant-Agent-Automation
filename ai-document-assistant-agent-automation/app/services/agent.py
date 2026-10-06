import json
from typing import Any

import requests
from langchain_core.tools import tool

from app.config import get_settings
from app.services.qdrant_store import SearchResult, QdrantStore
from app.services.rest_client import convert_currency


@tool
def search_documents(query: str) -> str:
    """Search the company documents for information relevant to the user's question."""
    results = QdrantStore().search(query, top_k=4)
    if not results:
        return "No matching document content was found."
    return json.dumps(
        [
            {
                "document": item.document,
                "chunk_id": item.chunk_id,
                "score": round(item.score, 4),
                "text": item.text,
            }
            for item in results
        ],
        ensure_ascii=False,
    )


@tool
def exchange_rate(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount between currencies using a public JSON REST API."""
    data = convert_currency(amount, from_currency, to_currency)
    return json.dumps(data)


def _tool_schema(tool_obj: Any) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool_obj.name,
            "description": tool_obj.description,
            "parameters": tool_obj.args_schema.model_json_schema(),
        },
    }


TOOLS = {
    search_documents.name: search_documents,
    exchange_rate.name: exchange_rate,
}
TOOL_SCHEMAS = [_tool_schema(tool_obj) for tool_obj in TOOLS.values()]


def _fallback_answer(query: str, results: list[SearchResult]) -> str:
    if not results:
        return "I couldn't find relevant information in the uploaded documents."
    context = "\n\n".join(
        f"[{item.document} | {item.chunk_id}]\n{item.text}" for item in results
    )
    return (
        "I am running in retrieval-only mode, so I am showing the most relevant "
        "document content instead of generating a new answer.\n\n"
        f"{context}"
    )


def run_agent(query: str) -> dict:
    settings = get_settings()
    retrieved: list[SearchResult] = QdrantStore().search(query, top_k=settings.top_k)

    if settings.llm_provider.lower() != "openai" or not settings.openai_api_key:
        return {
            "answer": _fallback_answer(query, retrieved),
            "mode": "retrieval-only",
            "tools_used": [],
            "sources": [r.__dict__ for r in retrieved],
        }

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    endpoint = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are a small company-document assistant. Use tools when useful. "
                "For policy questions, prefer the search_documents tool. "
                "For currency conversion, use the exchange_rate tool. "
                "Be clear and do not invent company policy."
            ),
        },
        {"role": "user", "content": query},
    ]
    tools_used: list[str] = []

    for _ in range(3):
        response = requests.post(
            endpoint,
            headers=headers,
            json={
                "model": settings.openai_model,
                "messages": messages,
                "tools": TOOL_SCHEMAS,
                "tool_choice": "auto",
                "temperature": 0.1,
            },
            timeout=60,
        )
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        messages.append(message)

        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            return {
                "answer": message.get("content", "").strip(),
                "mode": "agent",
                "tools_used": tools_used,
                "sources": [r.__dict__ for r in retrieved],
            }

        for call in tool_calls:
            name = call["function"]["name"]
            args = json.loads(call["function"].get("arguments") or "{}")
            tool_obj = TOOLS.get(name)
            if not tool_obj:
                result = "Unknown tool."
            else:
                result = tool_obj.invoke(args)
                tools_used.append(name)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result,
                }
            )

    return {
        "answer": "The agent reached its tool-call limit before producing an answer.",
        "mode": "agent",
        "tools_used": tools_used,
        "sources": [r.__dict__ for r in retrieved],
    }
