# 이 파일은 www.edumgt.co.kr 의 에듀엠지티에 저작권이 있습니다

"""class393 example1: LangChain 개요 · 단계 1/6 입문 이해 [class393]"""

TOPIC = "LangChain 개요 · 단계 1/6 입문 이해 [class393]"
EXAMPLE_TEMPLATE = "langchain"
EXAMPLE_VARIANT = 1

import json

CORE_COMPONENTS = [
    {"name": "Model", "role": "LLM 호출/추론 수행"},
    {"name": "PromptTemplate", "role": "변수 주입형 프롬프트 구성"},
    {"name": "Chain", "role": "단계 실행 흐름 오케스트레이션"},
    {"name": "Output Parser", "role": "문자열/JSON 구조화"},
    {"name": "Memory", "role": "대화 이력/컨텍스트 유지"},
    {"name": "Retriever", "role": "관련 문서 검색"},
    {"name": "Tool", "role": "검색/계산/API 등 외부 기능 호출"},
    {"name": "Agent", "role": "작업별 도구 선택/실행 판단"},
]

def resolve_mode():
    if "LangChain 개요" in TOPIC:
        return "overview"
    if "PromptTemplate" in TOPIC:
        return "prompt_template"
    if "Model/LLM 연결" in TOPIC:
        return "components"
    if "OutputParser" in TOPIC:
        return "output_parser"
    if "Chain 구성" in TOPIC:
        return "chain_design"
    if "Memory 활용" in TOPIC:
        return "memory_chat"
    if "Tool/Agent 기초" in TOPIC:
        return "tool_agent"
    if "문서 로딩과 분할" in TOPIC:
        return "retriever_base"
    if "VectorStore 연동" in TOPIC:
        return "rag_link"
    if "실전 체인 애플리케이션" in TOPIC:
        return "practice"
    return "langchain_general"

def build_cases():
    cases = [
        {
            "id": "doc_summary",
            "task": "문서 요약 체인",
            "input": "LangChain은 체인 기반으로 LLM 앱을 구성하며 Prompt, Parser, Memory, Tool, Retriever를 연결한다.",
            "session_id": "s1",
            "output_format": "TEXT",
        }
    ]
    if EXAMPLE_VARIANT >= 2:
        cases.append(
            {
                "id": "qa_chain",
                "task": "질의응답 체인",
                "input": "PromptTemplate는 왜 재사용성이 중요한가?",
                "session_id": "s2",
                "output_format": "TEXT",
            }
        )
    if EXAMPLE_VARIANT >= 3:
        cases.append(
            {
                "id": "chatbot",
                "task": "간단한 챗봇",
                "input": "이전 대화 맥락을 기억하면서 답해줘",
                "session_id": "chat-1",
                "output_format": "TEXT",
            }
        )
    if EXAMPLE_VARIANT >= 4:
        cases.append(
            {
                "id": "external_data",
                "task": "외부 데이터 연동",
                "input": "환율 API를 호출해 요약해줘",
                "session_id": "api-1",
                "output_format": "JSON",
            }
        )
    if EXAMPLE_VARIANT >= 5:
        cases.append(
            {
                "id": "rag_flow",
                "task": "RAG 연계",
                "input": "Retriever와 VectorStore를 왜 함께 쓰나?",
                "session_id": "rag-1",
                "output_format": "JSON",
            }
        )
    if EXAMPLE_VARIANT >= 4:
        cases.append(
            {
                "id": "langgraph_flow",
                "task": "LangGraph 상태 흐름",
                "input": "질문 유형에 따라 분기/재시도를 적용해줘",
                "session_id": "graph-1",
                "output_format": "JSON",
            }
        )
    if EXAMPLE_VARIANT >= 5:
        cases.append(
            {
                "id": "langsmith_trace",
                "task": "LangSmith 추적",
                "input": "실행 로그와 품질 지표를 추적해줘",
                "session_id": "trace-1",
                "output_format": "JSON",
            }
        )
    return cases

def tokenize(text):
    cleaned = str(text).replace(",", " ").replace(".", " ").replace("/", " ").replace("?", " ").lower()
    return [tok for tok in cleaned.split() if tok]

def build_prompt_template(mode):
    if mode == "prompt_template":
        return (
            "역할: {role}\n"
            "목표: {goal}\n"
            "입력: {user_input}\n"
            "출력형식: {output_format}\n"
            "제약: 핵심 3줄, 근거 없으면 '확인 필요' 표기"
        )
    return (
        "task={task}\n"
        "input={user_input}\n"
        "context={context}\n"
        "format={output_format}"
    )

def render_prompt(case, mode, context):
    template = build_prompt_template(mode)
    role = "LangChain 엔지니어"
    goal = "체인 기반으로 안정적인 LLM 응답 생성"
    return template.format(
        role=role,
        goal=goal,
        task=case["task"],
        user_input=case["input"],
        context=context,
        output_format=case["output_format"],
    )

def model_stub(prompt, temperature=0.35):
    head = " ".join(tokenize(prompt)[:12])
    stability = "stable" if temperature < 0.5 else "diverse"
    return f"{stability} output: {head}"

def transform_input(text):
    tokens = tokenize(text)
    return " ".join(tokens[: min(14, len(tokens))])

def single_chain(case, mode):
    prompt = render_prompt(case, mode, context="none")
    raw = model_stub(prompt, temperature=0.25)
    return {"pattern": "single", "prompt": prompt, "raw": raw}

def sequential_chain(case, mode):
    normalized = transform_input(case["input"])
    prompt = render_prompt({**case, "input": normalized}, mode, context="normalized")
    raw = model_stub(prompt, temperature=0.4)
    return {"pattern": "sequential", "normalized": normalized, "prompt": prompt, "raw": raw}

def parse_output(raw_text, output_format):
    if output_format == "JSON":
        try:
            return {"ok": True, "data": json.loads(raw_text)}
        except json.JSONDecodeError:
            return {"ok": False, "data": {"message": raw_text, "fallback": True}}
    return {"ok": True, "data": {"text": raw_text}}

def to_json_text(case, raw):
    payload = {
        "task": case["task"],
        "summary": raw,
        "session": case["session_id"],
    }
    return json.dumps(payload, ensure_ascii=False)

def append_memory(store, session_id, user_msg, assistant_msg):
    history = store.setdefault(session_id, [])
    history.append({"user": user_msg, "assistant": assistant_msg})
    if len(history) > 4:
        del history[:-4]
    return history

def memory_chat(case, memory_store):
    history = memory_store.get(case["session_id"], [])
    recent = " / ".join(item["user"] for item in history[-2:]) if history else "none"
    prompt = render_prompt(case, mode="memory_chat", context=recent)
    raw = model_stub(prompt, temperature=0.3)
    append_memory(memory_store, case["session_id"], case["input"], raw)
    return {"history_size": len(memory_store.get(case["session_id"], [])), "raw": raw, "context": recent}

def split_documents(text, chunk_size):
    tokens = tokenize(text)
    if not tokens:
        return []
    chunks = []
    step = max(4, chunk_size)
    for idx in range(0, len(tokens), step):
        chunks.append(" ".join(tokens[idx : idx + step]))
    return chunks

def retrieve_chunks(query, chunks, top_k=2):
    query_tokens = set(tokenize(query))
    scored = []
    for chunk in chunks:
        overlap = len(query_tokens & set(tokenize(chunk)))
        if overlap > 0:
            scored.append({"chunk": chunk, "score": overlap})
    scored.sort(key=lambda item: item["score"], reverse=True)
    if not scored and chunks:
        scored.append({"chunk": chunks[0], "score": 0})
    return scored[:top_k]

def rag_chain(query, source_text):
    chunks = split_documents(source_text, chunk_size=10 + EXAMPLE_VARIANT)
    hits = retrieve_chunks(query, chunks, top_k=2)
    evidence = " | ".join(item["chunk"] for item in hits)
    prompt = f"question={query}\nevidence={evidence}\nanswer in json"
    raw = model_stub(prompt, temperature=0.22)
    return {"chunks": len(chunks), "hits": hits, "raw": raw}

def tool_search(query, knowledge_base):
    q = set(tokenize(query))
    hits = []
    for doc in knowledge_base:
        score = len(q & set(tokenize(doc)))
        if score > 0:
            hits.append({"doc": doc, "score": score})
    hits.sort(key=lambda item: item["score"], reverse=True)
    return hits[:2]

def tool_calculate(expression):
    expr = expression.replace(" ", "")
    if "+" in expr:
        left, right = expr.split("+", maxsplit=1)
        if left.isdigit() and right.isdigit():
            return int(left) + int(right)
    if "*" in expr:
        left, right = expr.split("*", maxsplit=1)
        if left.isdigit() and right.isdigit():
            return int(left) * int(right)
    return "unsupported_expression"

def tool_api(endpoint, payload):
    return {
        "endpoint": endpoint,
        "status": 200,
        "latency_ms": 35 + len(str(payload)),
        "payload": payload,
    }

def run_agent(task, knowledge_base):
    if "검색" in task or "찾아" in task:
        result = {"tool": "search", "data": tool_search(task, knowledge_base)}
    elif "계산" in task or "+" in task or "*" in task:
        result = {"tool": "calculator", "data": tool_calculate(task.replace("계산", "").strip())}
    else:
        result = {"tool": "api", "data": tool_api("/v1/mock", {"task": task})}

    cautions = []
    if EXAMPLE_VARIANT >= 4:
        cautions.append("단순 질문은 Agent 대신 고정 체인으로 처리 가능")
    if EXAMPLE_VARIANT >= 5:
        cautions.append("Tool 호출 실패 시 fallback 경로를 먼저 정의")
    return {"result": result, "cautions": cautions}

def langgraph_workflow(case):
    # 상태 기반 그래프 흐름을 간단한 규칙형으로 시뮬레이션
    state = {"intent": "general", "retry": 0, "route": "direct", "status": "ok"}
    text = case["input"]
    if "분기" in text or "유형" in text:
        state["intent"] = "routing"
        state["route"] = "classifier -> worker"
    if "재시도" in text or "retry" in text.lower():
        state["retry"] = 1 if EXAMPLE_VARIANT < 5 else 2
        state["status"] = "recovered"
    return state

def langsmith_observe(case, bundle):
    # LangSmith 추적 항목과 유사한 구조(입력/출력/지연/오류)를 생성
    latency_ms = 42 + len(case["input"]) + EXAMPLE_VARIANT * 3
    error_count = 0
    if bundle.get("external_status", 200) != 200:
        error_count += 1
    return {
        "trace_name": f"trace-{case['id']}",
        "inputs_logged": True,
        "outputs_logged": True,
        "latency_ms": latency_ms,
        "error_count": error_count,
    }

def practice_bundle(case, memory_store, knowledge_base):
    summary_case = {**case, "task": "문서 요약 체인"}
    qa_case = {**case, "task": "질의응답 체인"}
    chat_case = {**case, "task": "간단한 챗봇"}
    api_case = {**case, "task": "외부 데이터 연동"}

    summary_result = sequential_chain(summary_case, mode="practice")
    qa_result = rag_chain(qa_case["input"], "LangChain 체인은 단계 실행과 검색 근거 결합을 지원한다.")
    chat_result = memory_chat(chat_case, memory_store)
    api_result = tool_api("/v1/external", {"query": api_case["input"]})
    graph_result = langgraph_workflow(case)
    trace_result = langsmith_observe(case, {"external_status": api_result["status"]})
    return {
        "summary_chain": summary_result["pattern"],
        "qa_hits": len(qa_result["hits"]),
        "chat_history": chat_result["history_size"],
        "external_status": api_result["status"],
        "graph_route": graph_result["route"],
        "graph_retry": graph_result["retry"],
        "trace_latency_ms": trace_result["latency_ms"],
        "trace_errors": trace_result["error_count"],
    }

def execute_case(case, mode, memory_store, knowledge_base):
    if mode == "overview":
        single = single_chain(case, mode)
        return {"case": case["id"], "mode": mode, "raw": single["raw"], "steps": ["입력", "모델", "출력"]}

    if mode == "prompt_template":
        prompt = render_prompt(case, mode, context="user_context")
        return {
            "case": case["id"],
            "mode": mode,
            "prompt_preview": prompt.split("\n")[:4],
            "variable_injection": True,
        }

    if mode == "components":
        single = single_chain(case, mode)
        return {
            "case": case["id"],
            "mode": mode,
            "component_count": len(CORE_COMPONENTS),
            "raw": single["raw"],
        }

    if mode == "output_parser":
        single = single_chain(case, mode)
        raw = to_json_text(case, single["raw"]) if case["output_format"] == "JSON" else single["raw"]
        parsed = parse_output(raw, case["output_format"])
        return {"case": case["id"], "mode": mode, "parsed_ok": parsed["ok"], "parsed": parsed["data"]}

    if mode == "chain_design":
        s = single_chain(case, mode)
        seq = sequential_chain(case, mode)
        return {
            "case": case["id"],
            "mode": mode,
            "single_len": len(tokenize(s["raw"])),
            "sequential_len": len(tokenize(seq["raw"])),
            "flow": ["입력", "변환", "생성"],
        }

    if mode == "memory_chat":
        chat = memory_chat(case, memory_store)
        return {"case": case["id"], "mode": mode, "history_size": chat["history_size"], "context": chat["context"]}

    if mode == "tool_agent":
        agent = run_agent(case["input"], knowledge_base)
        return {"case": case["id"], "mode": mode, "tool": agent["result"]["tool"], "cautions": agent["cautions"]}

    if mode == "retriever_base":
        chunks = split_documents(case["input"], chunk_size=8 + EXAMPLE_VARIANT)
        hits = retrieve_chunks("langchain chain", chunks, top_k=2)
        return {"case": case["id"], "mode": mode, "chunk_count": len(chunks), "hit_count": len(hits)}

    if mode == "rag_link":
        rag = rag_chain(case["input"], "VectorStore와 Retriever는 RAG의 검색 품질을 결정한다.")
        return {"case": case["id"], "mode": mode, "hits": len(rag["hits"]), "chunks": rag["chunks"]}

    if mode == "practice":
        bundle = practice_bundle(case, memory_store, knowledge_base)
        return {"case": case["id"], "mode": mode, **bundle}

    default_single = single_chain(case, mode)
    return {"case": case["id"], "mode": mode, "raw": default_single["raw"]}

def summarize_mode(mode, rows, memory_store):
    if mode == "overview":
        return {
            "goals": [
                "LangChain 구성요소 이해",
                "체인 기반 LLM 앱 설계",
                "프롬프트·메모리·도구·에이전트 연결 이해",
                "RAG 연계 기반 확보",
            ],
            "architecture": ["Model", "PromptTemplate", "Chain", "OutputParser", "Memory", "Retriever", "Tool", "Agent"],
        }
    if mode == "components":
        return {"components": CORE_COMPONENTS, "count": len(CORE_COMPONENTS)}
    if mode == "prompt_template":
        return {
            "prompt_template_usage": ["변수 주입", "템플릿 재사용", "사용자 입력 연결", "구조화 프롬프트 관리"],
            "sample_count": len(rows),
        }
    if mode == "chain_design":
        return {
            "chain_patterns": ["단일 체인", "순차 체인", "다단계 처리"],
            "flow": "입력 -> 변환 -> 생성",
        }
    if mode == "output_parser":
        success = sum(1 for row in rows if row.get("parsed_ok", False))
        return {
            "output_parser": ["문자열 파싱", "JSON 처리", "구조화 저장", "후처리 자동화"],
            "parsed_success": success,
            "total": len(rows),
        }
    if mode == "memory_chat":
        return {
            "memory_points": ["대화 이력 저장", "컨텍스트 유지", "세션별 응답 관리", "챗봇 흐름 구성"],
            "sessions": len(memory_store),
        }
    if mode == "tool_agent":
        tool_usage = {}
        for row in rows:
            tool = row.get("tool", "none")
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
        return {
            "tool_agent": ["검색", "계산", "API 호출", "Agent 동작/주의사항"],
            "tool_usage": tool_usage,
        }
    if mode == "retriever_base":
        return {
            "retriever_base": ["문서 로딩", "청크 분할", "검색"],
            "avg_chunks": round(sum(row.get("chunk_count", 0) for row in rows) / max(1, len(rows)), 2),
        }
    if mode == "rag_link":
        return {
            "rag_link": ["Retriever", "VectorStore", "검색근거 결합", "생성 응답"],
            "avg_hits": round(sum(row.get("hits", 0) for row in rows) / max(1, len(rows)), 2),
        }
    if mode == "practice":
        return {
            "practice_items": [
                "문서 요약 체인",
                "질의응답 체인",
                "간단한 챗봇",
                "외부 데이터 연동 기본 예제",
                "LangGraph 상태 흐름 제어",
                "LangSmith 실행 추적",
            ],
            "avg_trace_latency_ms": round(
                sum(row.get("trace_latency_ms", 0) for row in rows) / max(1, len(rows)),
                2,
            ),
            "result_count": len(rows),
        }
    return {"result_count": len(rows)}

def _lm_studio_langchain_demo():
    """
    LM Studio + LangChain 연동 실습.
    langchain-openai 의 ChatOpenAI 에 base_url 을 LM Studio 로 지정합니다.

    필요 패키지: pip install langchain-openai
    LM Studio: http://localhost:1234 에서 서버 실행 필요
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

    try:
        from langchain_openai import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate
    except ImportError:
        print("[LangChain+LM Studio] langchain-openai 패키지가 필요합니다: pip install langchain-openai")
        return

    lm_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    lm_model = os.getenv("LM_STUDIO_MODEL", "local-model")

    print(f"\n{'='*60}")
    print(f"[LangChain + LM Studio 실습] 모델: {lm_model}")
    print(f"{'='*60}")

    try:
        llm = ChatOpenAI(
            base_url=lm_url,
            api_key="lm-studio",
            model=lm_model,
            temperature=0.7,
        )

        # PromptTemplate + LLM 체인
        prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 친절한 한국어 AI 어시스턴트입니다."),
            ("user", "{question}"),
        ])
        chain = prompt | llm

        question = "LangChain 의 PromptTemplate 이 왜 유용한지 설명해주세요."
        print(f"\n[질문] {question}")
        response = chain.invoke({"question": question})
        print(f"[LM Studio 응답]\n{response.content}")
    except Exception as exc:
        print(f"[LangChain+LM Studio] 연결 실패: {exc}")
        print("  → LM Studio 가 실행 중인지 확인하세요 (포트 1234).")


def main():
    print("오늘 주제:", TOPIC)
    mode = resolve_mode()
    cases = build_cases()
    memory_store = {}
    knowledge_base = [
        "LangChain은 체인 기반 LLM 애플리케이션 프레임워크다.",
        "Retriever는 질문과 관련된 문서를 검색한다.",
        "Agent는 Tool을 선택해 외부 기능을 호출한다.",
        "OutputParser는 JSON 구조화를 도와준다.",
    ]

    rows = []
    for case in cases:
        row = execute_case(case, mode, memory_store, knowledge_base)
        rows.append(row)

    summary = summarize_mode(mode, rows, memory_store)
    print("모드:", mode)
    print("요약:", summary)

    # LM Studio + LangChain 실제 연동 실습
    _lm_studio_langchain_demo()

    return {
        "variant": EXAMPLE_VARIANT,
        "mode": mode,
        "sample_count": len(cases),
        "result_count": len(rows),
        "summary": summary,
    }

if __name__ == "__main__":
    main()
