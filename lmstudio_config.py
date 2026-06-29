# 이 파일은 www.edumgt.co.kr 의 에듀엠지티에 저작권이 있습니다
"""
LM Studio 공통 클라이언트 설정
==============================
LM Studio 는 로컬에서 GGUF 모델을 실행하며 OpenAI 호환 API 를 제공합니다.
기본 주소: http://localhost:1234/v1

사용 방법:
    from lmstudio_config import call_lm, client, LM_MODEL

환경 변수 (선택):
    LM_STUDIO_URL    기본값: http://localhost:1234/v1
    LM_STUDIO_API_KEY 기본값: lm-studio
    LM_STUDIO_MODEL  기본값: local-model (LM Studio 에서 로드한 모델명)
"""
from __future__ import annotations

import os

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
LM_MODEL = os.getenv("LM_STUDIO_MODEL", "local-model")

try:
    from openai import OpenAI as _OpenAI
    client = _OpenAI(base_url=LM_STUDIO_URL, api_key=LM_STUDIO_API_KEY)
    LM_STUDIO_AVAILABLE = True
except Exception:
    client = None
    LM_STUDIO_AVAILABLE = False


def call_lm(
    messages: list[dict],
    *,
    temperature: float = 0.7,
    max_tokens: int = 512,
    model: str | None = None,
) -> str | None:
    """
    LM Studio Chat Completions 호출.
    LM Studio 가 실행 중이지 않거나 패키지가 없으면 None 반환.

    Args:
        messages: [{"role": "user", "content": "..."}, ...] 형식 메시지 목록
        temperature: 생성 다양성 (0.0~2.0)
        max_tokens: 최대 생성 토큰 수
        model: 모델명 (None 이면 LM_MODEL 환경변수 사용)

    Returns:
        생성된 텍스트 또는 None (연결 실패 시)
    """
    if not LM_STUDIO_AVAILABLE or client is None:
        return None
    try:
        response = client.chat.completions.create(
            model=model or LM_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as exc:
        print(f"[LM Studio] 연결 실패 — LM Studio 가 실행 중인지 확인하세요: {exc}")
        return None


def call_lm_simple(prompt: str, *, system: str = "당신은 도움이 되는 한국어 AI 어시스턴트입니다.", **kwargs) -> str | None:
    """단일 사용자 메시지로 LM Studio 를 호출하는 간편 함수."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    return call_lm(messages, **kwargs)


def check_connection() -> bool:
    """LM Studio 연결 상태 확인."""
    result = call_lm_simple("안녕하세요. 연결 확인 중입니다. '연결됨'이라고만 답해주세요.", max_tokens=20)
    return result is not None
