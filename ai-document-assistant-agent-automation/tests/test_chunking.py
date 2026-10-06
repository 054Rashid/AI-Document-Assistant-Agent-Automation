from app.services.chunking import split_text


def test_split_text_returns_non_empty_chunks():
    text = "This is a sentence. " * 80
    chunks = split_text(text)
    assert chunks
    assert all(chunk.strip() for chunk in chunks)
