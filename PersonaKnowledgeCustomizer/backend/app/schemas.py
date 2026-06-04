from __future__ import annotations

from pydantic import BaseModel, Field


class KnowledgeItemInput(BaseModel):
    item_id: str | None = None
    title: str = Field(..., min_length=2, max_length=120)
    content: str = Field(..., min_length=4, max_length=5000)
    tags: list[str] = Field(default_factory=list)
    priority: int = Field(50, ge=1, le=100)


class KnowledgeUpsertRequest(BaseModel):
    items: list[KnowledgeItemInput]


class KnowledgeItemResponse(BaseModel):
    item_id: str
    title: str
    content: str
    tags: list[str]
    priority: int
    updated_at: str


class CustomAnswerRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    persona_name: str = Field("금융 리서치 봇")
    style: str = Field("차분하고 실행 중심")
    top_k: int = Field(3, ge=1, le=10)


class MatchedKnowledge(BaseModel):
    item_id: str
    title: str
    score: float


class CustomAnswerResponse(BaseModel):
    answer: str
    matched: list[MatchedKnowledge]


class HistoryItem(BaseModel):
    timestamp: str
    action: str
    payload: dict


class HistoryResponse(BaseModel):
    count: int
    items: list[HistoryItem]
