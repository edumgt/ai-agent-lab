# PersonaKnowledgeCustomizer · 금융 지식베이스 커스터마이저

독립 실행형 금융 지식 커스텀 답변 프로젝트입니다.

## 기능
- 금융 지식 데이터 업서트/조회
- 기본 지식 부트스트랩
- 질문 기반 검색 후 금융 스타일 답변 생성

## 실행
```bash
cd PersonaKnowledgeCustomizer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8080
```

## Docker
```bash
docker compose up -d --build
curl -sS http://127.0.0.1:9103/health
```
