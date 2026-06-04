from __future__ import annotations

from dataclasses import dataclass
import re

from app.finance_taxonomy_service import FinanceDomainIndex


@dataclass
class RoutedQuery:
    mode: str
    subject_name: str | None = None
    class_id: str | None = None
    concept: str | None = None
    query_expansions: list[str] | None = None


class QueryRouter:
    """Route question to structured handler or RAG search."""

    def __init__(self, finance_index: FinanceDomainIndex) -> None:
        self._index = finance_index

    def route(self, question: str) -> RoutedQuery:
        subject = self._index.detect_subject_in_question(question)
        class_id = self._extract_class_id(question)
        concept = self._extract_concept(question)
        expansions = self._build_query_expansions(question, concept)
        if concept and (
            concept.startswith("aws_")
            or concept in {"devops", "mlops", "aiops", "llmops"}
            or self._is_definition_question(question)
        ):
            return RoutedQuery(
                mode="concept_definition",
                subject_name=subject,
                class_id=class_id,
                concept=concept,
                query_expansions=expansions,
            )
        if subject and self._index.is_range_question(question):
            return RoutedQuery(
                mode="subject_range",
                subject_name=subject,
                class_id=class_id,
                concept=concept,
                query_expansions=expansions,
            )
        return RoutedQuery(mode="rag", subject_name=subject, class_id=class_id, concept=concept, query_expansions=expansions)

    @staticmethod
    def _extract_class_id(question: str) -> str | None:
        m = re.search(r"\b(class|project)\s*([0-9]{3})\b", question, flags=re.IGNORECASE)
        if m:
            prefix = m.group(1).lower()
            return f"{prefix}{m.group(2)}"
        # "290번", "290 번" 같은 질의도 classID/projectID로 해석
        m2 = re.search(r"\b([0-9]{3})\s*번\b", question)
        if m2:
            has_project_hint = bool(re.search(r"project|프로젝트", question, flags=re.IGNORECASE))
            number = m2.group(1)
            if has_project_hint:
                return f"project{number}"
            return f"class{number}"
        return None

    @staticmethod
    def _extract_concept(question: str) -> str | None:
        q = question.lower()
        q_norm = re.sub(r"[^0-9a-zA-Z가-힣]", "", q)
        if "llm" in q_norm or any(k in q_norm for k in ["거대언어모델", "언어모델", "대형언어모델", "largelanguagemodel"]):
            return "llm"
        if "rag" in q_norm:
            return "rag"
        if "langchain" in q_norm or "랭체인" in question:
            return "langchain"
        if "프롬프트" in question:
            return "prompt"
        if "임베딩" in question:
            return "embedding"
        if "벡터" in question and "db" in q_norm:
            return "vector_db"
        if "devops" in q_norm or "데브옵스" in question:
            return "devops"
        if "mlops" in q_norm:
            return "mlops"
        if "aiops" in q_norm:
            return "aiops"
        if "llmops" in q_norm:
            return "llmops"
        if ("aws" in q or "아마존" in question) and any(k in q for k in ["stt", "transcribe", "speech", "음성"]):
            return "aws_stt"
        if ("aws" in q or "아마존" in question) and any(k in q for k in ["tts", "polly", "음성합성"]):
            return "aws_tts"
        if ("aws" in q or "아마존" in question) and any(k in q for k in ["번역", "translate", "다국어", "translation"]):
            return "aws_translate"
        if ("aws" in q or "아마존" in question) and any(k in q for k in ["요약", "summarize", "summary"]):
            return "aws_summarize"
        if ("aws" in q or "아마존" in question) and any(
            k in q for k in ["감정", "개체", "분석", "nlp", "comprehend", "sentiment", "entity"]
        ):
            return "aws_comprehend"
        return None

    @staticmethod
    def _build_query_expansions(question: str, concept: str | None) -> list[str]:
        q = question.lower()
        expansions: list[str] = []
        q_norm = re.sub(r"[^0-9a-zA-Z가-힣]", "", q)

        if concept == "llm" or any(k in q_norm for k in ["거대언어모델", "언어모델", "llm"]):
            expansions.extend(
                [
                    "금융 생성형 AI 모델 거버넌스 환각 통제 개인정보 보호",
                    "투자 리서치 보고서 생성 자동화 LLM 프롬프트 설계",
                    "금융 상담 챗봇 설명 가능성 감사 로그 설계",
                ]
            )
        if concept == "rag" or "rag" in q_norm:
            expansions.extend(
                [
                    "RAG 기반 금융 규정 문서 검색 근거 답변",
                    "신용심사 약관 내부통제 매뉴얼 벡터 검색 파이프라인",
                    "금융 보고서 출처 추적 임베딩 리랭크 품질 평가",
                ]
            )
        if concept in {"devops", "mlops", "aiops", "llmops"}:
            expansions.extend(
                [
                    "금융 AI 서비스 devops mlops aiops llmops 운영체계",
                    "모델 배포 승인 체계 모니터링 경보 감사 추적",
                    "리스크 관리 대시보드 운영 자동화 관측성",
                ]
            )
        if concept == "aws_stt" or (
            ("aws" in q or "아마존" in question) and any(k in q for k in ["stt", "transcribe", "speech", "음성"])
        ):
            expansions.extend(
                [
                    "AWS STT Amazon Transcribe 실시간 배치 연동",
                    "음성 인식 speech to text aws transcribe",
                    "S3 Transcribe Streaming API Gateway Lambda ECS EKS",
                ]
            )
        if concept == "aws_tts" or (
            ("aws" in q or "아마존" in question) and any(k in q for k in ["tts", "polly", "음성합성"])
        ):
            expansions.extend(
                [
                    "AWS TTS Amazon Polly 음성 합성",
                    "텍스트 음성 변환 aws polly neural voice",
                    "S3 Polly Lambda API Gateway ECS EKS",
                ]
            )
        if concept == "aws_translate" or (
            ("aws" in q or "아마존" in question) and any(k in q for k in ["번역", "translate", "다국어", "translation"])
        ):
            expansions.extend(
                [
                    "AWS 번역 Amazon Translate 다국어",
                    "text translation aws translate",
                    "API Gateway Lambda ECS EKS translation pipeline",
                ]
            )
        if concept == "aws_summarize" or (
            ("aws" in q or "아마존" in question) and any(k in q for k in ["요약", "summarize", "summary"])
        ):
            expansions.extend(
                [
                    "AWS 요약 Amazon Bedrock summarize",
                    "LLM text summarization aws bedrock",
                    "S3 Bedrock Lambda ECS EKS summarization service",
                ]
            )
        if concept == "aws_comprehend" or (
            ("aws" in q or "아마존" in question)
            and any(k in q for k in ["감정", "개체", "분석", "nlp", "comprehend", "sentiment", "entity"])
        ):
            expansions.extend(
                [
                    "AWS NLP Amazon Comprehend sentiment entity keyphrase",
                    "텍스트 감정 분석 개체명 인식 aws comprehend",
                    "Comprehend API Gateway Lambda ECS EKS 분석 서비스",
                ]
            )
        return expansions

    @staticmethod
    def _is_definition_question(question: str) -> bool:
        q = question.replace(" ", "").lower()
        patterns = [
            r"이란",
            r"란$",
            r"뭔가요",
            r"뭐야",
            r"무엇인가요",
            r"무엇인가",
            r"어떤리소스",
            r"무슨리소스",
            r"연동가능",
            r"솔루션",
            r"설명",
            r"뜻",
            r"개념",
            r"정의",
            r"whatis",
        ]
        return any(re.search(p, q) for p in patterns)
