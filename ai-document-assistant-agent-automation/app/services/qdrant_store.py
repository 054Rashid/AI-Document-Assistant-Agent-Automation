from dataclasses import dataclass
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import get_settings
from app.services.embeddings import embed_query, embed_texts


@dataclass
class SearchResult:
    document: str
    chunk_id: str
    score: float
    text: str


class QdrantStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection
        self.dimension = settings.embedding_dimension

    def ensure_collection(self) -> None:
        collections = {c.name for c in self.client.get_collections().collections}
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=self.dimension,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(self, records: list[dict]) -> int:
        self.ensure_collection()
        texts = [record["text"] for record in records]
        vectors = embed_texts(texts)
        points = []
        for record, vector in zip(records, vectors):
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        "document": record["document"],
                        "chunk_id": record["chunk_id"],
                        "text": record["text"],
                    },
                )
            )
        if points:
            self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    def search(self, query: str, top_k: int | None = None) -> list[SearchResult]:
        settings = get_settings()
        self.ensure_collection()
        vector = embed_query(query)
        hits = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=top_k or settings.top_k,
            with_payload=True,
        ).points
        return [
            SearchResult(
                document=hit.payload.get("document", ""),
                chunk_id=hit.payload.get("chunk_id", ""),
                score=float(hit.score),
                text=hit.payload.get("text", ""),
            )
            for hit in hits
        ]
