# PersonaLLMResponder · 금융 상품 상담 에이전트

독립 실행형 금융 상담 응답 프로젝트입니다.

## 기능
- 상담 페르소나 등록/수정
- 금융 질문 응답 생성
- OpenAI 키가 있으면 LLM 응답, 없으면 로컬 규칙 응답

## 실행
```bash
cd PersonaLLMResponder
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8080
```

## Docker
```bash
docker compose up -d --build
curl -sS http://127.0.0.1:9102/health
```
