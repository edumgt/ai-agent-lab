from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path, default: list[dict]) -> list[dict]:
    if not path.exists():
        return list(default)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return list(default)
    if not isinstance(raw, list):
        return list(default)
    return [row for row in raw if isinstance(row, dict)]


def _save_json(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def append_history(history_file: Path, action: str, payload: dict) -> None:
    history_file.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": _now_iso(), "action": action, "payload": payload}
    with history_file.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_recent(history_file: Path, limit: int = 30) -> list[dict]:
    if not history_file.exists():
        return []
    rows: list[dict] = []
    for line in history_file.read_text(encoding="utf-8").splitlines()[-max(1, limit):]:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def list_personas(personas_file: Path) -> list[dict]:
    rows = _load_json(personas_file, default=[])
    rows.sort(key=lambda row: str(row.get("updated_at", "")), reverse=True)
    return rows


def get_persona(personas_file: Path, persona_id: str) -> dict | None:
    for row in _load_json(personas_file, default=[]):
        if str(row.get("persona_id", "")) == persona_id:
            return row
    return None


def upsert_persona(personas_file: Path, payload: dict) -> dict:
    rows = _load_json(personas_file, default=[])
    persona_id = str(payload.get("persona_id") or "").strip() or f"persona_{uuid.uuid4().hex[:10]}"

    record = {
        "persona_id": persona_id,
        "name": str(payload.get("name", "")).strip(),
        "role": str(payload.get("role", "금융 상담 분석가")).strip(),
        "tone": str(payload.get("tone", "차분하고 근거 중심의")).strip(),
        "speaking_rules": [str(v).strip() for v in payload.get("speaking_rules", []) if str(v).strip()],
        "forbidden_topics": [str(v).strip() for v in payload.get("forbidden_topics", []) if str(v).strip()],
        "greeting": str(payload.get("greeting", "")).strip(),
        "updated_at": _now_iso(),
    }

    updated = False
    for idx, row in enumerate(rows):
        if str(row.get("persona_id", "")) == persona_id:
            rows[idx] = record
            updated = True
            break
    if not updated:
        rows.append(record)

    _save_json(personas_file, rows)
    return record


def build_prompt(persona: dict, question: str, context: str) -> str:
    rules = "\n".join(f"- {r}" for r in persona.get("speaking_rules", [])) or "- 핵심부터 간결하게 설명"
    forbidden = ", ".join(persona.get("forbidden_topics", [])) or "없음"
    return (
        f"역할: {persona.get('role','금융 상담 분석가')}\n"
        f"이름: {persona.get('name','PERSONA')}\n"
        f"톤: {persona.get('tone','차분하고 근거 중심의')}\n"
        f"말하기 규칙:\n{rules}\n"
        f"금지 주제: {forbidden}\n\n"
        f"[참고 컨텍스트]\n{context or '(없음)'}\n\n"
        f"[사용자 질문]\n{question}\n"
    )


def answer_with_openai(
    *,
    api_key: str,
    model: str,
    prompt: str,
    persona: dict,
) -> str | None:
    if not api_key or OpenAI is None:
        return None
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0.5,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a persona-based Korean assistant. "
                    "Follow persona role and speaking rules strictly."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    text = str(response.choices[0].message.content or "").strip()
    return text or None


def answer_without_llm(*, persona: dict, question: str, context: str) -> str:
    q = question.strip()
    tone = persona.get("tone", "친절")
    greeting = persona.get("greeting", "안녕하세요")
    bullets: list[str] = []

    if context.strip():
        bullets.append(f"컨텍스트 기반 핵심: {context.strip()[:240]}")
    if "계획" in q or "로드맵" in q:
        bullets.append("1) 목표를 정의하고 2) 주간 단위로 실험하고 3) 결과를 회고하세요.")
    elif "비용" in q or "예산" in q:
        bullets.append("모델 호출량, 입력/출력 토큰, 캐시 전략을 먼저 계산하세요.")
    else:
        bullets.append("질문을 목적/제약/성공지표 3가지로 분해하면 답변 품질이 높아집니다.")

    joined = "\n".join(f"- {line}" for line in bullets)
    return f"{greeting}\n[{tone} 톤]\n질문: {q}\n{joined}"
