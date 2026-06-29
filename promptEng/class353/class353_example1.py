# 이 파일은 www.edumgt.co.kr 의 에듀엠지티에 저작권이 있습니다

"""class353 example1: 프롬프트 엔지니어링 개요 · 단계 1/4 입문 이해 [class353]"""

TOPIC = "프롬프트 엔지니어링 개요 · 단계 1/4 입문 이해 [class353]"
EXAMPLE_TEMPLATE = "prompt"
EXAMPLE_VARIANT = 1

import json

LEARNING_GOALS = [
    "원하는 결과를 얻기 위한 프롬프트 설계 능력 습득",
    "프롬프트 패턴과 전략 이해",
    "출력 품질·형식·안정성 개선 방법 습득",
    "LLM 응답 제어 기술 확보",
]
BANNED_RULES = ["무조건 정답", "100% 보장", "절대 틀리지 않음"]

def resolve_mode():
    if "프롬프트 엔지니어링 개요" in TOPIC:
        return "overview"
    if "질문 구조화" in TOPIC:
        return "structure"
    if "역할/맥락 설정" in TOPIC:
        return "role_context"
    if "출력 포맷 제어" in TOPIC:
        return "output_control"
    if "예시 기반 학습" in TOPIC:
        return "shot_learning"
    if "단계적 추론 유도" in TOPIC:
        return "reasoning"
    if "평가와 개선" in TOPIC:
        return "evaluation"
    if "자동화 프롬프트 패턴" in TOPIC:
        return "automation"
    if "도메인 템플릿 작성" in TOPIC:
        return "domain_template"
    if "실전 프롬프트 튜닝" in TOPIC:
        return "practical_tuning"
    return "prompt_general"

def template_version():
    return f"prompt-v{EXAMPLE_VARIANT}.0"

def build_cases():
    cases = [
        {
            "id": "support",
            "domain": "고객상담",
            "role": "고객상담 매니저",
            "goal": "환불 문의에 정책 기반 답변 제공",
            "input_text": "배송이 8일 지연됐는데 환불 가능한가요?",
            "tone": "친절",
        }
    ]
    if EXAMPLE_VARIANT >= 2:
        cases.append(
            {
                "id": "summary",
                "domain": "문서요약",
                "role": "문서 요약 비서",
                "goal": "회의록 핵심 3가지 요약",
                "input_text": "회의 내용: 비용 절감, 응답 지연 개선, 보안 점검 일정 확정",
                "tone": "간결",
            }
        )
    if EXAMPLE_VARIANT >= 3:
        cases.append(
            {
                "id": "code",
                "domain": "코드생성",
                "role": "Python 튜터",
                "goal": "문자열 길이 계산 함수 생성",
                "input_text": "입력 문자열 길이를 반환하는 함수를 만들어줘",
                "tone": "정확",
            }
        )
    if EXAMPLE_VARIANT >= 4:
        cases.append(
            {
                "id": "report",
                "domain": "보고서 작성",
                "role": "기획 리포트 작성자",
                "goal": "주간 보고서 초안 작성",
                "input_text": "이번 주 이슈: API 장애 2회, 복구시간 개선, 다음주 위험요소 정리",
                "tone": "공식",
            }
        )
    if EXAMPLE_VARIANT >= 5:
        cases.append(
            {
                "id": "edu",
                "domain": "교육 콘텐츠 생성",
                "role": "교육 콘텐츠 설계자",
                "goal": "초급 학습자용 퀴즈 3문항 생성",
                "input_text": "프롬프트 엔지니어링 입문 내용을 바탕으로 퀴즈를 만들어줘",
                "tone": "친절",
            }
        )
    return cases

def build_constraints(case):
    max_chars = 120 + EXAMPLE_VARIANT * 30
    constraints = [
        f"MAX_CHARS={max_chars}",
        "사실 단정 표현 최소화",
        "근거가 없으면 '확인 필요' 표기",
    ]
    if case["domain"] in {"코드생성", "보고서 작성"}:
        constraints.append("출력 항목 누락 금지")
    if EXAMPLE_VARIANT >= 4:
        constraints.append("금지 규칙 위반 문장 제거")
    return constraints

def split_system_user_prompts(case, output_format, constraints):
    system_prompt = (
        "당신은 출력 형식을 지키는 프롬프트 실행 도우미다. "
        "금지 규칙을 위반하면 경고를 반환한다."
    )
    user_prompt = (
        f"역할={case['role']}\n"
        f"목표={case['goal']}\n"
        f"입력={case['input_text']}\n"
        f"출력형식={output_format}\n"
        f"제약={', '.join(constraints)}"
    )
    return {"system": system_prompt, "user": user_prompt}

def build_prompt(role, goal, input_text, output_format, constraints, examples=None, style=None):
    lines = [
        f"[ROLE] {role}",
        f"[GOAL] {goal}",
        f"[INPUT] {input_text}",
        f"[FORMAT] {output_format}",
        f"[CONSTRAINTS] {'; '.join(constraints)}",
    ]
    if style:
        lines.append(f"[STYLE] {style}")
    if examples:
        lines.append("[EXAMPLES]")
        for idx, item in enumerate(examples, start=1):
            lines.append(f"{idx}) {item}")
    return "\n".join(lines)

def lint_prompt(prompt_text):
    required = ["[ROLE]", "[GOAL]", "[INPUT]", "[FORMAT]", "[CONSTRAINTS]"]
    missing = [tag for tag in required if tag not in prompt_text]
    return {"is_valid": len(missing) == 0, "missing": missing}

def build_zero_one_few_prompts(case, output_format, constraints):
    zero = build_prompt(
        role=case["role"],
        goal=case["goal"],
        input_text=case["input_text"],
        output_format=output_format,
        constraints=constraints,
        style=case["tone"],
    )
    one = build_prompt(
        role=case["role"],
        goal=case["goal"],
        input_text=case["input_text"],
        output_format=output_format,
        constraints=constraints,
        examples=["입력: 환불 문의 / 출력: 정책 조건 2개 + 안내 문장"],
        style=case["tone"],
    )
    few = build_prompt(
        role=case["role"],
        goal=case["goal"],
        input_text=case["input_text"],
        output_format=output_format,
        constraints=constraints,
        examples=[
            "입력: 배송 지연 / 출력: 요약 + 조치",
            "입력: 결제 오류 / 출력: 원인 + 재시도 절차",
            "입력: 계정 문의 / 출력: 확인 정보 + 안내",
        ],
        style=case["tone"],
    )
    return [
        {"strategy": "zero-shot", "prompt": zero},
        {"strategy": "one-shot", "prompt": one},
        {"strategy": "few-shot", "prompt": few},
    ]

def build_reasoning_prompts(case, output_format, constraints):
    baseline = build_prompt(
        role=case["role"],
        goal=case["goal"],
        input_text=case["input_text"],
        output_format=output_format,
        constraints=constraints,
        style=case["tone"],
    )
    step = baseline + "\n[REASONING] Step-by-step으로 핵심 단계를 3개로 나눠 작성"
    cot = baseline + "\n[REASONING] Chain-of-thought 개념에 따라 단계 요약 후 최종 답만 출력"
    return [
        {"strategy": "baseline", "prompt": baseline},
        {"strategy": "step-by-step", "prompt": step},
        {"strategy": "cot-concept", "prompt": cot},
    ]

def parse_max_chars(constraints):
    for item in constraints:
        if item.startswith("MAX_CHARS="):
            try:
                return int(item.split("=", maxsplit=1)[1])
            except ValueError:
                return 200
    return 200

def enforce_length(text, limit):
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3] + "..."

def enforce_banned_rules(text):
    cleaned = text
    for bad in BANNED_RULES:
        cleaned = cleaned.replace(bad, "확인 필요")
    return cleaned

def apply_tone(text, tone):
    prefix_map = {
        "친절": "안내: ",
        "간결": "요약: ",
        "정확": "정의: ",
        "공식": "보고: ",
    }
    return prefix_map.get(tone, "") + text

def render_output(output_format, case):
    if output_format == "JSON":
        payload = {
            "domain": case["domain"],
            "goal": case["goal"],
            "answer": "핵심 항목을 조건에 맞춰 생성했습니다.",
        }
        return json.dumps(payload, ensure_ascii=False)
    if output_format == "TABLE":
        return (
            "| 항목 | 내용 |\n"
            "| --- | --- |\n"
            f"| domain | {case['domain']} |\n"
            f"| goal | {case['goal']} |\n"
            "| answer | 조건 기반 응답 |"
        )
    return f"{case['goal']} -> {case['input_text']} 기반으로 응답을 생성했습니다."

def simulate_response(prompt_text, case, output_format, constraints):
    lint = lint_prompt(prompt_text)
    base = render_output(output_format, case)
    if "[REASONING]" in prompt_text:
        base += " 단계1 문제정의/단계2 정보정리/단계3 출력검증."
    if "[EXAMPLES]" in prompt_text:
        base += " 예시 패턴을 반영했습니다."
    if not lint["is_valid"]:
        base = "필수 블록 누락으로 품질 저하 가능: " + ", ".join(lint["missing"])
    toned = apply_tone(base, case["tone"])
    safe = enforce_banned_rules(toned)
    limited = enforce_length(safe, parse_max_chars(constraints))
    return {"text": limited, "lint": lint}

def check_format(response_text, output_format):
    if output_format == "JSON":
        try:
            json.loads(response_text)
            return True
        except json.JSONDecodeError:
            return False
    if output_format == "TABLE":
        return "| 항목 | 내용 |" in response_text
    return len(response_text.strip()) > 0

def evaluate_response(case, strategy, output_format, result):
    text = result["text"]
    format_ok = check_format(text, output_format)
    goal_ok = case["goal"].split()[0] in text or case["domain"] in text
    safe = all(bad not in text for bad in BANNED_RULES)
    score = int(format_ok) + int(goal_ok) + int(safe)
    return {
        "case_id": case["id"],
        "strategy": strategy,
        "format": output_format,
        "score": score,
        "format_ok": format_ok,
        "goal_ok": goal_ok,
        "safe": safe,
        "lint_ok": result["lint"]["is_valid"],
        "response": text,
    }

def choose_output_formats(mode):
    if mode == "output_control":
        return ["TABLE", "JSON", "TEXT"]
    if EXAMPLE_VARIANT >= 4:
        return ["JSON", "TEXT"]
    return ["TEXT"]

def build_prompt_variants(mode, case, output_format, constraints):
    if mode == "shot_learning":
        return build_zero_one_few_prompts(case, output_format, constraints)
    if mode == "reasoning":
        return build_reasoning_prompts(case, output_format, constraints)

    base_prompt = build_prompt(
        role=case["role"],
        goal=case["goal"],
        input_text=case["input_text"],
        output_format=output_format,
        constraints=constraints,
        style=case["tone"],
    )
    tuned_prompt = build_prompt(
        role=case["role"],
        goal=case["goal"],
        input_text=case["input_text"],
        output_format=output_format,
        constraints=constraints + ["불확실하면 확인 필요 표기"],
        examples=["입력과 같은 도메인의 예시를 반영"],
        style=case["tone"],
    )
    prompts = [{"strategy": "baseline", "prompt": base_prompt}]
    if EXAMPLE_VARIANT >= 2:
        prompts.append({"strategy": "tuned", "prompt": tuned_prompt})
    return prompts

def analyze_failure_patterns(rows):
    failures = {"format": 0, "goal": 0, "safety": 0, "lint": 0}
    for row in rows:
        if not row["format_ok"]:
            failures["format"] += 1
        if not row["goal_ok"]:
            failures["goal"] += 1
        if not row["safe"]:
            failures["safety"] += 1
        if not row["lint_ok"]:
            failures["lint"] += 1
    return failures

def summarize_mode(mode, rows, cases):
    avg_score = round(sum(row["score"] for row in rows) / max(1, len(rows)), 2)
    failures = analyze_failure_patterns(rows)
    domains = sorted({case["domain"] for case in cases})

    if mode == "overview":
        return {"learning_goals": LEARNING_GOALS, "avg_score": avg_score, "domains": domains}
    if mode == "structure":
        return {
            "prompt_structure": ["ROLE", "GOAL", "INPUT", "FORMAT", "CONSTRAINTS"],
            "avg_score": avg_score,
            "failures": failures,
        }
    if mode == "role_context":
        split_sample = split_system_user_prompts(
            cases[0], output_format="TEXT", constraints=build_constraints(cases[0])
        )
        return {
            "system_user_split": split_sample,
            "avg_score": avg_score,
            "failures": failures,
        }
    if mode == "output_control":
        return {
            "output_controls": ["표 형식", "JSON 형식", "길이 제한", "어조/문체", "금지 규칙"],
            "format_success": sum(1 for row in rows if row["format_ok"]),
            "total": len(rows),
        }
    if mode == "shot_learning":
        by_strategy = {}
        for row in rows:
            by_strategy.setdefault(row["strategy"], []).append(row["score"])
        comparison = {
            key: round(sum(vals) / len(vals), 2) for key, vals in by_strategy.items() if vals
        }
        return {"shot_comparison": comparison, "failures": failures}
    if mode == "reasoning":
        return {
            "reasoning_methods": ["baseline", "step-by-step", "cot-concept"],
            "avg_score": avg_score,
            "failures": failures,
        }
    if mode == "evaluation":
        return {
            "improvement_loop": ["실패 수집", "원인 분류", "지시 수정", "재평가"],
            "failure_patterns": failures,
            "avg_score": avg_score,
        }
    if mode == "automation":
        return {
            "template_version": template_version(),
            "automation_items": ["버전 관리", "재사용 템플릿", "테스트 케이스 자동 평가"],
            "case_count": len(cases),
        }
    if mode == "domain_template":
        return {
            "domains": domains,
            "domain_tasks": ["고객상담", "문서요약", "코드생성", "보고서 작성", "교육 콘텐츠 생성"],
            "avg_score": avg_score,
        }
    if mode == "practical_tuning":
        baseline_scores = [row["score"] for row in rows if row["strategy"] == "baseline"]
        tuned_scores = [row["score"] for row in rows if row["strategy"] != "baseline"]
        return {
            "tuning_compare": {
                "baseline_avg": round(sum(baseline_scores) / max(1, len(baseline_scores)), 2),
                "improved_avg": round(sum(tuned_scores) / max(1, len(tuned_scores)), 2),
            },
            "production_checks": [
                "프롬프트 버전 관리",
                "시스템/사용자 프롬프트 분리",
                "테스트 케이스 기반 평가",
                "오류 응답 처리",
            ],
        }
    return {"avg_score": avg_score, "failure_patterns": failures}

def _lm_studio_prompt_demo():
    """
    LM Studio 로 다양한 프롬프트 전략을 직접 비교합니다.
    같은 질문에 Zero-shot / Few-shot / 역할 부여 프롬프트를 적용해 차이를 관찰하세요.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        from lmstudio_config import call_lm, LM_STUDIO_AVAILABLE, LM_MODEL
    except ImportError:
        return

    if not LM_STUDIO_AVAILABLE:
        return

    question = "금융 상품을 추천해주세요."
    strategies = [
        {
            "name": "Zero-shot (기본)",
            "messages": [{"role": "user", "content": question}],
        },
        {
            "name": "역할 부여 (System prompt)",
            "messages": [
                {"role": "system", "content": "당신은 15년 경력의 금융 전문 상담사입니다. 고객의 위험 성향을 먼저 확인하고 맞춤형 추천을 제공합니다."},
                {"role": "user", "content": question},
            ],
        },
        {
            "name": "Few-shot (예시 포함)",
            "messages": [
                {"role": "system", "content": "당신은 금융 상담 AI 입니다."},
                {"role": "user", "content": "안전한 상품을 원해요."},
                {"role": "assistant", "content": "위험 성향이 낮으시군요. 예금, 국채 ETF, MMF 를 추천드립니다."},
                {"role": "user", "content": question},
            ],
        },
    ]

    print(f"\n{'='*60}")
    print(f"[LM Studio 프롬프트 전략 비교] 모델: {LM_MODEL}")
    print(f"질문: {question}")
    print(f"{'='*60}")

    for strategy in strategies:
        result = call_lm(strategy["messages"], temperature=0.7, max_tokens=150)
        print(f"\n[{strategy['name']}]")
        print(result if result else "  → LM Studio 연결 실패 (포트 1234 확인)")


def main():
    print("오늘 주제:", TOPIC)
    mode = resolve_mode()
    cases = build_cases()
    rows = []

    for case in cases:
        constraints = build_constraints(case)
        for output_format in choose_output_formats(mode):
            for item in build_prompt_variants(mode, case, output_format, constraints):
                result = simulate_response(item["prompt"], case, output_format, constraints)
                row = evaluate_response(
                    case=case,
                    strategy=item["strategy"],
                    output_format=output_format,
                    result=result,
                )
                rows.append(row)

    summary = summarize_mode(mode, rows, cases)
    print("모드:", mode)
    print("요약:", summary)

    # LM Studio 프롬프트 전략 비교 실습
    _lm_studio_prompt_demo()

    return {
        "variant": EXAMPLE_VARIANT,
        "mode": mode,
        "sample_count": len(cases),
        "result_count": len(rows),
        "template_version": template_version(),
        "summary": summary,
    }

if __name__ == "__main__":
    main()
