from app.services.chunking import split_text
from app.services.documents import load_documents
from app.services.qdrant_store import QdrantStore


def ingest_directory(directory: str) -> dict:
    documents = load_documents(directory)
    records: list[dict] = []

    for document_name, text in documents:
        chunks = split_text(text)
        for index, chunk in enumerate(chunks, start=1):
            records.append(
                {
                    "document": document_name,
                    "chunk_id": f"chunk-{index}",
                    "text": chunk,
                }
            )

    stored = QdrantStore().upsert(records)
    return {
        "documents_read": len(documents),
        "chunks_created": len(records),
        "chunks_stored": stored,
    }
