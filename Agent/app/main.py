from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.agent_service import QnaAgent
from app.auth_service import AuthService, AuthUser
from app.config import settings
from app.curriculum_service import CurriculumIndex
from app.ingest import run_ingestion
from app.multimodal_service import MultimodalService
from app.orchestration import AnswerOrchestrator
from app.query_router import QueryRouter
from app.rag_booster import RAGBooster
from app.rag_engine import RepoRAG
from app.rag_validation import RagValidationQueue
from app.schemas import (
    AskRequest,
    AskResponse,
    AuthResponse,
    HealthResponse,
    LoginRequest,
    MultimodalAskRequest,
    MultimodalAskResponse,
    OcrRequest,
    OcrResponse,
    RagValidationPendingResponse,
    RagValidationQueueRequest,
    RagValidationQueueResponse,
    RegisterRequest,
    ReindexResponse,
    SourceItem,
    SttRequest,
    SttResponse,
    TtsRequest,
    TtsResponse,
    UserProfileResponse,
    UserSettingsUpdateRequest,
)
from app.telemetry import TraceLogger
from app.user_store import build_user_store

app = FastAPI(title="Curriculum RAG Agent", version="2.0.0")
STATIC_DIR = Path(__file__).resolve().parent / "static"
bearer_scheme = HTTPBearer(auto_error=False)


def _new_rag() -> RepoRAG:
    return RepoRAG(
        db_path=settings.vector_db_path,
        collection_name=settings.vector_collection,
        embed_dim=settings.embedding_dim,
        embedding_provider=settings.embedding_provider,
        openai_api_key=settings.openai_api_key,
        openai_embedding_model=settings.openai_embedding_model,
    )


rag = _new_rag()
agent = QnaAgent()
curriculum = CurriculumIndex(repo_root=settings.repo_root)
router = QueryRouter(curriculum_index=curriculum)
validation_queue = RagValidationQueue(db_path=settings.vector_db_path)
orchestrator = AnswerOrchestrator(
    agent=agent,
    openai_api_key=settings.openai_api_key,
    openai_model=settings.openai_model,
)
trace_logger = TraceLogger(
    langsmith_enabled=settings.langsmith_tracing,
    langsmith_api_key=settings.langsmith_api_key,
    langsmith_project=settings.langsmith_project,
)

user_store_init = build_user_store(
    mode=settings.user_store_mode,
    vector_db_path=settings.vector_db_path,
    vector_collection=settings.user_vector_collection,
    qdrant_host=settings.qdrant_host,
    qdrant_port=settings.qdrant_port,
    qdrant_collection=settings.qdrant_user_collection,
    mariadb_url=settings.mariadb_url,
    mariadb_host=settings.mariadb_host,
    mariadb_port=settings.mariadb_port,
    mariadb_user=settings.mariadb_user,
    mariadb_password=settings.mariadb_password,
    mariadb_database=settings.mariadb_database,
)
user_store_warnings = list(user_store_init.warnings)
auth_service = AuthService(
    user_store=user_store_init.store,
    token_secret=settings.auth_secret,
    token_ttl_seconds=settings.auth_token_ttl_seconds,
)

multimodal = MultimodalService(
    openai_api_key=settings.openai_api_key,
    stt_model=settings.openai_stt_model,
    tts_model=settings.openai_tts_model,
    tts_voice=settings.openai_tts_voice,
    vision_model=settings.openai_vision_model,
    mock_fallback=settings.multimodal_mock_fallback,
    deepgram_api_key=settings.deepgram_api_key,
    deepgram_model=settings.deepgram_model,
    assemblyai_api_key=settings.assemblyai_api_key,
    elevenlabs_api_key=settings.elevenlabs_api_key,
    elevenlabs_voice_id=settings.elevenlabs_voice_id,
    elevenlabs_model_id=settings.elevenlabs_model_id,
    ocr_space_api_key=settings.ocr_space_api_key,
)

rag_booster = RAGBooster(
    cohere_api_key=settings.cohere_api_key,
    cohere_rerank_model=settings.cohere_rerank_model,
    tavily_api_key=settings.tavily_api_key,
    tavily_search_depth=settings.tavily_search_depth,
    tavily_topic=settings.tavily_topic,
    web_search_fallback_threshold=settings.web_search_fallback_threshold,
)


def _profile(user: AuthUser) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=user.user_id,
        username=user.username,
        full_name=user.full_name,
        settings=user.settings,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _resolve_user(
    credentials: HTTPAuthorizationCredentials | None,
    *,
    required: bool,
) -> AuthUser | None:
    if credentials is None:
        if required:
            raise HTTPException(status_code=401, detail="authorization required")
        return None

    token = (credentials.credentials or "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="invalid authorization token")
    try:
        return auth_service.authenticate_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthUser | None:
    return _resolve_user(credentials, required=False)


def get_current_user_required(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthUser:
    user = _resolve_user(credentials, required=True)
    assert user is not None
    return user


def _resolve_persona(user: AuthUser | None, payload: AskRequest) -> tuple[str, str | None]:
    if "persona_instruction" in payload.model_fields_set and payload.persona_instruction:
        return payload.persona_instruction.strip(), "request"

    if user:
        instruction = str(user.settings.get("persona_instruction", "")).strip()
        persona_name = str(user.settings.get("persona_name", "default")).strip() or "default"
        if instruction:
            return instruction, persona_name
        return "", persona_name

    return "", None


def _resolve_langsmith_flag(user: AuthUser | None, payload: AskRequest | None = None) -> bool:
    if payload and "enable_langsmith" in payload.model_fields_set and payload.enable_langsmith is not None:
        return bool(payload.enable_langsmith)

    if user and isinstance(user.settings.get("enable_langsmith"), bool):
        return bool(user.settings.get("enable_langsmith"))

    return settings.langsmith_tracing


def _as_source_items(sources: list[dict[str, Any]]) -> list[SourceItem]:
    output: list[SourceItem] = []
    for source in sources:
        source_type = str(source.get("source_type", "repo")).strip().lower()
        if source_type not in {"repo", "web"}:
            source_type = "repo"
        output.append(
            SourceItem(
                path=str(source["path"]),
                score=float(source["score"]),
                chunk=str(source["chunk"]),
                source_type=source_type,  # type: ignore[arg-type]
                provider=str(source.get("provider", "")) or None,
            )
        )
    return output


def _process_ask(payload: AskRequest, current_user: AuthUser | None) -> AskResponse:
    global rag

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    routed = router.route(question)

    if "top_k" in payload.model_fields_set:
        top_k = int(payload.top_k)
    elif current_user:
        top_k = int(current_user.settings.get("default_top_k", settings.default_top_k))
    else:
        top_k = int(settings.default_top_k)
    top_k = max(1, min(20, top_k))

    if "orchestrator" in payload.model_fields_set:
        requested_orchestrator = payload.orchestrator
    elif current_user:
        requested_orchestrator = str(current_user.settings.get("preferred_orchestrator", settings.default_orchestrator))
    else:
        requested_orchestrator = settings.default_orchestrator

    requested_orchestrator = str(requested_orchestrator).strip().lower()
    if requested_orchestrator not in {"native", "langchain", "langgraph"}:
        requested_orchestrator = payload.orchestrator

    if "use_web_search" in payload.model_fields_set:
        use_web_search = bool(payload.use_web_search)
    elif current_user:
        use_web_search = bool(current_user.settings.get("default_use_web_search", False))
    else:
        use_web_search = False

    if "use_rerank" in payload.model_fields_set:
        use_rerank = bool(payload.use_rerank)
    elif current_user:
        use_rerank = bool(current_user.settings.get("default_use_rerank", True))
    else:
        use_rerank = True

    persona_instruction, persona_name = _resolve_persona(current_user, payload)

    if routed.mode == "concept_definition" and routed.concept:
        answer = curriculum.answer_concept_definition(routed.concept)
        if answer:
            resp = AskResponse(
                answer=answer,
                sources=[
                    SourceItem(
                        path="curriculum_index.csv",
                        score=1.0,
                        chunk="개념형 질문은 구조화 Glossary + curriculum_index.csv 범위 매핑으로 응답합니다.",
                    )
                ],
                mode="concept_definition",
                matched_subject=routed.subject_name,
                matched_class_id=routed.class_id,
                selected_orchestrator="native",
                persona_name=persona_name,
                retrieval_diagnostics={"strategy": "concept_definition"},
            )
            resp.trace_id = trace_logger.log_event(
                event="ask",
                user_id=current_user.user_id if current_user else None,
                inputs={"question": question, "mode": resp.mode},
                outputs={"answer": resp.answer, "sources": [s.model_dump() for s in resp.sources]},
                metadata={"selected_orchestrator": resp.selected_orchestrator},
                enable_langsmith=_resolve_langsmith_flag(current_user, payload),
            )
            return resp

    if routed.mode == "subject_range" and routed.subject_name:
        answer = curriculum.answer_subject_range(routed.subject_name)
        if answer:
            resp = AskResponse(
                answer=answer,
                sources=[
                    SourceItem(
                        path="curriculum_index.csv",
                        score=1.0,
                        chunk="과목 범위 매핑은 curriculum_index.csv의 class/day/subject_name 컬럼 기준으로 계산됩니다.",
                    )
                ],
                mode="subject_range",
                matched_subject=routed.subject_name,
                matched_class_id=routed.class_id,
                selected_orchestrator="native",
                persona_name=persona_name,
                retrieval_diagnostics={"strategy": "subject_range"},
            )
            resp.trace_id = trace_logger.log_event(
                event="ask",
                user_id=current_user.user_id if current_user else None,
                inputs={"question": question, "mode": resp.mode},
                outputs={"answer": resp.answer, "sources": [s.model_dump() for s in resp.sources]},
                metadata={"selected_orchestrator": resp.selected_orchestrator},
                enable_langsmith=_resolve_langsmith_flag(current_user, payload),
            )
            return resp

    if routed.class_id:
        class_sources = curriculum.class_local_search(
            class_id=routed.class_id,
            question=question,
            top_k=top_k,
        )
        if class_sources:
            class_subject = routed.subject_name or curriculum.class_subject(routed.class_id)
            class_answer = curriculum.answer_class_scoped(
                class_id=routed.class_id,
                question=question,
                sources=class_sources,
            )
            resp = AskResponse(
                answer=class_answer or "",
                sources=_as_source_items(class_sources),
                mode="class_scoped",
                matched_subject=class_subject,
                matched_class_id=routed.class_id,
                selected_orchestrator="native",
                persona_name=persona_name,
                retrieval_diagnostics={"strategy": "class_scoped"},
            )
            resp.trace_id = trace_logger.log_event(
                event="ask",
                user_id=current_user.user_id if current_user else None,
                inputs={"question": question, "mode": resp.mode},
                outputs={"answer": resp.answer, "sources": [s.model_dump() for s in resp.sources]},
                metadata={"selected_orchestrator": resp.selected_orchestrator},
                enable_langsmith=_resolve_langsmith_flag(current_user, payload),
            )
            return resp

    if rag.count() == 0:
        run_ingestion(
            repo_root=str(settings.repo_root),
            db_path=str(settings.vector_db_path),
            collection=settings.vector_collection,
            embed_dim=settings.embedding_dim,
            embedding_provider=settings.embedding_provider,
            openai_api_key=settings.openai_api_key,
            openai_embedding_model=settings.openai_embedding_model,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            force=False,
            skip_if_exists=False,
        )
        rag = _new_rag()

    preferred_dirs = curriculum.subject_directory_hints(routed.subject_name)
    sources = rag.query(
        question=question,
        top_k=top_k,
        class_hint=routed.class_id,
        preferred_dirs=preferred_dirs,
        query_expansions=routed.query_expansions or [],
    )
    if not sources and routed.query_expansions:
        sources = rag.query(
            question=question,
            top_k=top_k,
            class_hint=routed.class_id,
            preferred_dirs=preferred_dirs,
            query_expansions=routed.query_expansions,
        )

    boosted = rag_booster.enhance(
        question=question,
        local_sources=sources,
        top_k=top_k,
        use_web_search=use_web_search,
        web_search_top_k=payload.web_search_top_k,
        use_rerank=use_rerank,
        rerank_provider=payload.rerank_provider,
    )
    sources = boosted.sources

    orchestration = orchestrator.answer(
        question=question,
        sources=sources,
        use_llm=payload.use_llm,
        requested_mode=requested_orchestrator,
        persona_instruction=persona_instruction,
    )

    resp = AskResponse(
        answer=orchestration.answer,
        sources=_as_source_items(sources),
        mode="rag",
        matched_subject=routed.subject_name,
        matched_class_id=routed.class_id,
        selected_orchestrator=orchestration.selected_mode,
        orchestrator_note=orchestration.note,
        persona_name=persona_name,
        retrieval_diagnostics=boosted.diagnostics,
    )

    resp.trace_id = trace_logger.log_event(
        event="ask",
        user_id=current_user.user_id if current_user else None,
        inputs={
            "question": question,
            "mode": "rag",
            "requested_orchestrator": requested_orchestrator,
            "top_k": top_k,
            "use_web_search": use_web_search,
            "use_rerank": use_rerank,
            "rerank_provider": payload.rerank_provider,
        },
        outputs={
            "answer": resp.answer,
            "source_count": len(resp.sources),
            "selected_orchestrator": resp.selected_orchestrator,
        },
        metadata={
            "orchestrator_note": resp.orchestrator_note,
            "matched_subject": resp.matched_subject,
            "matched_class_id": resp.matched_class_id,
            "retrieval_diagnostics": resp.retrieval_diagnostics,
        },
        enable_langsmith=_resolve_langsmith_flag(current_user, payload),
    )
    return resp


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    third_party = {}
    third_party.update(multimodal.provider_availability)
    third_party.update(rag_booster.capabilities)
    return HealthResponse(
        status="ok",
        collection=rag.collection_name,
        documents=rag.count(),
        curriculum_index=curriculum.index_path,
        pending_validations=validation_queue.pending_count(),
        user_store=auth_service.backend,
        users=auth_service.count_users(),
        orchestrators=orchestrator.availability,
        langsmith_ready=trace_logger.langsmith_ready,
        embedding_provider=rag.embedding_provider,
        third_party=third_party,
    )


@app.get("/v1/orchestrators")
def get_orchestrators() -> dict[str, Any]:
    return {
        "availability": orchestrator.availability,
        "default": settings.default_orchestrator,
    }


@app.get("/v1/bootstrap")
def bootstrap() -> dict[str, Any]:
    return {
        "settings": settings.export_public(),
        "orchestrators": orchestrator.availability,
        "user_store": auth_service.backend,
        "user_store_warnings": user_store_warnings,
        "multimodal": {
            "openai_available": multimodal.has_openai,
            "mock_fallback": settings.multimodal_mock_fallback,
            "providers": multimodal.provider_availability,
        },
        "rag_booster": rag_booster.capabilities,
    }


@app.post("/v1/reindex", response_model=ReindexResponse)
def reindex(force: bool = True) -> ReindexResponse:
    global rag
    indexed_files, indexed_chunks, collection = run_ingestion(
        repo_root=str(settings.repo_root),
        db_path=str(settings.vector_db_path),
        collection=settings.vector_collection,
        embed_dim=settings.embedding_dim,
        embedding_provider=settings.embedding_provider,
        openai_api_key=settings.openai_api_key,
        openai_embedding_model=settings.openai_embedding_model,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        force=force,
        skip_if_exists=False,
    )
    rag = _new_rag()
    curriculum.reload()
    validation_queue.process_on_reindex(rag)
    return ReindexResponse(
        indexed_files=indexed_files,
        indexed_chunks=indexed_chunks,
        collection=collection,
    )


@app.get("/v1/rag-validation/pending", response_model=RagValidationPendingResponse)
def rag_validation_pending() -> RagValidationPendingResponse:
    return RagValidationPendingResponse(pending_count=validation_queue.pending_count())


@app.post("/v1/rag-validation/queue", response_model=RagValidationQueueResponse)
def rag_validation_queue(payload: RagValidationQueueRequest) -> RagValidationQueueResponse:
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    review_id, pending_count = validation_queue.enqueue(payload.model_dump())
    return RagValidationQueueResponse(review_id=review_id, pending_count=pending_count)


@app.post("/v1/auth/register", response_model=AuthResponse)
def auth_register(payload: RegisterRequest) -> AuthResponse:
    try:
        token, user = auth_service.register(
            username=payload.username,
            password=payload.password,
            full_name=payload.full_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AuthResponse(access_token=token, profile=_profile(user))


@app.post("/v1/auth/login", response_model=AuthResponse)
def auth_login(payload: LoginRequest) -> AuthResponse:
    try:
        token, user = auth_service.login(username=payload.username, password=payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return AuthResponse(access_token=token, profile=_profile(user))


@app.get("/v1/auth/me", response_model=UserProfileResponse)
def auth_me(current_user: AuthUser = Depends(get_current_user_required)) -> UserProfileResponse:
    return _profile(current_user)


@app.put("/v1/auth/settings", response_model=UserProfileResponse)
def auth_settings(
    payload: UserSettingsUpdateRequest,
    current_user: AuthUser = Depends(get_current_user_required),
) -> UserProfileResponse:
    updates = payload.model_dump(exclude_none=True)
    try:
        updated = auth_service.update_settings(user_id=current_user.user_id, updates=updates)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _profile(updated)


@app.post("/v1/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    current_user: AuthUser | None = Depends(get_current_user_optional),
) -> AskResponse:
    return _process_ask(payload=payload, current_user=current_user)


@app.post("/v1/stt", response_model=SttResponse)
def stt(
    payload: SttRequest,
    current_user: AuthUser | None = Depends(get_current_user_optional),
) -> SttResponse:
    try:
        result = multimodal.transcribe(
            audio_base64=payload.audio_base64,
            mime_type=payload.mime_type,
            language=payload.language,
            provider=payload.provider,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    trace_id = trace_logger.log_event(
        event="stt",
        user_id=current_user.user_id if current_user else None,
        inputs={
            "provider": payload.provider,
            "mime_type": payload.mime_type,
            "language": payload.language,
            "audio_base64_length": len(payload.audio_base64),
        },
        outputs={"provider": result.provider, "text_preview": result.text[:200]},
        metadata={},
        enable_langsmith=_resolve_langsmith_flag(current_user),
    )
    return SttResponse(text=result.text, provider=result.provider, note=result.note, trace_id=trace_id)


@app.post("/v1/tts", response_model=TtsResponse)
def tts(
    payload: TtsRequest,
    current_user: AuthUser | None = Depends(get_current_user_optional),
) -> TtsResponse:
    try:
        result = multimodal.synthesize(
            text=payload.text,
            voice=payload.voice,
            provider=payload.provider,
            audio_format=payload.audio_format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    trace_id = trace_logger.log_event(
        event="tts",
        user_id=current_user.user_id if current_user else None,
        inputs={
            "provider": payload.provider,
            "voice": payload.voice,
            "format": payload.audio_format,
            "text_length": len(payload.text),
        },
        outputs={"provider": result.provider, "format": result.format, "audio_base64_length": len(result.audio_base64)},
        metadata={},
        enable_langsmith=_resolve_langsmith_flag(current_user),
    )
    return TtsResponse(
        audio_base64=result.audio_base64,
        provider=result.provider,
        format=result.format,
        note=result.note,
        trace_id=trace_id,
    )


@app.post("/v1/ocr", response_model=OcrResponse)
def ocr(
    payload: OcrRequest,
    current_user: AuthUser | None = Depends(get_current_user_optional),
) -> OcrResponse:
    try:
        result = multimodal.ocr(
            image_base64=payload.image_base64,
            mime_type=payload.mime_type,
            prompt=payload.prompt,
            provider=payload.provider,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    trace_id = trace_logger.log_event(
        event="ocr",
        user_id=current_user.user_id if current_user else None,
        inputs={
            "provider": payload.provider,
            "mime_type": payload.mime_type,
            "image_base64_length": len(payload.image_base64),
        },
        outputs={"provider": result.provider, "text_preview": result.text[:200]},
        metadata={},
        enable_langsmith=_resolve_langsmith_flag(current_user),
    )
    return OcrResponse(text=result.text, provider=result.provider, note=result.note, trace_id=trace_id)


@app.post("/v1/multimodal/ask", response_model=MultimodalAskResponse)
def multimodal_ask(
    payload: MultimodalAskRequest,
    current_user: AuthUser | None = Depends(get_current_user_optional),
) -> MultimodalAskResponse:
    transcript: str | None = None
    ocr_text: str | None = None

    if payload.audio_base64:
        try:
            stt_result = multimodal.transcribe(
                audio_base64=payload.audio_base64,
                mime_type=payload.audio_mime_type,
                language=payload.language,
                provider="auto",
            )
            transcript = stt_result.text
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"audio processing failed: {exc}") from exc

    if payload.image_base64:
        try:
            ocr_result = multimodal.ocr(
                image_base64=payload.image_base64,
                mime_type=payload.image_mime_type,
                prompt=payload.ocr_prompt,
                provider="auto",
            )
            ocr_text = ocr_result.text
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"image processing failed: {exc}") from exc

    blocks: list[str] = []
    if payload.question and payload.question.strip():
        blocks.append(payload.question.strip())
    if transcript:
        blocks.append(f"[음성 전사]\n{transcript}")
    if ocr_text:
        blocks.append(f"[이미지 OCR]\n{ocr_text}")

    composed_question = "\n\n".join(blocks).strip()
    ask_payload = AskRequest(
        question=composed_question,
        top_k=payload.top_k,
        use_llm=payload.use_llm,
        orchestrator=payload.orchestrator,
        persona_instruction=payload.persona_instruction,
        enable_langsmith=payload.enable_langsmith,
        use_web_search=payload.use_web_search,
        web_search_top_k=payload.web_search_top_k,
        use_rerank=payload.use_rerank,
        rerank_provider=payload.rerank_provider,
    )
    ask_response = _process_ask(payload=ask_payload, current_user=current_user)

    return MultimodalAskResponse(
        composed_question=composed_question,
        transcript=transcript,
        ocr_text=ocr_text,
        answer=ask_response.answer,
        sources=ask_response.sources,
        mode=ask_response.mode,
        matched_subject=ask_response.matched_subject,
        matched_class_id=ask_response.matched_class_id,
        selected_orchestrator=ask_response.selected_orchestrator,
        orchestrator_note=ask_response.orchestrator_note,
        persona_name=ask_response.persona_name,
        trace_id=ask_response.trace_id,
        retrieval_diagnostics=ask_response.retrieval_diagnostics,
    )
