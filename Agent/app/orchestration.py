from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from app.agent_service import QnaAgent


@dataclass
class OrchestrationResult:
    answer: str
    selected_mode: str
    note: str = ""


class AnswerOrchestrator:
    def __init__(self, *, agent: QnaAgent, openai_api_key: str, openai_model: str) -> None:
        self._agent = agent
        self._openai_api_key = openai_api_key
        self._openai_model = openai_model

        self._langchain_ready = False
        self._langgraph_ready = False

        self._ChatPromptTemplate = None
        self._StrOutputParser = None
        self._ChatOpenAI = None
        self._StateGraph = None
        self._START = None
        self._END = None

        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI

            self._ChatPromptTemplate = ChatPromptTemplate
            self._StrOutputParser = StrOutputParser
            self._ChatOpenAI = ChatOpenAI
            self._langchain_ready = True
        except Exception:
            self._langchain_ready = False

        try:
            from langgraph.graph import END, START, StateGraph

            self._StateGraph = StateGraph
            self._START = START
            self._END = END
            self._langgraph_ready = True
        except Exception:
            self._langgraph_ready = False

    @property
    def availability(self) -> dict[str, bool]:
        return {
            "native": True,
            "langchain": self._langchain_ready,
            "langgraph": self._langgraph_ready,
        }

    def answer(
        self,
        *,
        question: str,
        sources: Sequence[dict[str, Any]],
        use_llm: bool,
        requested_mode: str,
        persona_instruction: str = "",
    ) -> OrchestrationResult:
        mode = (requested_mode or "native").strip().lower()

        if mode == "langchain":
            return self._answer_langchain(
                question=question,
                sources=sources,
                use_llm=use_llm,
                persona_instruction=persona_instruction,
            )

        if mode == "langgraph":
            return self._answer_langgraph(
                question=question,
                sources=sources,
                use_llm=use_llm,
                persona_instruction=persona_instruction,
            )

        return OrchestrationResult(
            answer=self._agent.answer(
                question=question,
                sources=sources,
                use_llm=use_llm,
                mode="rag",
                persona_instruction=persona_instruction,
            ),
            selected_mode="native",
        )

    def _answer_langchain(
        self,
        *,
        question: str,
        sources: Sequence[dict[str, Any]],
        use_llm: bool,
        persona_instruction: str,
    ) -> OrchestrationResult:
        if not self._langchain_ready:
            fallback = self._agent.answer(
                question=question,
                sources=sources,
                use_llm=use_llm,
                mode="rag",
                persona_instruction=persona_instruction,
            )
            return OrchestrationResult(
                answer=fallback,
                selected_mode="native",
                note="langchain package unavailable, fell back to native",
            )

        if not use_llm or not self._openai_api_key:
            fallback = self._agent.answer(
                question=question,
                sources=sources,
                use_llm=False,
                mode="rag",
                persona_instruction=persona_instruction,
            )
            return OrchestrationResult(
                answer=fallback,
                selected_mode="langchain",
                note="LLM disabled or OPENAI_API_KEY missing, used deterministic summary",
            )

        context = self._build_context(sources)
        try:
            prompt = self._ChatPromptTemplate.from_template(
                """
당신은 금융 서비스 실험실용 에이전트입니다.
반드시 제공된 컨텍스트 범위에서만 답변하세요.
추측하지 말고 근거가 부족하면 부족하다고 명시하세요.

[페르소나 지시]
{persona_instruction}

[질문]
{question}

[컨텍스트]
{context}

출력 형식:
1) 핵심 답변
2) 근거 요약
3) 참고 파일 목록
""".strip()
            )
            llm = self._ChatOpenAI(
                api_key=self._openai_api_key,
                model=self._openai_model,
                temperature=0.2,
            )
            chain = prompt | llm | self._StrOutputParser()
            answer = chain.invoke(
                {
                    "persona_instruction": persona_instruction or "(기본)",
                    "question": question,
                    "context": context,
                }
            )
            return OrchestrationResult(answer=str(answer).strip(), selected_mode="langchain")
        except Exception as exc:
            fallback = self._agent.answer(
                question=question,
                sources=sources,
                use_llm=use_llm,
                mode="rag",
                persona_instruction=persona_instruction,
            )
            return OrchestrationResult(
                answer=fallback,
                selected_mode="native",
                note=f"langchain execution failed: {exc}",
            )

    def _answer_langgraph(
        self,
        *,
        question: str,
        sources: Sequence[dict[str, Any]],
        use_llm: bool,
        persona_instruction: str,
    ) -> OrchestrationResult:
        if not self._langgraph_ready:
            fallback = self._agent.answer(
                question=question,
                sources=sources,
                use_llm=use_llm,
                mode="rag",
                persona_instruction=persona_instruction,
            )
            return OrchestrationResult(
                answer=fallback,
                selected_mode="native",
                note="langgraph package unavailable, fell back to native",
            )

        try:
            StateGraph = self._StateGraph
            START = self._START
            END = self._END

            def build_context_node(state: dict[str, Any]) -> dict[str, Any]:
                return {"context": self._build_context(state.get("sources", []))}

            def answer_node(state: dict[str, Any]) -> dict[str, Any]:
                if use_llm and self._langchain_ready and self._openai_api_key:
                    result = self._answer_langchain(
                        question=state.get("question", ""),
                        sources=state.get("sources", []),
                        use_llm=True,
                        persona_instruction=state.get("persona_instruction", ""),
                    )
                    return {"answer": result.answer}

                fallback = self._agent.answer(
                    question=state.get("question", ""),
                    sources=state.get("sources", []),
                    use_llm=False,
                    mode="rag",
                    persona_instruction=state.get("persona_instruction", ""),
                )
                return {"answer": fallback}

            graph = StateGraph(dict)
            graph.add_node("build_context", build_context_node)
            graph.add_node("answer", answer_node)
            graph.add_edge(START, "build_context")
            graph.add_edge("build_context", "answer")
            graph.add_edge("answer", END)
            compiled = graph.compile()
            output = compiled.invoke(
                {
                    "question": question,
                    "sources": list(sources),
                    "persona_instruction": persona_instruction,
                }
            )
            answer = str(output.get("answer", "")).strip()
            if not answer:
                answer = self._agent.answer(
                    question=question,
                    sources=sources,
                    use_llm=False,
                    mode="rag",
                    persona_instruction=persona_instruction,
                )
            return OrchestrationResult(answer=answer, selected_mode="langgraph")
        except Exception as exc:
            fallback = self._agent.answer(
                question=question,
                sources=sources,
                use_llm=use_llm,
                mode="rag",
                persona_instruction=persona_instruction,
            )
            return OrchestrationResult(
                answer=fallback,
                selected_mode="native",
                note=f"langgraph execution failed: {exc}",
            )

    @staticmethod
    def _build_context(sources: Sequence[dict[str, Any]]) -> str:
        lines: list[str] = []
        for idx, source in enumerate(sources, start=1):
            path = str(source.get("path", ""))
            score = float(source.get("score", 0.0))
            chunk = str(source.get("chunk", "")).strip()
            lines.append(f"[{idx}] path={path} score={score:.3f}\n{chunk}")
        return "\n\n".join(lines)
