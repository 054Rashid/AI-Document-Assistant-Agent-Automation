from app.config import get_settings
from app.services.agent import _fallback_answer
from app.services.qdrant_store import SearchResult


def test_fallback_answer_is_honest(monkeypatch):
    monkeypatch.setattr(get_settings(), "llm_provider", "none")
    results = [SearchResult("policy.txt", "chunk-1", 0.9, "Submit the request to IT.")]
    answer = _fallback_answer("How do I get IT help?", results)
    assert "retrieval-only mode" in answer
    assert "Submit the request to IT." in answer
