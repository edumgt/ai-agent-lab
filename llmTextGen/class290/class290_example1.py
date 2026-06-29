# 이 파일은 www.edumgt.co.kr 의 에듀엠지티에 저작권이 있습니다

"""class290 example1: LLM 개요 · 단계 2/7 기초 구현 [class290]"""

TOPIC = "LLM 개요 · 단계 2/7 기초 구현 [class290]"
EXAMPLE_TEMPLATE = "llm_gen"
EXAMPLE_VARIANT = 1

VOCAB = ["정확성", "요약", "근거", "응답", "검증", "안전", "JSON", "맥락", "추론", "서비스"]
KNOWLEDGE_TERMS = {
    "llm", "transformer", "token", "context", "temperature", "topk", "topp",
    "요약", "질의응답", "번역", "문서", "코드", "분류", "추출", "json",
    "api", "cloud", "local", "security", "cost", "performance"
}

def resolve_mode():
    if "LLM 개요" in TOPIC:
        return "overview"
    if "토큰/컨텍스트 이해" in TOPIC:
        return "token_context"
    if "생성 파라미터" in TOPIC:
        return "generation_params"
    if "프롬프트 기반 생성" in TOPIC:
        return "prompting"
    if "요약/분류/추출" in TOPIC:
        return "task_types"
    if "대화형 응답 설계" in TOPIC:
        return "chatbot"
    if "안전성/환각 관리" in TOPIC:
        return "safety"
    if "도메인 적용 시나리오" in TOPIC:
        return "deployment_modes"
    if "API 연동 실습" in TOPIC:
        return "api_practice"
    if "Agent 시스템 통합 구현" in TOPIC:
        return "agent_integration"
    return "llm_general"

def build_prompt_cases():
    cases = [
        "LLM의 정의를 2문장으로 설명해줘",
        "고객 문의 답변 초안을 3문장으로 작성해줘",
    ]
    if EXAMPLE_VARIANT >= 2:
        cases.append("다음 회의록을 요약해줘: 모델 비용, 지연, 보안 이슈를 논의했다.")
    if EXAMPLE_VARIANT >= 3:
        cases.append("환불 정책을 묻는 사용자에게 챗봇 응답을 작성해줘")
    if EXAMPLE_VARIANT >= 4:
        cases.append("문서에서 날짜, 담당자, 우선순위를 JSON으로 추출해줘")
    if EXAMPLE_VARIANT >= 5:
        cases.append("입력 문자열 길이를 계산하는 Python 함수를 생성해줘")
    return cases

def build_generation_config():
    return {
        "temperature": round(0.35 + EXAMPLE_VARIANT * 0.15, 2),
        "top_k": 3 + EXAMPLE_VARIANT,
        "top_p": min(0.98, round(0.72 + EXAMPLE_VARIANT * 0.05, 2)),
        "max_tokens": 120 + EXAMPLE_VARIANT * 20,
        "context_limit": 6 + EXAMPLE_VARIANT,
    }

def tokenize(text):
    cleaned = str(text).replace(",", " ").replace(".", " ").replace("/", " ").lower()
    return [tok for tok in cleaned.split() if tok]

def context_window(tokens, limit):
    if limit <= 0:
        return []
    return tokens[-limit:]

def next_token_probs(vocab, temperature):
    weighted = []
    t = max(0.1, float(temperature))
    for idx, token in enumerate(vocab):
        base = 1.0 / (idx + 2)
        weighted.append((token, base ** (1.0 / t)))
    total = sum(score for _, score in weighted) or 1.0
    return [(token, round(score / total, 4)) for token, score in weighted]

def apply_top_k_top_p(items, top_k, top_p):
    ranked = sorted(items, key=lambda x: x[1], reverse=True)
    if top_k > 0:
        ranked = ranked[:top_k]
    selected = []
    cumulative = 0.0
    for token, prob in ranked:
        selected.append((token, prob))
        cumulative += prob
        if cumulative >= top_p:
            break
    return selected

def choose_next_token(filtered):
    if not filtered:
        return "응답"
    return filtered[0][0]

def simulate_generation(prompt, cfg):
    prompt_tokens = tokenize(prompt)
    ctx = context_window(prompt_tokens, cfg["context_limit"])
    probs = next_token_probs(VOCAB, cfg["temperature"])
    filtered = apply_top_k_top_p(probs, cfg["top_k"], cfg["top_p"])
    token = choose_next_token(filtered)
    prefix = " ".join(ctx[:4]) if ctx else "입력없음"
    text = f"[SIM] {prefix} -> {token} 중심으로 답변을 생성합니다."
    if cfg["temperature"] >= 1.0 and len(prompt_tokens) > 8:
        text += " 일부 내용은 확인이 필요합니다."
    return text

def hallucination_guard(text):
    risky_markers = ["항상", "100%", "보장", "확실히"]
    found = [m for m in risky_markers if m in text]
    unknown = []
    for tok in tokenize(text):
        if len(tok) >= 5 and tok not in KNOWLEDGE_TERMS and tok.isalpha():
            unknown.append(tok)
        if len(unknown) >= 4:
            break
    return {
        "risk": bool(found) or len(unknown) >= 3,
        "markers": found,
        "unknown_terms": unknown,
    }

def build_task_outputs(prompt):
    words = tokenize(prompt)
    summary = " ".join(words[: min(8, len(words))])
    category = "고객지원" if "환불" in prompt else "일반"
    return {
        "summary": summary,
        "qa": f"Q: {prompt} / A: 핵심은 요구사항 명확화와 검증입니다.",
        "translation": f"[KR->EN] {summary}",
        "draft": f"안녕하세요. 요청하신 내용({summary})을 반영해 초안을 작성했습니다.",
        "code": "def length_of_text(text):\n    return len(text)",
        "classification": category,
        "extraction": {"keyword_count": len(words), "first_token": words[0] if words else ""},
    }

def deployment_options():
    return [
        {"mode": "api", "cost": "중", "latency": "낮음", "security": "중"},
        {"mode": "open_model", "cost": "중", "latency": "중", "security": "중"},
        {"mode": "cloud", "cost": "중상", "latency": "중", "security": "상"},
        {"mode": "local", "cost": "초기고", "latency": "중상", "security": "상"},
    ]

def to_json_schema_payload(task, content):
    return {
        "task": task,
        "response": {
            "format": "json",
            "content": content,
        },
    }

def handle_error(status_code):
    if status_code == 429:
        return "rate_limit_retry"
    if status_code >= 500:
        return "server_fallback"
    return "ok"

def rule_based_reply(user_text):
    if "환불" in user_text:
        return "환불 정책 링크를 안내합니다."
    if "요약" in user_text:
        return "입력 문서의 앞부분을 기준으로 요약합니다."
    return "사전 정의된 규칙 응답입니다."

def llm_based_reply(user_text, cfg):
    return simulate_generation(user_text, cfg)

def build_mode_summary(mode, prompt_outputs, cfg):
    if mode == "overview":
        return {
            "llm_core": ["LLM 정의", "Transformer", "토큰/컨텍스트", "사전학습/파인튜닝"],
            "difference_from_nlp": ["범용 생성", "few-shot 적응", "긴 문맥 처리"],
        }
    if mode == "token_context":
        token_lengths = [len(tokenize(item["prompt"])) for item in prompt_outputs]
        return {
            "next_token": "컨텍스트 기반 확률 예측",
            "context_window": cfg["context_limit"],
            "token_lengths": token_lengths,
        }
    if mode == "generation_params":
        risk_count = sum(1 for item in prompt_outputs if item["guard"]["risk"])
        return {
            "params": {"temperature": cfg["temperature"], "top_k": cfg["top_k"], "top_p": cfg["top_p"]},
            "hallucination_risk_count": risk_count,
        }
    if mode == "prompting":
        sample = build_task_outputs(prompt_outputs[0]["prompt"]) if prompt_outputs else {}
        return {
            "practice": ["기본 프롬프트 생성", "문서 요약", "이메일/보고서 초안", "챗봇 응답"],
            "sample_outputs": {"summary": sample.get("summary"), "draft": sample.get("draft")},
        }
    if mode == "task_types":
        sample = build_task_outputs(prompt_outputs[-1]["prompt"]) if prompt_outputs else {}
        return {
            "task_types": ["요약", "질의응답", "번역", "문서 작성", "코드 생성", "분류/정보추출"],
            "structured_output": to_json_schema_payload("extract", sample.get("extraction", {})),
        }
    if mode == "chatbot":
        user_text = prompt_outputs[-1]["prompt"] if prompt_outputs else "환불 정책을 알려줘"
        return {
            "rule_based": rule_based_reply(user_text),
            "llm_based": llm_based_reply(user_text, cfg),
            "controls": ["길이", "톤", "스타일", "오류 응답 처리"],
        }
    if mode == "safety":
        risk_count = sum(1 for item in prompt_outputs if item["guard"]["risk"])
        return {
            "limits": ["사실성 문제", "최신성 한계", "보안/개인정보", "프롬프트 민감성"],
            "risk_count": risk_count,
            "validation_need": "실무 적용 전 검증 필수",
        }
    if mode == "deployment_modes":
        return {
            "modes": deployment_options(),
            "considerations": ["비용", "성능", "보안"],
        }
    if mode == "api_practice":
        payload = to_json_schema_payload("summary", {"text": "샘플 문서"})
        return {
            "api_flow": ["요청 구성", "응답 생성", "JSON 검증", "오류 처리"],
            "payload_sample": payload,
            "error_policy": {"429": handle_error(429), "500": handle_error(500)},
        }
    if mode == "agent_integration":
        user_text = prompt_outputs[0]["prompt"] if prompt_outputs else "요약 요청"
        return {
            "workflow": ["입력 라우팅", "생성", "검증", "응답", "로그"],
            "comparison": {
                "rule_based": rule_based_reply(user_text),
                "llm_based": llm_based_reply(user_text, cfg),
            },
        }
    return {"prompt_count": len(prompt_outputs), "config": cfg}

def _lm_studio_temperature_demo():
    """
    LM Studio 로 temperature 파라미터 효과를 실습합니다.
    temperature 가 낮을수록 일관된 답변, 높을수록 창의적 답변이 생성됩니다.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        from lmstudio_config import call_lm_simple, LM_STUDIO_AVAILABLE, LM_MODEL
    except ImportError:
        return

    if not LM_STUDIO_AVAILABLE:
        return

    prompt = "금융 AI 에이전트의 핵심 역할을 한 문장으로 설명해주세요."
    print(f"\n{'='*60}")
    print(f"[LM Studio 실습] Temperature 비교 — 모델: {LM_MODEL}")
    print(f"프롬프트: {prompt}")
    print(f"{'='*60}")

    for temp in [0.1, 0.7, 1.2]:
        result = call_lm_simple(prompt, temperature=temp, max_tokens=100)
        if result:
            print(f"\n  temperature={temp}: {result}")
        else:
            print(f"\n  temperature={temp}: [LM Studio 연결 실패]")
            break


def main():
    print("오늘 주제:", TOPIC)
    mode = resolve_mode()
    cfg = build_generation_config()
    prompts = build_prompt_cases()

    prompt_outputs = []
    for prompt in prompts:
        text = simulate_generation(prompt, cfg)
        guard = hallucination_guard(text)
        prompt_outputs.append({"prompt": prompt, "text": text, "guard": guard})

    summary = build_mode_summary(mode, prompt_outputs, cfg)
    print("모드:", mode)
    print("요약:", summary)

    # LM Studio temperature 실습
    _lm_studio_temperature_demo()

    return {
        "variant": EXAMPLE_VARIANT,
        "mode": mode,
        "sample_count": len(prompts),
        "summary": summary,
    }

if __name__ == "__main__":
    main()
