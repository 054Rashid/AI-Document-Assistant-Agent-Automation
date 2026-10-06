from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    directory: str = Field(default="data/documents")


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=4, ge=1, le=10)


class AgentRequest(BaseModel):
    query: str = Field(min_length=2)
