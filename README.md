<!-- 이 파일은 www.edumgt.co.kr 의 에듀엠지티에 저작권이 있습니다 -->
# LM Studio AI Agent Lab

**LM Studio** 로 로컬에서 LLM 을 실행하며 AI 에이전트를 단계적으로 구축하는 실습 저장소입니다.
외부 API 키 없이 내 PC에서 바로 시작할 수 있습니다.

---

## LM Studio 란?

- **로컬 LLM 실행 도구**: GGUF 형식 오픈소스 모델을 내 PC에서 실행
- **OpenAI 호환 API**: `http://localhost:1234/v1` — 기존 OpenAI SDK 코드를 그대로 사용
- **무료/무API키**: 인터넷 연결 불필요, 비용 없음
- **지원 OS**: Windows · macOS · Linux

### 설치 및 시작

```
1. https://lmstudio.ai 에서 설치 파일 다운로드
2. LM Studio 실행 → 좌측 "Discover" 탭 → 모델 검색 및 다운로드
   권장 입문 모델: Qwen2.5-7B-Instruct-GGUF (4~8GB)
   경량 모델:     Phi-3.5-mini-instruct-GGUF (2~4GB)
3. 좌측 "Local Server" 탭 → [Start Server] 클릭 (포트 1234)
4. 이 저장소 실습 실행
```

### 빠른 연결 확인

```python
# 설치: pip install openai
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
response = client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": "안녕하세요!"}],
)
print(response.choices[0].message.content)
```

또는 공통 유틸리티 사용:

```python
from lmstudio_config import call_lm_simple
print(call_lm_simple("안녕하세요!"))
```

---

## 난이도별 학습 경로

### 레벨 1 — 입문 (Python + LM Studio 첫 걸음)

> 목표: Python 기초와 LM Studio 설치, 첫 LLM 호출 성공

| 모듈 | 범위 | 핵심 내용 |
|------|------|----------|
| Python 프로그래밍 | class001~040 | 변수·자료형·함수·HTML·FastAPI 기초 |
| LLM 첫 호출 | class289~295 | LM Studio 설치, OpenAI SDK로 첫 대화 |

**실습 시작:**
```bash
# Python 기초
python pyBasics/class001/class001.py

# LM Studio 첫 호출 (LM Studio 실행 후)
python llmTextGen/class289/class289_example1.py
```

**학습 체크리스트:**
- [ ] LM Studio 설치 및 모델 다운로드
- [ ] 로컬 서버 실행 (포트 1234 확인)
- [ ] `lmstudio_config.py` 로 연결 확인
- [ ] 첫 번째 chat completion 호출 성공

---

### 레벨 2 — 기초 (데이터 + 프롬프트 엔지니어링)

> 목표: 데이터 처리 기초와 프롬프트로 LLM 응답 품질 제어

| 모듈 | 범위 | 핵심 내용 |
|------|------|----------|
| 데이터 전처리·시각화 | class041~080 | NumPy·Pandas·Matplotlib, EDA |
| 프롬프트 엔지니어링 | class353~392 | 역할 설정, 출력 포맷 제어, Few-shot |
| LLM 생성 파라미터 | class296~308 | temperature·top-k·top-p 실습 |

**실습 예시:**
```bash
# 프롬프트 엔지니어링
python promptEng/class353/class353_example1.py

# LM Studio temperature 비교 실습
python llmTextGen/class290/class290_example1.py
```

**주요 개념:**
- `temperature`: 낮을수록 일관적, 높을수록 창의적
- `System prompt`: LLM 에게 역할과 규칙 부여
- `Few-shot`: 예시를 보여줘서 출력 포맷 제어

---

### 레벨 3 — 중급 (LangChain + LM Studio 연동)

> 목표: LangChain 체인 구성, LM Studio 를 백엔드로 서비스 구현

| 모듈 | 범위 | 핵심 내용 |
|------|------|----------|
| LangChain 활용 | class393~448 | Chain, PromptTemplate, OutputParser, Memory |
| 머신러닝 딥다이브 | class081~128 | 지도학습·회귀·분류, 모델 평가 |
| NLP·음성 | class129~288 | 텍스트 임베딩, STT/TTS |

**LM Studio + LangChain 연동 패턴:**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="local-model",   # LM Studio 에서 로드한 모델명
    temperature=0.7,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 금융 상담 AI 어시스턴트입니다."),
    ("user", "{question}"),
])
chain = prompt | llm
response = chain.invoke({"question": "펀드와 ETF 의 차이는?"})
print(response.content)
```

```bash
# LangChain + LM Studio 실습
python langChainLab/class393/class393_example1.py
```

**필요 패키지:**
```bash
pip install langchain-openai
```

---

### 레벨 4 — 심화 (RAG 파이프라인 + Agent)

> 목표: 벡터DB + LM Studio 를 결합한 RAG 시스템, Agent 구축

| 모듈 | 범위 | 핵심 내용 |
|------|------|----------|
| RAG 파이프라인 | class449~500 | 문서 로딩·청킹·임베딩·검색·생성 |
| Finance Agent | Agent/ | RAG+멀티모달+사용자관리 통합 |

**LM Studio RAG 흐름:**
```
문서 로딩 → 청크 분할 → 로컬 임베딩(sentence-transformers)
→ Chroma/Qdrant 저장 → 쿼리 검색 → LM Studio 생성
```

```bash
# RAG + LM Studio 실습
python ragPipeline/class449/class449_example1.py

# Finance Agent (Docker)
cd Agent && cp .env.example .env
# .env 에서 LM_STUDIO_URL 확인 후:
docker compose up -d
curl http://localhost:8954/health
```

**로컬 임베딩 + LM Studio 조합 (권장):**
```python
from sentence_transformers import SentenceTransformer
from lmstudio_config import call_lm

# 임베딩: 로컬 모델 사용 (API 불필요)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# 생성: LM Studio 사용
answer = call_lm([
    {"role": "system", "content": "컨텍스트 기반으로만 답변하세요."},
    {"role": "user", "content": f"컨텍스트: {context}\n\n질문: {query}"},
], temperature=0.2)
```

---

### 레벨 5 — 전문가 (LLMOps + 배포)

> 목표: LLM 서비스 품질 관리, 모니터링, CI/CD 자동화

| 모듈 | 범위 | 핵심 내용 |
|------|------|----------|
| LLMOps | class501~520 | 프롬프트 버전관리, 평가, Prometheus/Grafana |
| 프로젝트 앱 | VoiceModelBuilder, PersonaLLMResponder, PersonaKnowledgeCustomizer | 금융 특화 독립 서비스 |

```bash
# 전체 서비스 스택 (LM Studio + Qdrant + Agent + 보조앱)
docker compose up -d
```

**서비스 포트:**
| 서비스 | 포트 | 설명 |
|--------|------|------|
| LM Studio | 1234 | 로컬 LLM 추론 (호스트 실행) |
| Qdrant | 6333 | 벡터DB (RAG용) |
| Agent API | 8954 | RAG+멀티모달 Agent |
| VoiceModelBuilder | 8951 | 음성 브리핑 스튜디오 |
| PersonaLLMResponder | 8952 | 금융 상품 상담 에이전트 |
| PersonaKnowledgeCustomizer | 8953 | 지식베이스 커스터마이저 |

---

## 권장 LM Studio 모델

| 모델 | 크기 | 특징 | 권장 용도 |
|------|------|------|----------|
| Qwen2.5-7B-Instruct-Q4_K_M | ~4.5GB | 한국어 우수, 빠름 | 레벨 1~3 |
| Qwen2.5-14B-Instruct-Q4_K_M | ~9GB | 고품질 한국어 | 레벨 3~4 |
| Phi-3.5-mini-instruct-Q4_K_M | ~2.4GB | 경량, 저사양 PC용 | 입문 |
| Llama-3.2-3B-Instruct-Q4_K_M | ~2GB | 영어 중심, 빠름 | 코드 생성 |
| mistral-7b-instruct-v0.3 | ~4.1GB | 균형 잡힌 성능 | 범용 |

> GPU 없는 PC: Q4_K_M (4비트 양자화) 모델 권장  
> GPU 8GB+: Q5_K_M 이상으로 품질 개선 가능

---

## 환경 설정

### 가상환경 생성 및 패키지 설치

```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Linux / macOS / WSL
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 환경 변수 (선택)

기본값으로 동작하지만 변경이 필요한 경우:

```bash
# .env 파일 생성 또는 셸에서 export
export LM_STUDIO_URL=http://localhost:1234/v1   # 기본값
export LM_STUDIO_MODEL=Qwen2.5-7B-Instruct      # LM Studio 에서 로드한 모델명
```

---

## Docker 실행 (레벨 4~5)

```bash
# 1. LM Studio 를 호스트에서 실행 (포트 1234)
# 2. 환경 파일 준비
cp Agent/.env.example Agent/.env
# Agent/.env 에서 LM_STUDIO_MODEL 을 실제 로드한 모델명으로 수정

# 3. 서비스 실행
docker compose up -d

# 4. 확인
docker compose ps
curl http://localhost:8954/health
```

---

## 저장소 구조

```
ai-agent-lab/
├── lmstudio_config.py          ← LM Studio 공통 클라이언트 (모든 예제에서 import)
├── requirements.txt            ← 패키지 목록 (openai 포함)
├── docker-compose.yml          ← LM Studio + Qdrant + 서비스 스택
│
├── pyBasics/     class001~040  [레벨 1] Python 기초
├── dataVizPrep/  class041~080  [레벨 2] 데이터 전처리·시각화
├── mlDeepDive/   class081~128  [레벨 3] 머신러닝·딥러닝
├── nlpSpeechAI/  class129~224  [레벨 3] NLP·음성
├── speechTtsStt/ class225~288  [레벨 3] STT/TTS
├── llmTextGen/   class289~352  [레벨 1~2] LLM 개요·생성·파라미터
├── promptEng/    class353~392  [레벨 2] 프롬프트 엔지니어링
├── langChainLab/ class393~448  [레벨 3] LangChain + LM Studio
├── ragPipeline/  class449~500  [레벨 4] RAG 파이프라인
├── llmOps/       class501~520  [레벨 5] LLMOps·모니터링·배포
│
├── Agent/                      [레벨 4~5] Finance RAG Agent (FastAPI)
├── VoiceModelBuilder/          [레벨 5] 음성 브리핑 프로젝트
├── PersonaLLMResponder/        [레벨 5] 페르소나 LLM 응답 프로젝트
├── PersonaKnowledgeCustomizer/ [레벨 5] 지식베이스 커스터마이저 프로젝트
└── docs/                       운영 가이드·강사 노트
```

---

## 수업 실행 명령

```bash
# 특정 클래스 실행
./run_class.sh class289

# Day 단위 실행
./run_day.sh 37 launcher   # 37일차 런처
./run_day.sh 37 solution   # 37일차 정답

# 웹 실습 UI (pyBasics 제외 모든 과목)
cd llmTextGen/class289
uvicorn server:app --reload
# 브라우저: http://127.0.0.1:8000
```

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 로컬 LLM | LM Studio (GGUF 모델, OpenAI 호환 API) |
| LLM SDK | `openai>=1.30` (LM Studio / OpenAI 공통) |
| LLM 프레임워크 | LangChain · LangGraph |
| 임베딩 | `sentence-transformers` (로컬, 무료) |
| 벡터DB | Chroma (로컬) · Qdrant (Docker) |
| API 서버 | FastAPI · Uvicorn |
| 데이터 | NumPy · Pandas · Matplotlib |
| ML | scikit-learn |
| 컨테이너 | Docker · Docker Compose |
| 인프라 (선택) | AWS · Kubernetes/EKS |

---

## VS Code 권장 확장

- `Python` (`ms-python.python`)
- `Pylance` (`ms-python.vscode-pylance`)
- `Markdown All in One` (`yzhang.markdown-all-in-one`)
- `Markdown Preview Mermaid Support` (`bierner.markdown-mermaid`)
- `Live Server` (`ritwickdey.LiveServer`)
- `Docker` (`ms-azuretools.vscode-docker`)

---

## 라이선스

본 교육 자료의 저작권 및 라이선스 권한은 **에듀엠지티 (www.edumgt.co.kr)** 에 있습니다.
교육, 사내공유, 외부배포, 상용활용 등 형태와 관계없이 사용 전 **사전 안내/승인**이 필요합니다.
