from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "project002")
    project_name: str = os.getenv("PROJECT_NAME", "금융 상품 상담 에이전트")
    project_track: str = os.getenv("PROJECT_TRACK", "금융-프로젝트-B")
    project_topic: str = os.getenv("PROJECT_TOPIC", "금융 상품 상담 에이전트")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data")).resolve()

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()
