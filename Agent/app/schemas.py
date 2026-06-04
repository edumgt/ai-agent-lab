from __future__ import annotations

from typing import Any, List, Literal

from pydantic import BaseModel, Field, model_validator


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, description="질문")
    top_k: int = Field(6, ge=1, le=20)
    use_llm: bool = Field(True, description="OPENAI_API_KEY가 있으면 LLM 답변 생성")
    orchestrator: Literal["native", "langchain", "langgraph"] = Field("native")
    persona_instruction: str | None = Field(None, description="요청 단위 페르소나 지시")
    enable_langsmith: bool | None = Field(None, description="요청 단위 LangSmith trace 활성화")
    use_web_search: bool = Field(False, description="Tavily 웹 검색 결과를 RAG에 병합")
    web_search_top_k: int = Field(3, ge=1, le=10, description="웹 검색 결과 개수")
    use_rerank: bool = Field(True, description="리랭킹 사용")
    rerank_provider: Literal["auto", "cohere", "lexical", "none"] = Field("auto")


class SourceItem(BaseModel):
    path: str
    score: float
    chunk: str
    source_type: Literal["repo", "web"] = "repo"
    provider: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    mode: str = "rag"
    matched_subject: str | None = None
    matched_class_id: str | None = None
    selected_orchestrator: str = "native"
    orchestrator_note: str = ""
    persona_name: str | None = None
    trace_id: str | None = None
    retrieval_diagnostics: dict[str, Any] = Field(default_factory=dict)


class ReindexResponse(BaseModel):
    indexed_files: int
    indexed_chunks: int
    collection: str


class RagValidationQueueRequest(BaseModel):
    question: str = Field(..., min_length=2, description="검증이 필요한 질문")
    answer: str = Field("", description="사용자에게 제공된 기존 답변")
    sources: List[SourceItem] = Field(default_factory=list)
    mode: str = Field("rag")
    matched_subject: str | None = None
    matched_class_id: str | None = None
    note: str = Field("", max_length=500)
    top_k: int = Field(6, ge=1, le=20)
    use_llm: bool | None = None


class RagValidationQueueResponse(BaseModel):
    review_id: str
    pending_count: int


class RagValidationPendingResponse(BaseModel):
    pending_count: int


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field("", max_length=80)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)


class UserSettingsUpdateRequest(BaseModel):
    persona_name: str | None = Field(None, max_length=64)
    persona_instruction: str | None = Field(None, max_length=1000)
    preferred_orchestrator: Literal["native", "langchain", "langgraph"] | None = None
    default_top_k: int | None = Field(None, ge=1, le=20)
    default_use_web_search: bool | None = None
    default_use_rerank: bool | None = None
    enable_langsmith: bool | None = None
    env_overrides: dict[str, Any] | None = None


class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    full_name: str
    settings: dict[str, Any]
    created_at: str
    updated_at: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile: UserProfileResponse


class SttRequest(BaseModel):
    audio_base64: str = Field(..., min_length=8)
    mime_type: str = Field("audio/wav")
    language: str = Field("ko")
    provider: Literal["auto", "openai", "deepgram", "assemblyai"] = Field("auto")


class SttResponse(BaseModel):
    text: str
    provider: str
    note: str = ""
    trace_id: str | None = None


class TtsRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000)
    voice: str | None = None
    provider: Literal["auto", "openai", "elevenlabs"] = Field("auto")
    audio_format: Literal["wav", "mp3"] = Field("wav")


class TtsResponse(BaseModel):
    audio_base64: str
    provider: str
    format: str = "wav"
    note: str = ""
    trace_id: str | None = None


class OcrRequest(BaseModel):
    image_base64: str = Field(..., min_length=8)
    mime_type: str = Field("image/png")
    prompt: str = Field("이미지 안 텍스트를 OCR 결과로 정리해 주세요.", max_length=500)
    provider: Literal["auto", "openai", "ocr_space"] = Field("auto")


class OcrResponse(BaseModel):
    text: str
    provider: str
    note: str = ""
    trace_id: str | None = None


class MultimodalAskRequest(BaseModel):
    question: str | None = Field(None, description="텍스트 질문")
    audio_base64: str | None = Field(None, description="STT할 오디오")
    audio_mime_type: str = Field("audio/wav")
    image_base64: str | None = Field(None, description="OCR할 이미지")
    image_mime_type: str = Field("image/png")
    ocr_prompt: str = Field("이미지 안 텍스트를 OCR 결과로 정리해 주세요.", max_length=500)
    language: str = Field("ko")
    top_k: int = Field(6, ge=1, le=20)
    use_llm: bool = Field(True)
    orchestrator: Literal["native", "langchain", "langgraph"] = Field("native")
    persona_instruction: str | None = Field(None)
    enable_langsmith: bool | None = Field(None)
    use_web_search: bool = Field(False)
    web_search_top_k: int = Field(3, ge=1, le=10)
    use_rerank: bool = Field(True)
    rerank_provider: Literal["auto", "cohere", "lexical", "none"] = Field("auto")

    @model_validator(mode="after")
    def _validate_inputs(self) -> "MultimodalAskRequest":
        if not (self.question and self.question.strip()) and not self.audio_base64 and not self.image_base64:
            raise ValueError("one of question, audio_base64, image_base64 is required")
        return self


class MultimodalAskResponse(BaseModel):
    composed_question: str
    transcript: str | None = None
    ocr_text: str | None = None
    answer: str
    sources: List[SourceItem]
    mode: str = "rag"
    matched_subject: str | None = None
    matched_class_id: str | None = None
    selected_orchestrator: str = "native"
    orchestrator_note: str = ""
    persona_name: str | None = None
    trace_id: str | None = None
    retrieval_diagnostics: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    collection: str
    documents: int
    curriculum_index: str
    pending_validations: int
    user_store: str
    users: int
    orchestrators: dict[str, bool]
    langsmith_ready: bool
    embedding_provider: str
    third_party: dict[str, bool]
