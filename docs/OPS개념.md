# DevOps / MLOps / AIOps / LLMOps 정리 보고서

## 1. 개요

본 문서는 DevOps, MLOps, AIOps의 개념 차이와 주요 도구의 오픈소스 여부를 정리하고, 추가로 AI Agent 개발, RAG 구성, 배포가 어느 영역에 포함되는지까지 함께 정리한 보고서용 요약 자료이다.

---

## 2. DevOps / MLOps / AIOps / LLMOps 비교

| 구분 | DevOps | MLOps | AIOps | LLMOps / AI Engineering |
|---|---|---|---|---|
| 정의 | 개발(Development)과 운영(Operations)을 통합하여 소프트웨어를 빠르고 안정적으로 배포·운영하는 방식 | 머신러닝 모델의 데이터 준비, 학습, 배포, 운영, 재학습까지 전 과정을 체계적으로 관리·자동화하는 방식 | AI/ML을 활용해 운영 데이터를 분석하고 장애를 예측·탐지·분석·자동 대응하는 운영 방식 | 대규모 언어모델(LLM) 기반 서비스의 프롬프트, 체인, 에이전트, 평가, 배포, 운영을 관리하는 방식 |
| 목적 | 배포 속도 향상, 품질 안정화, 운영 효율화 | 모델 품질 유지, 재현성 확보, 배포 자동화, 지속적 개선 | 장애 조기 탐지, 원인 분석 고도화, 운영 자동화, 서비스 안정성 향상 | 생성형 AI 서비스 품질 향상, 응답 일관성 확보, 안전성 강화, 운영 자동화 |
| 주요 대상 | 애플리케이션 코드, 인프라, CI/CD 파이프라인 | 데이터셋, 피처, 학습 코드, 모델, 실험 이력, 추론 서비스 | 로그, 메트릭, 트레이스, 이벤트, 알림, 운영 이력 | 프롬프트, 벡터DB, 임베딩, 체인, 툴 호출, 에이전트 워크플로, 평가 결과 |
| 핵심 활동 | 자동 빌드, 테스트, 배포, IaC, 모니터링, 장애 대응 | 데이터·모델 버전관리, 실험 추적, 학습 파이프라인, 모델 배포, 드리프트 모니터링 | 이상 탐지, 이벤트 상관분석, 원인 분석(RCA), 이상 패턴 분석, 자동 복구 | 프롬프트 엔지니어링, RAG 파이프라인 구성, 에이전트 설계, 평가, 가드레일, 응답 품질 모니터링 |
| 대표 오픈소스 도구 | Jenkins, Kubernetes | MLflow, Kubeflow, Airflow, DVC | Prometheus, Grafana, OpenTelemetry, Jaeger, OpenSearch 조합 | LangChain 일부 생태계, Haystack, Open WebUI, LiteLLM 일부 활용 조합 |
| 대표 상용/관리형 도구 | GitHub Actions, Docker Desktop, Terraform Cloud 계열 | SageMaker | Datadog, Dynatrace, New Relic, Splunk | OpenAI API 기반 플랫폼, Azure OpenAI, Vertex AI, Bedrock 등 |
| 산출 효과 | 안정적인 애플리케이션 릴리스와 운영 자동화 | 신뢰할 수 있는 모델 운영과 지속적 성능 관리 | 장애 감소, MTTR 단축, 운영 인사이트 강화 | AI Agent 및 RAG 서비스의 품질 향상, 운영 체계화, 비용·응답 최적화 |
| 핵심 질문 | “애플리케이션을 어떻게 더 빠르고 안전하게 배포할 것인가?” | “모델을 어떻게 지속적으로 학습·배포·관리할 것인가?” | “운영 장애를 어떻게 더 빨리 탐지하고 자동 대응할 것인가?” | “LLM 기반 서비스를 어떻게 안정적으로 설계·평가·운영할 것인가?” |

---

## 3. 주요 도구의 오픈소스 여부

| 도구 | 영역 | 오픈소스 여부 | 설명 |
|---|---|---|---|
| Jenkins | DevOps | 오픈소스 | 오픈소스 자동화 서버로 제공됨 citeturn0search0 |
| Kubernetes | DevOps | 오픈소스 | 대표적인 오픈소스 컨테이너 오케스트레이션 플랫폼 citeturn0search1 |
| Docker | DevOps | 혼합 | Docker Engine은 오픈소스, Docker Desktop은 상용 라이선스 조건 존재 citeturn0search2turn0search10 |
| GitHub Actions | DevOps | 상용 서비스 중심 | GitHub 플랫폼에 포함된 CI/CD 서비스 citeturn0search3 |
| Terraform | DevOps | 완전 오픈소스 아님 | 현재 source-available 성격으로 보는 것이 적절 citeturn0search4 |
| MLflow | MLOps | 오픈소스 | 실험 추적, 모델 관리, 평가 기능 제공 citeturn0search5 |
| Kubeflow | MLOps | 오픈소스 | Kubernetes 기반 머신러닝 워크플로 플랫폼 citeturn0search6 |
| Airflow | MLOps | 오픈소스 | Apache 오픈소스 워크플로 오케스트레이션 도구 citeturn0search7 |
| DVC | MLOps | 오픈소스 | 데이터 및 모델 버전관리 도구 citeturn0search8 |
| SageMaker | MLOps | 상용 서비스 | AWS의 관리형 머신러닝 서비스 citeturn0search9 |
| Datadog | AIOps | 상용 서비스 | 관측성 및 모니터링 SaaS 플랫폼 citeturn0search11 |
| Dynatrace | AIOps | 상용 서비스 | 엔터프라이즈 관측성 및 AIOps 플랫폼 citeturn0search12 |
| New Relic | AIOps | 상용 서비스 | 상용 관측성 플랫폼 citeturn0search13 |
| Splunk | AIOps | 상용 서비스 | 로그, 보안, 관측성 중심의 상용 제품군 citeturn0search14 |

---

## 4. AI Agent 개발, RAG 구성, 배포의 포함 영역

| 항목 | 주로 포함되는 영역 | 설명 |
|---|---|---|
| AI Agent 개발 | LLMOps / AI Engineering / MLOps | 프롬프트 설계, 툴 호출, 메모리, 멀티스텝 워크플로, 평가, 모델 선택, 가드레일 설계 등을 포함 |
| RAG 구성 | LLMOps / MLOps + Data Engineering | 문서 수집, 정제, chunking, embedding, 벡터DB 적재, retrieval 튜닝, reranking, grounding 품질 평가 등을 포함 |
| 배포 | DevOps | Docker 이미지 생성, CI/CD, Kubernetes 배포, Terraform, API Gateway 연동, Secret 관리, Auto Scaling 등을 포함 |
| 운영 중 이상 탐지/자동 대응 | AIOps + Observability | 로그·메트릭·트레이스 분석, 비용 이상 감지, 장애 예측, 자동 복구, 원인 분석 등을 포함 |

---

## 5. 실무 관점 요약

| 관점 | 포함 영역 | 핵심 설명 |
|---|---|---|
| 애플리케이션을 배포하고 운영 자동화 | DevOps | 앱 코드와 인프라를 빠르고 안정적으로 배포하고 운영하는 데 집중 |
| 머신러닝 모델을 학습·배포·재학습 | MLOps | 데이터와 모델의 전체 생명주기를 재현 가능하게 관리 |
| 운영 장애를 예측·탐지·자동 대응 | AIOps | 운영 데이터를 AI/ML로 분석하여 장애 대응 속도와 정확도를 높임 |
| 생성형 AI 서비스와 에이전트 품질 관리 | LLMOps / AI Engineering | 프롬프트, RAG, 에이전트, 평가, 안전성, 비용, 응답 품질을 관리 |

---

## 6. 보고서용 서술 문안

DevOps는 소프트웨어 애플리케이션의 빌드, 테스트, 배포, 운영을 자동화하고 안정화하는 데 초점을 둔다. MLOps는 여기에 데이터와 모델의 생명주기 관리까지 포함하여 머신러닝 시스템을 지속적으로 운영 가능하게 만든다. AIOps는 운영 과정에서 수집되는 로그, 메트릭, 트레이스, 이벤트 데이터를 AI/ML로 분석하여 이상 탐지, 원인 분석, 자동 복구를 지원하는 개념이다. 한편, 생성형 AI 서비스 확산과 함께 LLMOps 또는 AI Engineering이라는 개념이 중요해졌으며, 이는 프롬프트 설계, RAG 구성, AI Agent 개발, 평가, 가드레일, 서비스 운영까지 포괄하는 영역으로 볼 수 있다.

AI Agent 개발과 RAG 구성은 전통적인 DevOps만으로 설명하기 어렵고, 일반적으로 LLMOps 또는 MLOps 범주에 포함된다. 특히 프롬프트 설계, 벡터 데이터베이스 운영, 임베딩 파이프라인, 검색 품질 개선, 응답 평가 같은 요소가 핵심이기 때문이다. 반면, 이를 실제 서비스 환경에 배포하고 CI/CD 파이프라인과 인프라 운영 체계에 반영하는 작업은 DevOps에 해당한다. 또한 운영 중 발생하는 장애 탐지, 성능 이상 분석, 비용 급증 감시, 자동 복구와 같은 활동은 AIOps 및 관측성(Observability) 영역과 밀접하게 연결된다.

즉, DevOps는 애플리케이션 전달, MLOps는 모델 전달, LLMOps는 생성형 AI 전달, AIOps는 운영 최적화에 각각 초점을 둔다고 정리할 수 있다.

---

## 7. 발표용 한 줄 요약

- DevOps: 애플리케이션을 빠르고 안정적으로 배포하는 체계
- MLOps: 머신러닝 모델을 지속적으로 학습·배포·운영하는 체계
- AIOps: 운영 데이터를 AI로 분석해 장애를 예측·탐지·자동 대응하는 체계
- LLMOps: 생성형 AI, RAG, AI Agent를 안정적으로 설계·평가·운영하는 체계

---

## 8. 커리큘럼 접목 점검 및 반영 (3개 독립 프로젝트 앱)

현재 저장소 프로젝트는 `Agent/`와 동일하게 루트 상위 독립 앱 3개(`VoiceModelBuilder`, `PersonaLLMResponder`, `PersonaKnowledgeCustomizer`)로 구성되며, 본 보고서의 핵심 축(DevOps/MLOps/AIOps/LLMOps)에 맞춰 다음과 같이 접목했다.

| 프로젝트 앱 | 프로젝트 주제 | 보고서 접목 축 | 핵심 반영 포인트 |
|---|---|---|---|
| VoiceModelBuilder (`project001`) | 금융 상담 음성 브리핑 스튜디오 | DevOps + MLOps | 음성 브리핑 프로필/품질 파이프라인 구성, API 서빙 및 실행 자동화 |
| PersonaLLMResponder (`project002`) | 금융 상품 상담 에이전트 | LLMOps / AI Engineering | 상담 페르소나 규칙 설계, 프롬프트 기반 응답, LLM/로컬 fallback 운영 |
| PersonaKnowledgeCustomizer (`project003`) | 금융 지식베이스 커스터마이저 | LLMOps + RAG + AIOps | 금융 지식 업서트/검색/근거 응답, 로그 기반 품질 점검 및 개선 루프 |

정리하면, 현재 프로젝트 앱 3종은 본 보고서 2장(개념 비교), 4장(영역 포함), 5장(실무 요약), 7장(핵심 요약)을 실제 구현 단위로 연결한 운영형 프로젝트 트랙이다.
