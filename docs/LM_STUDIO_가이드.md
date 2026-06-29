# LM Studio 설치 및 사용 가이드

## 1. LM Studio 란?

LM Studio 는 오픈소스 LLM 을 로컬에서 실행할 수 있는 무료 데스크톱 앱입니다.

- **OpenAI 호환 API**: 기존 OpenAI Python SDK 코드를 `base_url` 만 바꿔 그대로 사용
- **GGUF 모델 지원**: Llama, Qwen, Phi, Mistral 등 다양한 오픈소스 모델
- **오프라인 실행**: 인터넷 없이, API 키 없이, 무료로 운영

---

## 2. 설치

1. https://lmstudio.ai 접속
2. 운영체제에 맞는 설치 파일 다운로드 및 설치
3. 실행 확인

**최소 사양 (CPU 추론):**
| 구분 | 최소 | 권장 |
|------|------|------|
| RAM  | 8GB  | 16GB |
| 저장공간 | 10GB | 50GB |
| CPU  | 4코어 | 8코어 |

**GPU 가속 (선택):**
- NVIDIA GPU 8GB+ VRAM: CUDA 활성화 → 속도 5~10배 향상
- Apple Silicon (M1/M2/M3): Metal 가속 자동 적용

---

## 3. 모델 다운로드

### 3.1 Discover 탭에서 검색

LM Studio 좌측 "Discover (돋보기)" 탭 → 모델명 검색

### 3.2 권장 모델 (한국어 실습용)

| 모델 | 파일명 (Q4_K_M 기준) | 크기 | 특징 |
|------|---------------------|------|------|
| Qwen2.5-7B-Instruct | `Qwen2.5-7B-Instruct-Q4_K_M.gguf` | ~4.5GB | 한국어 최우수, 입문 추천 |
| Qwen2.5-14B-Instruct | `Qwen2.5-14B-Instruct-Q4_K_M.gguf` | ~9GB | 고품질, 16GB RAM 필요 |
| Phi-3.5-mini | `Phi-3.5-mini-instruct-Q4_K_M.gguf` | ~2.4GB | 경량, 저사양 PC |
| Llama-3.2-3B | `Llama-3.2-3B-Instruct-Q4_K_M.gguf` | ~2GB | 영어/코드 중심 |

> **Q4_K_M**: 4비트 양자화, 품질과 속도의 균형 — CPU 전용 PC에 권장

---

## 4. 로컬 서버 시작

1. LM Studio 좌측 **"Local Server (↔)"** 탭 클릭
2. 상단 드롭다운에서 로드할 모델 선택
3. **[Start Server]** 버튼 클릭
4. 포트 확인: 기본 `1234`

서버 시작 후 표시되는 정보:
```
Server running at: http://localhost:1234
Model loaded: Qwen2.5-7B-Instruct-Q4_K_M
```

---

## 5. Python 연동

### 5.1 기본 연결 (openai 패키지)

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # 아무 문자열 가능
)

response = client.chat.completions.create(
    model="local-model",  # LM Studio 에서 로드한 모델명 (아무 값 가능)
    messages=[
        {"role": "system", "content": "당신은 친절한 AI 어시스턴트입니다."},
        {"role": "user", "content": "안녕하세요!"},
    ],
    temperature=0.7,
    max_tokens=256,
)

print(response.choices[0].message.content)
```

### 5.2 저장소 공통 클라이언트

```python
# lmstudio_config.py 사용 (저장소 루트에 위치)
from lmstudio_config import call_lm_simple, call_lm, check_connection

# 연결 확인
ok = check_connection()
print("LM Studio 연결:", "성공" if ok else "실패")

# 단순 호출
answer = call_lm_simple("LLM 이란 무엇인가요?")

# 멀티턴 호출
answer = call_lm([
    {"role": "system", "content": "당신은 금융 전문가입니다."},
    {"role": "user", "content": "ETF 와 펀드의 차이를 알려주세요."},
], temperature=0.5, max_tokens=300)
```

### 5.3 LangChain 연동

```bash
pip install langchain-openai
```

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

llm = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1"),
    api_key="lm-studio",
    model=os.getenv("LM_STUDIO_MODEL", "local-model"),
    temperature=0.7,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_msg}"),
    ("human", "{user_msg}"),
])

chain = prompt | llm
result = chain.invoke({
    "system_msg": "당신은 친절한 금융 상담사입니다.",
    "user_msg": "펀드 투자 시 주의할 점은?",
})
print(result.content)
```

---

## 6. 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `LM_STUDIO_URL` | `http://localhost:1234/v1` | LM Studio 서버 주소 |
| `LM_STUDIO_API_KEY` | `lm-studio` | 아무 값 가능 |
| `LM_STUDIO_MODEL` | `local-model` | 로드한 모델명 |

```bash
# 셸에서 설정
export LM_STUDIO_URL=http://localhost:1234/v1
export LM_STUDIO_MODEL=Qwen2.5-7B-Instruct-Q4_K_M

# 또는 .env 파일
echo "LM_STUDIO_MODEL=Qwen2.5-7B-Instruct-Q4_K_M" >> .env
```

---

## 7. Docker 에서 LM Studio 연결

Docker 컨테이너에서 호스트의 LM Studio 에 접근할 때:

```yaml
# docker-compose.yml
services:
  my-service:
    environment:
      LM_STUDIO_URL: http://host.docker.internal:1234/v1
    extra_hosts:
      - "host.docker.internal:host-gateway"  # Linux 전용
```

---

## 8. 자주 묻는 질문

**Q: API 키가 없어도 되나요?**  
A: 예. LM Studio 는 어떤 문자열이든 API 키로 받습니다. `"lm-studio"` 또는 `"not-needed"` 등 아무 값이나 사용하세요.

**Q: 모델명은 어떻게 확인하나요?**  
A: LM Studio Local Server 탭에서 드롭다운으로 선택한 모델명이 표시됩니다. Python 에서는 실제 모델명 대신 `"local-model"` 을 써도 현재 로드된 모델로 라우팅됩니다.

**Q: 느린데 어떻게 하나요?**  
A: (1) 더 작은 Q4_K_M 모델 사용, (2) GPU 가속 설정 (CUDA/Metal), (3) `max_tokens` 줄이기, (4) 한 번에 여러 요청 보내지 않기.

**Q: 응답이 한국어가 아닌 경우?**  
A: System prompt 에 "반드시 한국어로 답변하세요." 를 명시하거나, Qwen2.5 계열 한국어 모델을 사용하세요.
