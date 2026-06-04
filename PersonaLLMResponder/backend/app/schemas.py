from __future__ import annotations

from pydantic import BaseModel, Field


class PersonaUpsertRequest(BaseModel):
    persona_id: str | None = None
    name: str = Field(..., min_length=2, max_length=40)
    role: str = Field("금융 상담 분석가", max_length=80)
    tone: str = Field("차분하고 근거 중심의")
    speaking_rules: list[str] = Field(default_factory=list)
    forbidden_topics: list[str] = Field(default_factory=list)
    greeting: str = Field("안녕하세요. 금융 의사결정에 필요한 핵심 근거부터 정리해드리겠습니다.")


class PersonaResponse(BaseModel):
    persona_id: str
    name: str
    role: str
    tone: str
    speaking_rules: list[str]
    forbidden_topics: list[str]
    greeting: str
    updated_at: str


class PersonaAnswerRequest(BaseModel):
    persona_id: str = Field(..., min_length=4)
    question: str = Field(..., min_length=2, max_length=800)
    context: str = Field("", max_length=1500)
    use_llm: bool = True


class PersonaAnswerResponse(BaseModel):
    persona_id: str
    provider: str
    answer: str
    prompt_preview: str


class HistoryItem(BaseModel):
    timestamp: str
    action: str
    payload: dict


class HistoryResponse(BaseModel):
    count: int
    items: list[HistoryItem]
