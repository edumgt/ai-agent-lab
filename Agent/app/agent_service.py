from __future__ import annotations

from typing import Sequence

from app.config import settings

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


class QnaAgent:
    def __init__(self) -> None:
        self._client = None
        self._model = ""

        if OpenAI is None:
            return

        if settings.use_lm_studio:
            # LM Studio (로컬 추론, OpenAI 호환 API)
            self._client = OpenAI(
                base_url=settings.lm_studio_url,
                api_key=settings.lm_studio_api_key,
            )
            self._model = settings.lm_studio_model
        elif settings.openai_api_key:
            # OpenAI 클라우드 API
            self._client = OpenAI(api_key=settings.openai_api_key)
            self._model = settings.openai_model

    def answer(
        self,
        question: str,
        sources: Sequence[dict],
        use_llm: bool = True,
        mode: str = "rag",
        persona_instruction: str = "",
    ) -> str:
        if mode == "subject_range":
            return self._answer_without_llm(question, sources)
        if use_llm and self._client is not None:
            try:
                return self._answer_with_llm(question, sources, persona_instruction=persona_instruction)
            except Exception:
                return self._answer_without_llm(question, sources)
        return self._answer_without_llm(question, sources)

    def _answer_with_llm(self, question: str, sources: Sequence[dict], persona_instruction: str = "") -> str:
        context_lines = []
        for idx, item in enumerate(sources, start=1):
            context_lines.append(
                f"[source {idx}] path={item['path']} score={item['score']:.3f}\n{item['chunk']}"
            )

        context_block = "\n\n".join(context_lines)
        persona_line = persona_instruction.strip() or "기본 학습 도우미 톤으로 간결하게 설명하세요."
        prompt = (
            "당신은 이 저장소 학습 도우미입니다. "
            "반드시 제공된 source 범위에서만 답하세요. "
            "근거가 부족하면 추측하지 말고 불확실하다고 말하세요. "
            "답변 형식: 1) 핵심 답변 2) 근거 요약 3) 참고 파일.\n\n"
            f"[페르소나 지시]\n{persona_line}\n\n"
            f"[질문]\n{question}\n\n"
            f"[검색 컨텍스트]\n{context_block}"
        )

        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are a careful repository Q&A assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return (response.choices[0].message.content or "").strip()

    def _answer_without_llm(self, question: str, sources: Sequence[dict]) -> str:
        if not sources:
            return "질문과 관련된 자료를 찾지 못했습니다. 질문 키워드를 더 구체적으로 입력해 주세요."

        summary_lines = [
            f"핵심 답변(요약): 질문 '{question}'에 대한 관련 근거를 아래에서 확인하세요.",
            "근거 요약:",
        ]
        for idx, item in enumerate(sources[:5], start=1):
            chunk = " ".join(item["chunk"].split())
            if len(chunk) > 280:
                chunk = chunk[:280] + "..."
            summary_lines.append(
                f"{idx}. [{item['path']}] (score={item['score']:.2f}) {chunk}"
            )

        summary_lines.append(
            "\n참고: LM Studio 를 실행하고 LM_STUDIO_URL 을 설정하면 생성형 답변을 받을 수 있습니다."
        )
        return "\n".join(summary_lines)
