<!-- 이 파일은 www.edumgt.co.kr 의 에듀엠지티에 저작권이 있습니다 -->
# Finance AI Agent Lab
 
금융 도메인 에이전트 실습을 위한 Python 기반 저장소입니다.  
RAG, 멀티모달, 음성 브리핑, 금융 지식베이스, 상품/리서치 응답 자동화를 한 저장소에서 실험할 수 있도록 구성했습니다.

RAG 대상 - https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=data&dataSetSn=71938

### 핵심 목표

1. 금융 문서 검색과 근거 기반 답변 에이전트 구축
2. 상품 설명, 심사/리스크 체크, 리서치 요약을 위한 LLM 워크플로우 실습
3. Python 백엔드 + 바닐라 HTML 프런트엔드 기반 멀티모달 서빙
4. LangChain/LangGraph/RAG/LLMOps 아키텍처를 금융 시나리오에 맞춰 검증
5. Docker, AWS, On-Prem 환경까지 고려한 서비스형 Agent Lab 운영

### 운영 방식

1. 금융 시나리오 중심 예제와 API를 빠르게 실행하고 검증
2. 문서, 코드, 설정 변경을 Git 기반으로 축적해 RAG 지식 원천으로 활용
3. 프로젝트 앱 단위로 브리핑, 상담, 지식 커스터마이징 기능을 독립 실험
4. 결과물은 Markdown, JSON, API 응답 형태로 남겨 재현성과 검토 가능성 확보
5. 필요 시 외부 검색, 리랭킹, 멀티모달 API를 결합해 실제 운영 패턴 검증

### 저장소 활용 방향

1. `Agent/`는 금융 Q&A/RAG 허브 역할을 수행합니다.
2. `VoiceModelBuilder/`, `PersonaLLMResponder/`, `PersonaKnowledgeCustomizer/`는 금융 특화 보조 앱입니다.
3. 기존 과목형 실습 폴더는 Python/LLM/RAG 기초를 다지는 참고 모듈로 유지합니다.
4. 모든 신규 예시는 가상 아이디 기반 모의 캡처 없이 텍스트/코드 중심으로 관리합니다.

---

최종 목표: `Agent/` 중심의 금융 에이전트 실험실을 단계별로 구축하고, 보조 앱까지 포함한 실무형 레퍼런스를 축적하는 것입니다.

기존 학습 모듈(`class001`~`class520`)은 Python, 데이터, LLM, RAG, LLMOps 기초를 익히는 참고 자료로 유지하고, 프로젝트 과목은 루트의 3개 독립 앱(`VoiceModelBuilder`, `PersonaLLMResponder`, `PersonaKnowledgeCustomizer`)으로 금융 시나리오를 실험합니다.

## 1) 현재까지 반영된 핵심 작업
- 금융 Agent 허브(`Agent/`)와 보조 앱 3종 운영
- Python/LLM/RAG/LLMOps 기초 모듈 유지
- Markdown, Mermaid, 실행 예제 중심의 실습 자료 구조화
- 예제/퀴즈/런처/웹 서빙 파일 체계 정비

## 2) 기술 스택
- Language: `Python 3.10+` (권장 3.11)
- Data/ML: `numpy`, `pandas`, `matplotlib`, `scikit-learn`
- API/Serving: `fastapi`, `uvicorn`, `pydantic`
- AI/LLM: `langchain`, `langchain-community`, `langgraph`
- Speech: `pyttsx3`, `SpeechRecognition`
- Utility: `requests`, `Pillow`
- Docs: `Markdown`, `Mermaid`
- Dev Tools: `VS Code`, `Git`, `GitHub`, `ChatGPT`, `Codex`
- Optional Infra: `Docker`, `Docker Compose` (RAG/LLM 실습용)

## 3) 저장소 구조
- 과목별 상위 폴더(영문 camelCase) 아래에 `classXXX/` 배치
- `classXXX/` 기본 구성(모든 과목 공통)
  - `classXXX.md`: 자기주도 학습 가이드
  - `classXXX_flow.png`: 차시 흐름도 PNG
  - `classXXX.py`: 실행 런처
  - `classXXX_example1.py` ~ `classXXX_example5.py`: 단계형 실습 예제
  - `classXXX_solution.py`: 정답/레퍼런스 코드
  - `classXXX_quiz.html`: 퀴즈
  - `instructor_notes.md`: 강사용 노트
- 웹 실습 구성(`pyBasics` 제외 과목 공통)
  - `server.py`: FastAPI 백엔드(예제 실행/소스 조회 API)
  - `client.html`: Vanilla JS + Tailwind 기반 실습 UI
- 보조/운영 파일
  - `tools/`: 콘텐츠 재생성/검증 스크립트
  - `docs/`: 운영 가이드/채점 가이드/부가 문서
  - `curriculum_index.csv`: 기존 학습 모듈 인덱스
  - `VoiceModelBuilder/`, `PersonaLLMResponder/`, `PersonaKnowledgeCustomizer/`: 금융 특화 프로젝트 앱(FastAPI + Vanilla JS + Docker)
  - `project/`: 프로젝트 인덱스/매니페스트

## 3-1) 과목 폴더 매핑 및 상세 학습 내용
| 과목명 | 폴더명(camelCase) | class 범위 | 상세 학습 내용 |
| --- | --- | --- | --- |
| Python 프로그래밍 | `pyBasics` | class001~class040 | 변수/자료형/함수 기초 이후, **웹 프론트엔드 기초(HTML/CSS/Vanilla JS)**, **Tailwind CSS UI 모듈 제작**, 외부 라이브러리 활용, API 개념/HTTP, FastAPI·Uvicorn 서버 구현, OpenAPI 명세 문서화까지 개발자 중심으로 구성 |
| Python 전처리 및 시각화 | `dataVizPrep` | class041~class080 | 데이터 분석 개요부터 NumPy/Pandas, 데이터 정제·가공, EDA, Matplotlib/Seaborn 시각화, 통합 실습까지 단계형 구성 |
| 머신러닝과 딥러닝 | `mlDeepDive` | class081~class128 | 지도학습, 회귀/분류, 모델 평가, 특성공학, 과적합 제어, 신경망 기초와 실전 예측 프로젝트 |
| 자연어 및 음성 데이터 활용 및 모델 개발 | `nlpSpeechAI` | class129~class224 | 텍스트 토큰화/임베딩과 음성 데이터 전처리를 통합해 NLP·Speech 모델 파이프라인 설계 |
| 음성 데이터 활용한 TTS와 STT 모델 개발 | `speechTtsStt` | class225~class288 | 발화/화자 데이터 구성, 오디오 특징 추출, STT·TTS 모델 구성/평가, 품질 개선 루프 실습 |
| 거대 언어 모델을 활용한 자연어 생성 | `llmTextGen` | class289~class352 | LLM 구조/Transformer/토큰·컨텍스트, 확률 기반 생성(temperature/top-k/top-p), API·오픈모델·클라우드/로컬 추론, 생성 작업(요약·Q&A·번역·문서·코드·추출), 품질 제어(JSON·톤·길이·오류 처리), 한계/주의(사실성·최신성·보안·검증)까지 통합 실습 |
| 프롬프트 엔지니어링 | `promptEng` | class353~class392 | 역할/맥락/출력형식 설계, 템플릿화, 평가 기준 수립, 실전 프롬프트 튜닝 전략 |
| Langchain 활용하기 | `langChainLab` | class393~class448 | 체인 구성, PromptTemplate/OutputParser, 메모리/도구 연결, LangGraph 상태 흐름, LangSmith 추적 기반 서비스형 워크플로우 구현 |
| RAG(Retrieval-Augmented Generation) | `ragPipeline` | class449~class500 | 문서 로딩/청크, 임베딩·벡터검색, 근거 결합 응답, 출처 기반 검증까지 RAG 전체 파이프라인 구현 |
| **LLMOps** | `llmOps` | **class501~class520** | LLMOps 개요, 프롬프트 버전관리, LLM 평가·품질관리, 모니터링·관측성, 배포 자동화(CI/CD·Blue-Green·Canary)까지 Lab 스타일 실습 |
| 프로젝트 앱 | `VoiceModelBuilder`, `PersonaLLMResponder`, `PersonaKnowledgeCustomizer` | 독립 앱 3종 | 금융 상담 음성 브리핑, 상품/리서치 응답, 금융 지식베이스 커스터마이징을 각각 독립 서비스로 실습 |

### 3-1-1) dataVizPrep 7단계 구성(요청 반영)
| 단계 | 핵심 내용 | class 범위 |
| --- | --- | --- |
| 1. 데이터 분석 개요 | 데이터 분석 프로세스, 정형/비정형, CSV·Excel·JSON 구조, 분석용 Python 생태계 | class041~044 |
| 2. NumPy 기초 | 배열(Array), list vs ndarray, 벡터화, 인덱싱/슬라이싱, 기초 통계 연산 | class045~048 |
| 3. Pandas 기초 | Series/DataFrame, 데이터 로딩·저장, 행/열 선택, 조건 필터링, 정렬, 기초 통계 | class049~052 |
| 4. 데이터 정제 | 결측치 처리, 중복 제거, 타입 변환, 문자열 정리, 날짜형 처리, 컬럼명 정리 | class053~060 |
| 5. 데이터 가공 | 파생변수, groupby, aggregation, merge/join, pivot table, 범주형 처리 | class061~068 |
| 6. EDA | 분포, 평균·중앙값·표준편차, 상관관계, 패턴 탐색, 문제 정의·가설 설정 | class073~076 |
| 7. 데이터 시각화 기초 | 시각화 원칙, Matplotlib 문법, line/bar/scatter/histogram, 한글 폰트, 제목·축·범례 | class069~072 |

### 3-1-2) llmTextGen 7단계 구성(요청 반영)
학습 목표:
- LLM의 구조와 개념 이해
- 생성형 AI가 텍스트를 만드는 방식 이해
- API 또는 오픈모델 기반 자연어 생성 실습
- 서비스형 AI 기능 구현 역량 확보

| 단계 | 핵심 내용 | class 범위(주요 모듈) |
| --- | --- | --- |
| 1. LLM 개요 | LLM 정의, 기존 NLP 대비 차이, Transformer, 토큰/컨텍스트, 사전학습·파인튜닝 | class289~295 (`LLM 개요`) |
| 2. 자연어 생성 원리 | 다음 토큰 예측, 확률 기반 생성, temperature·top-k·top-p, hallucination, 문맥 유지 | class296~308 (`토큰/컨텍스트 이해`, `생성 파라미터`) |
| 3. LLM 활용 방식 | API 기반, 오픈소스 모델, 클라우드/로컬 추론, 비용·성능·보안 고려 | class334~346 (`도메인 적용 시나리오`, `API 연동 실습`) |
| 4. 생성 작업 유형 | 요약, 질의응답, 번역, 문서 작성, 코드 생성, 분류/정보추출 | class315~320 (`요약/분류/추출`) |
| 5. 실습 | 기본 프롬프트 생성, 문서 요약, 이메일/보고서 초안, 챗봇 응답, 규칙 기반 vs LLM 비교 | class309~327 (`프롬프트 기반 생성`, `대화형 응답 설계`) |
| 6. 품질 제어 | 출력 형식 제어, JSON 응답 강제, 길이/톤/스타일 제어, 오류 응답 처리 | class321~327, class341~352 (`대화형 응답 설계`, `API/Agent 통합`) |
| 7. 한계와 주의사항 | 사실성 문제, 최신성 한계, 보안/개인정보, 프롬프트 민감성, 실무 검증 필요성 | class328~333 (`안전성/환각 관리`) |

### 3-1-3) ragPipeline 8단계 구성(요청 반영)
학습 목표:
- RAG의 필요성과 구조 이해
- 외부 문서를 검색해서 LLM 답변 품질 개선
- 벡터DB, 임베딩, 검색 파이프라인 개념 습득
- 사내 문서 Q&A 시스템 구현 역량 확보

| 단계 | 핵심 내용 | class 범위(주요 모듈) |
| --- | --- | --- |
| 1. RAG 개요 | 왜 RAG가 필요한가, LLM 단독 한계, 최신/사내 정보 활용, 검색+생성 결합 구조 | class449~454 (`RAG 개요`) |
| 2. RAG 전체 구조 | 문서 수집, 문서 분할, 임베딩 생성, 벡터 저장, 검색, 프롬프트 주입, 답변 생성 | class455~459 (`문서 수집 전략`) |
| 3. 임베딩 이해 | 임베딩 개념, 문장 의미 벡터, 유사도 검색, cosine similarity, 모델 선택 기준 | class465~469 (`임베딩 생성`) |
| 4. 문서 전처리와 Chunking | PDF/TXT/HTML/CSV 처리, 문서 구조 보존, chunk 크기/overlap, 메타데이터 관리 | class460~464 (`문서 청크 설계`) |
| 5. 벡터DB와 검색 | Chroma/FAISS/Qdrant 개요, 인덱싱, Top-K 검색, reranking, 검색 실패 분석 | class470~480 (`벡터DB 기초`, `검색 품질 개선`) |
| 6. LangChain과 RAG 연결 | Retriever 구성, Prompt 문맥 주입, 검색 기반 답변 생성, source 반환, hallucination 감소 | class481~490 (`프롬프트 결합`, `응답 검증/출처화`) |
| 7. 평가와 개선 | 검색 정확도, 답변 정확도, chunking 개선, 프롬프트 튜닝, 하이브리드 검색 | class491~495 (`평가 지표 설계`) |
| 8. 실습 | 사내 문서 질의응답, FAQ 챗봇, PDF 검색 시스템, 출처 포함 답변 생성 | class496~500 (`Agent 시스템 통합 구현`) |

### 3-1-4) llmOps 5단계 구성 *(신규)*
학습 목표:
- LLMOps 개념과 DevOps/MLOps와의 차이 이해
- 프롬프트 버전관리·A/B 테스트 역량 습득
- LLM 서비스 품질 평가 자동화 파이프라인 구성
- Prometheus/Grafana 기반 모니터링·관측성 실습
- CI/CD·Blue-Green·Canary 기반 LLM 배포 자동화 구현

| 단계 | 핵심 내용 | class 범위 |
| --- | --- | --- |
| 1. LLMOps 개요 | LLMOps 정의, DevOps·MLOps와의 차이, 핵심 구성요소(프롬프트·평가·모니터링·가드레일), 드리프트 관리 | class501~504 |
| 2. 프롬프트 관리 | 프롬프트 버전관리, 템플릿화, A/B 테스트, Chain-of-Thought, 프롬프트 인젝션 방어 | class505~508 |
| 3. LLM 평가와 품질 | BLEU/Faithfulness/Answer Relevance, 자동 평가 파이프라인, LLM-as-Judge, 지속적 품질 관리 | class509~512 |
| 4. LLM 모니터링 | Prometheus·Grafana 메트릭, 토큰·지연·오류율 추적, 이상 탐지, SLO 설정, Circuit Breaker | class513~516 |
| 5. LLM 배포 자동화 | CI/CD 파이프라인, Docker 패키징, K8s HPA, Blue-Green/Canary 배포, IaC, Secret 관리 | class517~520 |

## 3-2) 실무 배포 트랙 (OnPrem + AWS + K8s/EKS)
| 트랙 | class 범위 | 핵심 학습 항목 | 운영/배포 결과물 |
| --- | --- | --- | --- |
| 로컬/OnPrem 개발 표준화 | class001~class128 | 가상환경, 의존성 잠금, Docker 이미지 빌드, API 기본 서빙 | OnPrem 서버에서 재현 가능한 Python 서비스 |
| ML 학습·추론 분리 | class081~class224 | 모델 학습 파이프라인, 추론 API, 배치/실시간 추론 전략 | 학습 잡 + 추론 서버 분리 배포 |
| LLM/Prompt 서비스화 | class289~class448 | 외부 라이브러리(LangChain 등) 통합, 안전한 응답 정책, 관측성 | LLM 기반 백엔드 API 운영 |
| 프로젝트 통합 운영 | VoiceModelBuilder / PersonaLLMResponder / PersonaKnowledgeCustomizer | 음성 모델 생성, PERSONA 답변, 사전 데이터 기반 커스텀 파이프라인을 독립 개발 후 통합 운영 | 음성 AI 서비스 핵심 컴포넌트를 분리 설계하고 운영 자동화까지 연결 |

## 3-2-1) 프로젝트 과목과 보고서 접목
- 기준 문서: [OPS개념.md](/home/Python-AI_Agent-Class/docs/OPS개념.md)
- `VoiceModelBuilder`: 개인 맞춤 코칭 음성 모델 구축(프로필/학습 품질/합성 프리뷰)
- `PersonaLLMResponder`: 거대 언어 모델 기반 PERSONA 답변 기능 구현(페르소나 규칙/응답 생성)
- `PersonaKnowledgeCustomizer`: 사전 데이터 기반 PERSO 답변 커스텀(지식 업서트/검색/근거 기반 응답)

## 3-3) 공공 데이터·API Hub 연계 학습
- 공공데이터포털(`data.go.kr`) OpenAPI: 교통/환경/인구 등 API 수집, 전처리, 시각화, 예측 실습
- AI Hub(한국지능정보사회진흥원) 데이터셋: 한국어 텍스트/음성 데이터 기반 NLP·STT·TTS 모델 실습
- 권장 방식: 수집기(배치) + 추론 API(실시간) + 대시보드(모니터링)로 구성해 OnPrem/AWS 모두 배포


## 3-4) ML/DL 실사례 Docker 이미지 활용
| 용도 | 권장 이미지 | 빠른 시작 명령 | 학습 포인트 |
| --- | --- | --- | --- |
| PyTorch 학습 환경 | `pytorch/pytorch` | `docker pull pytorch/pytorch` | CUDA/CPU 태그 선택, 실험 재현성 확보 |
| TensorFlow 모델 서빙 | `tensorflow/serving` | `docker run -p 8501:8501 tensorflow/serving` | REST/gRPC 추론 엔드포인트 운영 |
| 고성능 추론 서버 | NVIDIA Triton (NGC) | `docker run --gpus=all ... nvcr.io/nvidia/tritonserver:<tag>` | 다중 프레임워크 추론 통합, GPU 최적화 |
| 실험 추적/모델 레지스트리 | `ghcr.io/mlflow/mlflow` | `docker pull ghcr.io/mlflow/mlflow` | 실험/아티팩트/모델 버전 관리 |
| 워크플로우 오케스트레이션 | `apache/airflow` | `docker compose up` (공식 quick-start) | 학습/배치 파이프라인 자동화 |

- 원칙: 태그는 `latest` 고정보다 안정 버전 태그를 명시해 재현성 유지
- 권장: 학습 단계(로컬 Docker Compose) → 운영 단계(Kubernetes/EKS)로 승격
- 공식 참고 링크:
  - PyTorch Docker Hub: https://hub.docker.com/r/pytorch/pytorch
  - TensorFlow Serving Docker 가이드: https://www.tensorflow.org/tfx/serving/docker
  - NVIDIA Triton 컨테이너(공식): https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/deploy.html
  - MLflow Docker 이미지(GHCR): https://github.com/mlflow/mlflow/pkgs/container/mlflow
  - Apache Airflow Docker Compose Quick Start: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
  - KServe(쿠버네티스 모델서빙): https://kserve.github.io/website/latest/
  - Prometheus Docker 설치: https://prometheus.io/docs/prometheus/latest/installation/
  - Grafana Docker 설치: https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/

## 3-5) MLOps + AIOps 운영 학습 축
1. MLOps: 데이터/코드/모델 버전관리, 학습-검증-배포 자동화, 모델 레지스트리 운영
2. Model Serving: FastAPI + TF Serving/Triton/KServe 중 용도별 선택
3. Observability(AIOps): Prometheus 메트릭, Grafana 대시보드, 로그/알람 기반 이상탐지
4. Reliability: 롤백 가능한 배포 전략(Blue-Green/Canary), SLO·에러버짓 기반 운영
5. Runbook: 장애 재현 절차, 복구 체크리스트, 운영 인수 문서화

## 3-5-1) DevOps / MLOps / AIOps 구분
| 구분 | DevOps | MLOps | AIOps |
| --- | --- | --- | --- |
| 목적 | 개발(Dev)과 운영(Ops)을 통합해 배포 속도와 안정성 향상 | 모델의 학습-배포-운영 전 과정을 자동화하고 품질 유지 | AI/ML로 운영 데이터를 분석해 장애 예측/탐지/자동 대응 |
| 대상 | 애플리케이션 코드, 인프라, CI/CD 파이프라인 | 데이터셋, 피처, 학습 코드, 모델 아티팩트, 추론 서비스 | 로그, 메트릭, 트레이스, 알림 이벤트 등 운영 관측 데이터 |
| 핵심 활동 | 자동 빌드/테스트/배포, IaC, 모니터링, 장애 대응 | 데이터/모델 버전관리, 실험 추적, 모델 배포, 드리프트 모니터링 | 이상 탐지, 이벤트 상관분석, 원인 분석(RCA), 자동 복구 |
| 대표 도구 | GitHub Actions, Jenkins, Docker, Kubernetes, Terraform | MLflow, Kubeflow, Airflow, DVC, SageMaker | Datadog, Dynatrace, New Relic, Splunk |

- 한 줄 요약
  - `DevOps`: 소프트웨어 전달 프로세스 자동화
  - `MLOps`: 모델 생명주기(학습-배포-운영) 자동화
  - `AIOps`: 운영 자체를 AI로 지능화해 장애 대응 자동화

## 3-6) Docker 이미지 목록 및 캡처 표준
- 수업에서 사용하는 Docker 이미지 목록: [도커목록.md](/home/Python-AI_Agent-Class/docs/도커목록.md)
- 화면 캡처 표준: `mcr.microsoft.com` 계열 Docker 이미지를 사용해 캡처 수행

## 4) 사전 준비 (필수 설치)

### 4.0 필수 플랫폼 가입 목록 (수업 시작 전)
| 구분 | 플랫폼 | 가입/준비 목적 | 필수 여부 |
| --- | --- | --- | --- |
| 코드/형상관리 | GitHub (`github.com`) | 저장소 접근, 과제 제출, 협업 PR | 필수 |
| AI 어시스턴트 | ChatGPT (`chatgpt.com`) | 코드 리뷰, 문서 정리, 실습 보조 | 필수 |
| 클라우드 | AWS (`aws.amazon.com`) | S3/ECR/EKS 등 클라우드 실습 | 필수 |
| 공공데이터 | 공공데이터포털 (`data.go.kr`) | OpenAPI 키 발급, 실데이터 수집 실습 | 권장(강력) |
| AI 데이터 | AI Hub (`aihub.or.kr`) | 한국어/음성 데이터셋 실습 | 권장(강력) |
| 컨테이너 레지스트리 | Docker Hub (`hub.docker.com`) | ML/DL 컨테이너 이미지 pull/push | 권장 |
| MLOps 보조 | Weights & Biases (`wandb.ai`) 또는 MLflow | 실험 추적/모델 관리 | 권장 |

### 4.0-1 필수 소프트웨어 설치 목록 (수업 시작 전)
| 구분 | 소프트웨어 | 권장 버전 | 용도 |
| --- | --- | --- | --- |
| 런타임 | Python | 3.11.x | 실습 코드 실행 |
| 편집기 | VS Code | 최신 안정화 | 코드 작성/디버깅 |
| 버전관리 | Git | 최신 안정화 | 커밋/브랜치/협업 |
| 패키지관리 | pip + venv | Python 포함 | 의존성/가상환경 분리 |
| 컨테이너 | Docker Desktop 또는 Docker Engine | 최신 안정화 | 이미지 빌드/서빙 실습 |
| API 테스트 | Postman 또는 Insomnia | 최신 안정화 | API 호출/검증 |
| 클러스터 도구 | kubectl, helm | EKS 호환 버전 | 쿠버네티스 배포 |
| AWS CLI | awscli v2 | 최신 안정화 | AWS 리소스 제어 |

### 4.0-2 기술스택 상세 (개발자 실무 기준)
| 영역 | 기술스택 | 수업 내 사용 맥락 |
| --- | --- | --- |
| Backend/API | FastAPI, Uvicorn, Pydantic | Agent API 서버/명세(OpenAPI) |
| Data/ML | NumPy, Pandas, scikit-learn, PyTorch, TensorFlow | 전처리/학습/추론 |
| LLM/RAG | LangChain, Vector DB(Chroma 등), Prompt Engineering | Agent 질의응답 파이프라인 |
| Frontend | HTML, Tailwind CSS, Vanilla JS | API 검증용 FE 모듈 |
| MLOps | MLflow, Airflow, Docker, Kubernetes, EKS | 실험/배포/운영 자동화 |
| AIOps/Observability | Prometheus, Grafana, CloudWatch, 로그/알람 | 이상탐지/운영 모니터링 |
| Infra as Code(선택) | Terraform | 반복 가능한 인프라 구성 |

### 4.1 VS Code 설치
1. https://code.visualstudio.com 접속
2. 운영체제별 설치 파일 다운로드/설치
3. 실행 후 `File > Open Folder`로 저장소 열기

### 4.2 GitHub 가입
1. https://github.com 가입
2. 이메일 인증
3. 프로필 기본 설정(사용자명/이메일)

### 4.3 ChatGPT 가입
1. https://chatgpt.com 접속
2. 이메일 또는 소셜 계정으로 가입
3. 계정 인증 완료 후 기본 프로필 설정
4. 프로젝트 학습용 대화 폴더(예: `Python-AI-Agent-Class`)를 만들어 관리

### 4.4 Git 설치 및 초기 설정
1. https://git-scm.com/downloads 설치
2. 버전 확인
```bash
git --version
```
3. 사용자 정보 등록
```bash
git config --global user.name "YOUR_NAME"
git config --global user.email "YOUR_EMAIL@example.com"
```

### 4.5 Python 설치
1. https://www.python.org/downloads 설치
2. Windows 설치 시 `Add Python to PATH` 체크
3. 버전 확인
```bash
python --version
```

### 4.6 Docker Desktop 설치 (선택, RAG/LLM 실습용)
1. https://www.docker.com/products/docker-desktop 설치
2. 실행 후 버전 확인
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
