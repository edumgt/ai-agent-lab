# Project Index (Finance Lab Apps)

프로젝트 앱은 `Agent/`와 함께 금융 특화 보조 실험 앱으로 운영됩니다.

## Projects
1. `VoiceModelBuilder`
   - 주제: `금융 상담 음성 브리핑 스튜디오`
   - 경로: `VoiceModelBuilder`
   - 포트: `9101`

2. `PersonaLLMResponder`
   - 주제: `금융 상품 상담 에이전트`
   - 경로: `PersonaLLMResponder`
   - 포트: `9102`

3. `PersonaKnowledgeCustomizer`
   - 주제: `금융 지식베이스 커스터마이저`
   - 경로: `PersonaKnowledgeCustomizer`
   - 포트: `9103`

## 공통 실행
```bash
cd VoiceModelBuilder  # 또는 PersonaLLMResponder, PersonaKnowledgeCustomizer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8080
```

## Docker
```bash
cd VoiceModelBuilder  # 또는 PersonaLLMResponder, PersonaKnowledgeCustomizer
docker compose up -d --build
curl -sS http://127.0.0.1:9101/health
```
