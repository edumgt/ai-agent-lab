from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "project003")
    project_name: str = os.getenv("PROJECT_NAME", "금융 지식베이스 커스터마이저")
    project_track: str = os.getenv("PROJECT_TRACK", "금융-프로젝트-C")
    project_topic: str = os.getenv("PROJECT_TOPIC", "금융 지식베이스 커스터마이저")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data")).resolve()


settings = Settings()
