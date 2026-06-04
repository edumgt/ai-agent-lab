from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import uuid


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


def list_knowledge(knowledge_file: Path) -> list[dict]:
    rows = _load_json(knowledge_file, default=[])
    rows.sort(key=lambda row: (int(row.get("priority", 50)), str(row.get("updated_at", ""))), reverse=True)
    return rows


def upsert_knowledge(knowledge_file: Path, payload_items: list[dict]) -> list[dict]:
    rows = _load_json(knowledge_file, default=[])
    index = {str(row.get("item_id", "")): i for i, row in enumerate(rows)}

    outputs: list[dict] = []
    for item in payload_items:
        item_id = str(item.get("item_id") or "").strip() or f"kb_{uuid.uuid4().hex[:10]}"
        record = {
            "item_id": item_id,
            "title": str(item.get("title", "")).strip(),
            "content": str(item.get("content", "")).strip(),
            "tags": [str(v).strip() for v in item.get("tags", []) if str(v).strip()],
            "priority": int(item.get("priority", 50)),
            "updated_at": _now_iso(),
        }

        if item_id in index:
            rows[index[item_id]] = record
        else:
            rows.append(record)
            index[item_id] = len(rows) - 1
        outputs.append(record)

    _save_json(knowledge_file, rows)
    return outputs


def bootstrap_knowledge(knowledge_file: Path) -> list[dict]:
    seed = [
        {
            "item_id": "kb_data_policy",
            "title": "고객 데이터 처리 정책",
            "content": "금융 상담 데이터는 수집 목적, 보관기간, 파기 기준, 제3자 제공 여부를 명확히 고지하고 동의 이력을 기록해야 한다.",
            "tags": ["정책", "개인정보", "금융소비자보호"],
            "priority": 92,
        },
        {
            "item_id": "kb_persona_style",
            "title": "금융 응답 스타일",
            "content": "답변은 핵심 결론-위험 요인-다음 행동 순으로 3단 구성으로 작성하고 수익 보장처럼 오해를 부를 표현을 금지한다.",
            "tags": ["스타일", "응답규칙", "리스크"],
            "priority": 88,
        },
        {
            "item_id": "kb_rag_chunk",
            "title": "리서치 문서 검색 품질",
            "content": "상품설명서, 약관, 시장 리포트는 문서 종류별로 분리 인덱싱하고 chunk 크기는 500~900자, overlap은 10~20%를 권장한다.",
            "tags": ["rag", "검색", "리서치"],
            "priority": 84,
        },
    ]
    return upsert_knowledge(knowledge_file, seed)


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[0-9a-zA-Z가-힣_]+", (text or "").lower()) if len(token) >= 2]


def retrieve_knowledge(knowledge_file: Path, question: str, top_k: int) -> list[dict]:
    q_tokens = set(_tokenize(question))
    scored: list[dict] = []

    for row in list_knowledge(knowledge_file):
        doc = f"{row.get('title','')} {row.get('content','')} {' '.join(row.get('tags',[]))}"
        d_tokens = set(_tokenize(doc))
        lexical = 0.0
        if q_tokens and d_tokens:
            lexical = len(q_tokens & d_tokens) / max(1, len(q_tokens))
        priority = float(row.get("priority", 50)) / 100.0
        score = round(min(1.0, (lexical * 0.72) + (priority * 0.28)), 6)
        if score <= 0.01:
            continue
        scored.append({**row, "score": score})

    scored.sort(key=lambda row: float(row.get("score", 0.0)), reverse=True)
    return scored[: max(1, min(10, top_k))]


def build_custom_answer(persona_name: str, style: str, question: str, matched: list[dict]) -> str:
    if not matched:
        return (
            f"[{persona_name}] {style} 기준 답변\n"
            f"질문: {question}\n"
            "- 사전 데이터에서 직접 근거를 찾지 못했습니다.\n"
            "- 먼저 데이터 항목(title/content/tags)을 보강해 주세요."
        )

    lines = [
        f"[{persona_name}] {style} 기준 답변",
        f"질문: {question}",
        "핵심 정리:",
    ]
    for idx, row in enumerate(matched, start=1):
        content = str(row.get("content", "")).strip()
        if len(content) > 140:
            content = content[:140] + "..."
        lines.append(f"{idx}. {row.get('title')} -> {content} (근거: {row.get('item_id')})")

    lines.append("다음 단계: 상위 근거 1~2개를 정책/기술 구현 항목으로 분리해 체크리스트화 하세요.")
    return "\n".join(lines)
