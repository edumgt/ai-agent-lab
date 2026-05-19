from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class Settings:
    def __init__(self) -> None:
        self.repo_root = Path(os.getenv("REPO_ROOT", "/srv/repo")).resolve()
        self.vector_db_path = Path(os.getenv("VECTOR_DB_PATH", "/srv/vector_db")).resolve()
        self.vector_collection = os.getenv("VECTOR_COLLECTION", "curriculum_repo")
        self.embedding_dim = int(os.getenv("EMBEDDING_DIM", "1024"))
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()
        self.openai_embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "900"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))
        self.default_top_k = int(os.getenv("DEFAULT_TOP_K", "6"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.default_orchestrator = os.getenv("DEFAULT_ORCHESTRATOR", "native").strip().lower()

        # Authentication / user profile
        self.auth_secret = os.getenv("AUTH_SECRET", "change-me-in-production")
        self.auth_token_ttl_seconds = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", str(60 * 60 * 24)))

        # User store selection:
        # - auto: try vector -> mariadb -> memory
        # - vector: use ChromaDB collection
        # - mariadb: use MariaDB
        # - memory: process-local fallback
        self.user_store_mode = os.getenv("USER_STORE_MODE", "auto").strip().lower()
        self.user_vector_collection = os.getenv("USER_VECTOR_COLLECTION", "agent_users")

        self.qdrant_host = os.getenv("QDRANT_HOST", "qdrant").strip()
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.qdrant_user_collection = os.getenv("QDRANT_USER_COLLECTION", "agent_users")

        self.mariadb_host = os.getenv("MARIADB_HOST", "mariadb").strip()
        self.mariadb_port = int(os.getenv("MARIADB_PORT", "3306"))
        self.mariadb_user = os.getenv("MARIADB_USER", "agent")
        self.mariadb_password = os.getenv("MARIADB_PASSWORD", "agentpass")
        self.mariadb_database = os.getenv("MARIADB_DATABASE", "agentdb")
        self.mariadb_url = os.getenv("MARIADB_URL", "").strip()

        # LangSmith
        self.langsmith_tracing = self._as_bool(os.getenv("LANGSMITH_TRACING", "false"))
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY", "").strip()
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "curriculum-agent")

        # Multimodal defaults
        self.openai_stt_model = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
        self.openai_tts_model = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
        self.openai_tts_voice = os.getenv("OPENAI_TTS_VOICE", "alloy")
        self.openai_vision_model = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")
        self.multimodal_mock_fallback = self._as_bool(os.getenv("MULTIMODAL_MOCK_FALLBACK", "true"))

        # Third-party practical integrations
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY", "").strip()
        self.deepgram_model = os.getenv("DEEPGRAM_MODEL", "nova-2")
        self.assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
        self.elevenlabs_model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
        self.ocr_space_api_key = os.getenv("OCR_SPACE_API_KEY", "").strip()

        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()
        self.tavily_search_depth = os.getenv("TAVILY_SEARCH_DEPTH", "advanced").strip().lower()
        self.tavily_topic = os.getenv("TAVILY_TOPIC", "general").strip().lower()

        self.cohere_api_key = os.getenv("COHERE_API_KEY", "").strip()
        self.cohere_rerank_model = os.getenv("COHERE_RERANK_MODEL", "rerank-v3.5")
        self.web_search_fallback_threshold = float(os.getenv("WEB_SEARCH_FALLBACK_THRESHOLD", "0.34"))

    @staticmethod
    def _as_bool(value: str | bool | None) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

    def export_public(self) -> dict[str, Any]:
        return {
            "repo_root": str(self.repo_root),
            "vector_collection": self.vector_collection,
            "default_orchestrator": self.default_orchestrator,
            "user_store_mode": self.user_store_mode,
            "langsmith_tracing": self.langsmith_tracing,
            "openai_model": self.openai_model,
            "embedding_provider": self.embedding_provider,
        }


settings = Settings()
