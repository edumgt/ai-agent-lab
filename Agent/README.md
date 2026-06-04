# Agent (Finance RAG + Auth + Multimodal + 3rd-party Integrations)

금융 관련 문서 검색, 상담 보조, 리서치 요약 실험을 위한 FastAPI Agent입니다. 실무형 적용을 위해 주요 외부 API를 바로 붙일 수 있게 확장되어 있습니다.

## 핵심 기능
- RAG 질의응답
  - 로컬 문서 인덱싱(Chroma)
  - 쿼리 확장 + 하이브리드 검색
  - Cohere 리랭킹(선택)
  - Tavily 웹 검색 병합(선택/저신뢰 자동 보강)
- 멀티모달
  - STT: OpenAI, Deepgram, AssemblyAI
  - TTS: OpenAI, ElevenLabs
  - OCR: OpenAI Vision, OCR.Space
  - 통합 질의: `/v1/multimodal/ask`
- 오케스트레이션 선택
  - `native`, `langchain`, `langgraph`
- 사용자 관리
  - 회원가입/로그인/프로필/개인설정
  - 페르소나, 기본 검색옵션, 기본 오케스트레이터
- 추적
  - JSON 로그
  - LangSmith 연동(선택)
- 사용자 저장소 fallback
  - Vector(Chroma) → MariaDB → Memory

## Docker 실행

### 1) 환경 파일 준비
```bash
cd Agent
cp .env.example .env
```

### 2) 실행
```bash
docker compose up -d --build
```

### 3) 확인
```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/bootstrap
```

## 주요 API
- 인증
  - `POST /v1/auth/register`
  - `POST /v1/auth/login`
  - `GET /v1/auth/me`
  - `PUT /v1/auth/settings`
- 질의
  - `POST /v1/ask`
  - `POST /v1/multimodal/ask`
- 멀티모달
  - `POST /v1/stt`
  - `POST /v1/tts`
  - `POST /v1/ocr`
- 관리
  - `POST /v1/reindex`
  - `GET /v1/orchestrators`
  - `GET /health`
  - `GET /v1/bootstrap`

## RAG 보강 포인트
- `AskRequest` 확장 필드
  - `use_web_search`: Tavily 검색 병합
  - `web_search_top_k`: 웹 검색 결과 개수
  - `use_rerank`: 리랭킹 활성화
  - `rerank_provider`: `auto | cohere | lexical | none`
- 응답의 `retrieval_diagnostics`
  - 웹검색 사용 여부, 리랭킹 제공자, 최종 소스 개수 등

## 3rd-party API 환경변수

### RAG/검색
- `TAVILY_API_KEY`
- `COHERE_API_KEY`
- `COHERE_RERANK_MODEL`
- `WEB_SEARCH_FALLBACK_THRESHOLD`

### STT
- `DEEPGRAM_API_KEY`, `DEEPGRAM_MODEL`
- `ASSEMBLYAI_API_KEY`

### TTS
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`
- `ELEVENLABS_MODEL_ID`

### OCR
- `OCR_SPACE_API_KEY`

### OpenAI
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_STT_MODEL`
- `OPENAI_TTS_MODEL`
- `OPENAI_TTS_VOICE`
- `OPENAI_VISION_MODEL`

## 임베딩/인덱싱
- `EMBEDDING_PROVIDER=local|openai`
- `EMBEDDING_DIM` (OpenAI 임베딩 dimensions와 연동 가능)

## 샘플 요청

### 회원가입
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst01","password":"Pass1234","full_name":"금융 분석가"}'
```

### 실무형 RAG 질의 (웹검색+리랭크)
```bash
curl -X POST http://localhost:8000/v1/ask \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "question":"기업대출 심사 에이전트에 필요한 문서 검증 흐름을 설명해줘",
    "top_k": 8,
    "use_llm": true,
    "orchestrator": "langgraph",
    "use_web_search": true,
    "web_search_top_k": 4,
    "use_rerank": true,
    "rerank_provider": "auto"
  }'
```

### STT (Deepgram/OpenAI/AssemblyAI 자동 선택)
```bash
curl -X POST http://localhost:8000/v1/stt \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"audio_base64":"<BASE64_AUDIO>","mime_type":"audio/wav","provider":"auto"}'
```

### TTS (OpenAI/ElevenLabs 자동 선택)
```bash
curl -X POST http://localhost:8000/v1/tts \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"text":"안녕하세요. 오늘의 시장 리스크 요약을 브리핑합니다.","provider":"auto","audio_format":"mp3"}'
```

### OCR (OpenAI Vision/OCR.Space 자동 선택)
```bash
curl -X POST http://localhost:8000/v1/ocr \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"<BASE64_IMAGE>","provider":"auto"}'
```

## 로컬 실행
```bash
cd Agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.ingest --repo-root .. --db-path ./data/chroma --collection finance_agent_lab
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
