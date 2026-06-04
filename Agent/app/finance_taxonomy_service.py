from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

ALLOWED_CLASS_SEARCH_EXTS = {".md", ".py", ".html", ".txt", ".csv"}
CLASS_SEARCH_EXCLUDE_PATTERNS = (
    re.compile(r".*_assignment(_.*)?\.py$", re.IGNORECASE),
    re.compile(r".*instructor_notes\.md$", re.IGNORECASE),
)


@dataclass
class SubjectRange:
    subject_name: str
    class_start: str
    class_end: str
    day_start: int
    day_end: int
    class_count: int


class FinanceDomainIndex:
    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root
        finance_index_file = repo_root / "finance_domain_index.csv"
        legacy_index_file = repo_root / "curriculum_index.csv"
        self._index_file = finance_index_file if finance_index_file.exists() else legacy_index_file
        self._rows: list[dict[str, str]] = []
        self._subject_ranges: dict[str, SubjectRange] = {}
        self._alias_to_subject: dict[str, str] = {}
        self._class_map: dict[str, dict[str, str]] = {}
        self._subject_dirs: dict[str, list[str]] = {}
        self.reload()

    def reload(self) -> None:
        self._rows = self._load_rows()
        self._subject_ranges = self._build_subject_ranges(self._rows)
        self._alias_to_subject = self._build_subject_aliases(self._subject_ranges)
        self._class_map = self._build_class_map(self._rows)
        self._subject_dirs = self._build_subject_dirs(self._rows)

    @property
    def index_path(self) -> str:
        return self._index_file.as_posix()

    def resolve_subject(self, raw_subject: str) -> str | None:
        key = self._normalize(raw_subject)
        if not key:
            return None
        if key in self._alias_to_subject:
            return self._alias_to_subject[key]

        # Fuzzy containment fallback
        for alias_key, subject in self._alias_to_subject.items():
            if key in alias_key or alias_key in key:
                return subject
        return None

    def get_subject_range(self, subject_name: str) -> SubjectRange | None:
        return self._subject_ranges.get(subject_name)

    def detect_subject_in_question(self, question: str) -> str | None:
        q = self._normalize(question)
        for alias, subject in self._alias_to_subject.items():
            if alias and alias in q:
                return subject

        # Broad keyword heuristics for common labels
        if any(k in q for k in ["python", "파이썬"]):
            return self.resolve_subject("Python 프로그래밍")
        if "프롬프트" in q:
            return self.resolve_subject("프롬프트 엔지니어링")
        if "rag" in q:
            return self.resolve_subject("RAG(Retrieval-Augmented Generation)")
        if any(k in q for k in ["llm", "언어모델", "거대언어모델", "생성형ai"]):
            return self.resolve_subject("거대 언어 모델을 활용한 자연어 생성")
        if any(k in q for k in ["langchain", "랭체인"]):
            return self.resolve_subject("Langchain 활용하기")
        if any(k in q for k in ["devops", "mlops", "aiops", "llmops", "프로젝트"]):
            return self.resolve_subject("프로젝트")
        if any(k in q for k in ["stt", "tts", "음성", "transcribe", "speech"]):
            return self.resolve_subject("자연어 및 음성 데이터 활용 및 모델 개발")
        return None

    def subject_directory_hints(self, subject_name: str | None) -> list[str]:
        if not subject_name:
            return []
        return list(self._subject_dirs.get(subject_name, []))

    @staticmethod
    def is_range_question(question: str) -> bool:
        q = question.replace(" ", "")
        patterns = [
            r"몇번부터몇번",
            r"어디부터어디",
            r"범위",
            r"시작.*끝",
            r"(class|project)\d+.*(class|project)\d+",
        ]
        return any(re.search(p, q, flags=re.IGNORECASE) for p in patterns)

    def answer_subject_range(self, subject_name: str) -> str | None:
        rng = self.get_subject_range(subject_name)
        if not rng:
            return None
        return (
            f"{subject_name} 과정은 {rng.class_start} ~ {rng.class_end} 입니다. "
            f"(총 {rng.class_count}개 차시, Day {rng.day_start:02d} ~ Day {rng.day_end:02d})"
        )

    def answer_concept_definition(self, concept: str) -> str | None:
        concept = (concept or "").strip().lower()
        glossary: dict[str, dict[str, str]] = {
            "llm": {
                "title": "LLM (Large Language Model)",
                "desc": "LLM은 대규모 텍스트 데이터로 학습된 언어 모델로, 금융 상담/요약/문서 생성 같은 업무를 자동화합니다.",
                "subject": "거대 언어 모델을 활용한 자연어 생성",
                "hint": "금융 민감정보 마스킹, 환각 통제, 감사 가능한 응답 추적이 핵심 운영 포인트입니다.",
            },
            "rag": {
                "title": "RAG (Retrieval-Augmented Generation)",
                "desc": "RAG는 문서 검색 결과를 근거로 결합해 답변을 생성하는 방식으로, 환각을 줄이고 근거 기반 답변을 강화합니다.",
                "subject": "RAG(Retrieval-Augmented Generation)",
                "hint": "여신 규정, 내부통제 기준, 상품 약관 같은 문서를 근거로 답변할 때 특히 효과적입니다.",
            },
            "langchain": {
                "title": "LangChain",
                "desc": "LangChain은 LLM 애플리케이션을 체인, 도구, 메모리 구조로 구성할 수 있게 돕는 프레임워크입니다.",
                "subject": "Langchain 활용하기",
                "hint": "금융 상담 워크플로를 툴 호출, 규정 조회, 요약 리포트 생성 단계로 분리할 때 유용합니다.",
            },
            "prompt": {
                "title": "프롬프트 엔지니어링",
                "desc": "프롬프트 엔지니어링은 모델이 원하는 형식과 품질로 응답하도록 입력(역할/맥락/출력형식)을 설계하는 방법입니다.",
                "subject": "프롬프트 엔지니어링",
                "hint": "금융 답변은 근거 우선, 규정 인용, 불확실성 고지 규칙을 프롬프트에 명시하는 것이 중요합니다.",
            },
            "embedding": {
                "title": "임베딩 (Embedding)",
                "desc": "임베딩은 텍스트/데이터를 의미를 보존한 벡터로 변환한 표현으로, 검색/유사도 계산의 기반입니다.",
                "subject": "RAG(Retrieval-Augmented Generation)",
                "hint": "신용평가 보고서, 시장 코멘트, 리스크 공지의 의미 유사도 탐색에 활용됩니다.",
            },
            "vector_db": {
                "title": "벡터 DB (Vector Database)",
                "desc": "벡터 DB는 임베딩 벡터를 저장하고 유사도 기반 검색을 빠르게 수행하는 데이터베이스입니다.",
                "subject": "RAG(Retrieval-Augmented Generation)",
                "hint": "RAG 검색 계층의 핵심 구성요소입니다.",
            },
            "devops": {
                "title": "DevOps",
                "desc": "DevOps는 개발과 운영을 통합해 소프트웨어를 빠르고 안정적으로 배포/운영하는 방법론입니다.",
                "subject": "프로젝트",
                "hint": "대표 솔루션은 CI/CD(GitHub Actions/Jenkins), 컨테이너(Docker), 오케스트레이션(Kubernetes)입니다. 프로젝트 앱(VoiceModelBuilder, PersonaLLMResponder, PersonaKnowledgeCustomizer)에서 배포 자동화와 운영 절차로 연결해 학습합니다.",
            },
            "mlops": {
                "title": "MLOps",
                "desc": "MLOps는 데이터 준비, 모델 학습, 배포, 모니터링, 재학습까지 모델 생명주기를 운영 자동화하는 체계입니다.",
                "subject": "프로젝트",
                "hint": "대표 솔루션은 MLflow, Kubeflow, Airflow, DVC, SageMaker입니다. 현재 프로젝트 앱에서는 VoiceModelBuilder를 중심으로 파이프라인/모델 운영 흐름을 연결합니다.",
            },
            "aiops": {
                "title": "AIOps",
                "desc": "AIOps는 운영 로그·메트릭·트레이스를 AI/ML로 분석해 이상 탐지, 원인 분석, 자동 복구를 수행하는 방식입니다.",
                "subject": "프로젝트",
                "hint": "대표 솔루션은 Datadog, Dynatrace, New Relic, Splunk, Prometheus+Grafana 조합입니다. 현재 프로젝트 앱에서는 PersonaKnowledgeCustomizer를 중심으로 관측성/로그 기반 품질 점검을 다룹니다.",
            },
            "llmops": {
                "title": "LLMOps",
                "desc": "LLMOps는 LLM 기반 서비스의 프롬프트, RAG, 평가, 가드레일, 배포/운영 품질을 관리하는 체계입니다.",
                "subject": "프로젝트",
                "hint": "대표 솔루션은 OpenAI API/플랫폼, Azure OpenAI, Vertex AI, Bedrock, LangChain 계열 도구입니다. 현재 프로젝트 앱에서는 PersonaLLMResponder/PersonaKnowledgeCustomizer에서 RAG/품질관리 시나리오로 학습합니다.",
            },
            "aws_stt": {
                "title": "AWS STT 연동 리소스",
                "desc": "AWS에서 STT 연동의 기본 리소스는 Amazon Transcribe이며, 실시간/배치 음성 전사를 모두 지원합니다.",
                "subject": "자연어 및 음성 데이터 활용 및 모델 개발",
                "hint": "파일 기반은 S3 + Transcribe Batch, 실시간은 Transcribe Streaming + API Gateway/Lambda 또는 ECS/EKS 연계를 권장합니다.",
            },
            "aws_tts": {
                "title": "AWS TTS 연동 리소스",
                "desc": "AWS에서 TTS 연동의 기본 리소스는 Amazon Polly이며, 텍스트를 자연스러운 음성으로 합성합니다.",
                "subject": "자연어 및 음성 데이터 활용 및 모델 개발",
                "hint": "Polly 음성 파일을 S3에 저장하고 API Gateway/Lambda 또는 ECS/EKS 서비스에서 재생 API로 연계할 수 있습니다.",
            },
            "aws_translate": {
                "title": "AWS 번역 연동 리소스",
                "desc": "AWS 다국어 번역의 기본 리소스는 Amazon Translate입니다.",
                "subject": "자연어 및 음성 데이터 활용 및 모델 개발",
                "hint": "실시간 번역 API는 API Gateway/Lambda, 대량 배치 번역은 S3 기반 파이프라인(ECS/EKS 포함)으로 구성하는 패턴이 일반적입니다.",
            },
            "aws_summarize": {
                "title": "AWS 요약 연동 리소스",
                "desc": "AWS에서 문서 요약은 Amazon Bedrock의 LLM 모델을 활용하는 방식이 실무에서 널리 사용됩니다.",
                "subject": "거대 언어 모델을 활용한 자연어 생성",
                "hint": "요약 서비스는 S3 입력 + Bedrock 호출 + API Gateway/Lambda 또는 ECS/EKS 배포 구조로 설계할 수 있습니다.",
            },
            "aws_comprehend": {
                "title": "AWS NLP 분석 연동 리소스",
                "desc": "AWS에서 감정 분석, 개체명 인식, 키프레이즈 추출 같은 NLP 분석은 Amazon Comprehend가 기본 리소스입니다.",
                "subject": "자연어 및 음성 데이터 활용 및 모델 개발",
                "hint": "실시간 분석 API는 API Gateway/Lambda, 대량 분석은 S3 + 배치 파이프라인(ECS/EKS)으로 운영할 수 있습니다.",
            },
        }
        item = glossary.get(concept)
        if not item:
            return None

        subject_name = self.resolve_subject(item["subject"]) or item["subject"]
        range_line = ""
        if subject_name:
            range_answer = self.answer_subject_range(subject_name)
            if range_answer:
                range_line = f" 관련 도메인 범위: {range_answer}"

        return f"{item['title']}: {item['desc']} {item['hint']}{range_line}"

    def class_local_search(self, class_id: str, question: str, top_k: int = 6) -> list[dict]:
        info = self._class_map.get(class_id)
        if not info:
            return []
        class_dir_rel = info.get("class_dir", "")
        class_dir = self._repo_root / class_dir_rel
        if not class_dir.exists():
            return []

        q_tokens = self._tokenize(question)
        if not q_tokens:
            return []

        results: list[dict] = []
        for path in class_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in ALLOWED_CLASS_SEARCH_EXTS:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            lines = text.splitlines()
            if not lines:
                continue
            rel = path.relative_to(self._repo_root).as_posix()
            rel_lower = rel.lower()
            if any(pat.match(rel_lower) for pat in CLASS_SEARCH_EXCLUDE_PATTERNS):
                continue
            best_score = 0.0
            best_line = ""
            for line in lines:
                score = self._lexical_overlap(q_tokens, line)
                if score > best_score:
                    best_score = score
                    best_line = line.strip()
            if best_score <= 0.0:
                continue
            # 가이드(.md)와 예제/정답 파일을 우선 노출
            if rel_lower.endswith(".md"):
                best_score = min(1.0, best_score + 0.14)
            elif "_example" in rel_lower or "_solution.py" in rel_lower:
                best_score = min(1.0, best_score + 0.10)
            snippet = best_line if len(best_line) <= 300 else best_line[:300] + "..."
            results.append({"path": rel, "score": round(best_score, 6), "chunk": snippet})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[: max(1, top_k)]

    def class_subject(self, class_id: str) -> str | None:
        info = self._class_map.get(class_id)
        if not info:
            return None
        subject = info.get("subject_name", "").strip()
        return subject or None

    def answer_class_scoped(self, class_id: str, question: str, sources: list[dict]) -> str | None:
        info = self._class_map.get(class_id)
        if not info:
            return None
        subject = info.get("subject_name", "")
        module = info.get("module", "")
        day = info.get("day", "")
        slot = info.get("slot", "")
        day_text = f"{int(day):02d}" if str(day).isdigit() else str(day)
        if not sources:
            return (
                f"{class_id}({subject})의 질문에 대한 근거를 충분히 찾지 못했습니다. "
                f"{class_id}.md / {class_id}_example1.py 중심으로 다시 질문해 주세요."
            )

        lead = (
            f"{class_id}는 '{module}' 주제(도메인: {subject}, Day {day_text} / {slot}교시)입니다. "
            f"질문 '{question}'과 직접 관련된 근거를 우선 정리했습니다."
        )
        bullets = []
        for idx, src in enumerate(sources[:3], start=1):
            bullets.append(f"{idx}. {src['path']} -> {src['chunk']}")
        return lead + "\n" + "\n".join(bullets)

    def _load_rows(self) -> list[dict[str, str]]:
        if not self._index_file.exists():
            return []

        rows: list[dict[str, str]] = []
        with self._index_file.open(encoding="utf-8-sig", newline="") as fp:
            reader = csv.DictReader(line for line in fp if line.strip() and not line.lstrip().startswith("#"))
            for raw in reader:
                row = {str(k).lstrip("\ufeff"): str(v).strip() for k, v in raw.items()}
                if row.get("class"):
                    rows.append(row)
        return rows

    @staticmethod
    def _build_subject_ranges(rows: list[dict[str, str]]) -> dict[str, SubjectRange]:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            subject = row.get("subject_name", "").strip()
            if not subject:
                continue
            grouped.setdefault(subject, []).append(row)

        out: dict[str, SubjectRange] = {}
        for subject, items in grouped.items():
            items_sorted = sorted(items, key=lambda r: r.get("class", ""))
            day_values = [int(i.get("day", "0") or 0) for i in items_sorted if (i.get("day", "0") or "0").isdigit()]
            out[subject] = SubjectRange(
                subject_name=subject,
                class_start=items_sorted[0].get("class", ""),
                class_end=items_sorted[-1].get("class", ""),
                day_start=min(day_values) if day_values else 0,
                day_end=max(day_values) if day_values else 0,
                class_count=len(items_sorted),
            )
        return out

    def _build_subject_aliases(self, subject_ranges: dict[str, SubjectRange]) -> dict[str, str]:
        aliases: dict[str, str] = {}
        for subject in subject_ranges.keys():
            norm = self._normalize(subject)
            aliases[norm] = subject

            # Keep tokens and common alternates.
            plain = re.sub(r"\(.*?\)", "", subject).strip()
            aliases[self._normalize(plain)] = subject

        explicit = {
            "python": "Python 프로그래밍",
            "파이썬": "Python 프로그래밍",
            "python프로그래밍": "Python 프로그래밍",
            "데이터전처리및시각화": "Python 전처리 및 시각화",
            "시각화": "Python 전처리 및 시각화",
            "머신러닝과딥러닝": "머신러닝과 딥러닝",
            "자연어및음성데이터활용및모델개발": "자연어 및 음성 데이터 활용 및 모델 개발",
            "tts": "음성 데이터 활용한 TTS와 STT 모델 개발",
            "stt": "음성 데이터 활용한 TTS와 STT 모델 개발",
            "llm": "거대 언어 모델을 활용한 자연어 생성",
            "프롬프트엔지니어링": "프롬프트 엔지니어링",
            "langchain": "Langchain 활용하기",
            "rag": "RAG(Retrieval-Augmented Generation)",
            "프로젝트": "프로젝트",
        }
        for alias, subj in explicit.items():
            if subj in subject_ranges:
                aliases[self._normalize(alias)] = subj

        return aliases

    @staticmethod
    def _build_class_map(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
        out: dict[str, dict[str, str]] = {}
        for row in rows:
            class_id = row.get("class", "").strip()
            md_file = row.get("md_file", "").strip()
            if not class_id:
                continue
            class_dir = Path(md_file).parent.as_posix() if md_file else class_id
            out[class_id] = {
                "class_id": class_id,
                "subject_name": row.get("subject_name", "").strip(),
                "module": row.get("module", "").strip(),
                "day": row.get("day", "").strip(),
                "slot": row.get("slot", "").strip(),
                "md_file": md_file,
                "class_dir": class_dir,
            }
        return out

    @staticmethod
    def _build_subject_dirs(rows: list[dict[str, str]]) -> dict[str, list[str]]:
        out: dict[str, set[str]] = {}
        for row in rows:
            subject = row.get("subject_name", "").strip()
            md_file = row.get("md_file", "").strip()
            if not subject or not md_file:
                continue
            root_dir = Path(md_file).parts[0] if Path(md_file).parts else ""
            if not root_dir:
                continue
            out.setdefault(subject, set()).add(root_dir)
        return {subject: sorted(list(dirs)) for subject, dirs in out.items()}

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"[^0-9a-zA-Z가-힣]", "", (text or "").lower()).strip()

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [t for t in re.findall(r"[0-9a-zA-Z가-힣_]+", (text or "").lower()) if len(t) >= 2]

    @staticmethod
    def _lexical_overlap(q_tokens: list[str], text: str) -> float:
        d_tokens = set(FinanceDomainIndex._tokenize(text))
        if not d_tokens:
            return 0.0
        overlap = sum(1 for t in q_tokens if t in d_tokens)
        return min(1.0, overlap / max(1, len(set(q_tokens))))
