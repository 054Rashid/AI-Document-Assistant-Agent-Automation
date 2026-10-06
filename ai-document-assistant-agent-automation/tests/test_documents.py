from pathlib import Path

from app.services.documents import load_documents


def test_load_documents(tmp_path: Path):
    (tmp_path / "a.txt").write_text("Hello world", encoding="utf-8")
    documents = load_documents(str(tmp_path))
    assert documents == [("a.txt", "Hello world")]
