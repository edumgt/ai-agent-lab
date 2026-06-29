# 이 파일은 www.edumgt.co.kr 의 에듀엠지티에 저작권이 있습니다

"""class449 example1: RAG 개요 · 단계 1/6 입문 이해 [class449]"""

TOPIC = "RAG 개요 · 단계 1/6 입문 이해 [class449]"
EXAMPLE_TEMPLATE = "rag"
EXAMPLE_VARIANT = 1

DOCUMENTS = [
    {
        "id": "D1",
        "title": "사내 보안 정책",
        "type": "PDF",
        "section": "보안",
        "text": "사내 보안 정책은 민감 데이터 조회 시 다중인증을 요구한다. 정책 위반은 보안팀 승인 절차로 처리한다.",
    },
    {
        "id": "D2",
        "title": "RAG 운영 가이드",
        "type": "TXT",
        "section": "운영",
        "text": "RAG 파이프라인은 문서 수집, 청크 분할, 임베딩 생성, 벡터 저장, 검색, 프롬프트 주입, 답변 생성 순서로 운영한다.",
    },
    {
        "id": "D3",
        "title": "고객지원 FAQ",
        "type": "HTML",
        "section": "FAQ",
        "text": "FAQ 챗봇은 환불 기준, 배송 일정, 계정 복구 질문을 자주 처리한다. 답변에는 출처 링크를 포함해야 한다.",
    },
    {
        "id": "D4",
        "title": "제품 안내 데이터",
        "type": "CSV",
        "section": "제품",
        "text": "CSV 문서에는 제품명, 가격, 업데이트일, 담당팀 메타데이터가 저장된다. 최신 컬럼 기준으로 검색 정확도를 관리한다.",
    },
    {
        "id": "D5",
        "title": "내부 회의록",
        "type": "PDF",
        "section": "회의록",
        "text": "검색 실패 사례는 query rewrite와 reranking으로 개선한다. 하이브리드 검색은 키워드와 벡터를 결합한다.",
    },
]

EMBEDDING_MODELS = [
    {"name": "ko-sbert", "strength": "한국어 의미 유사도", "cost": "중"},
    {"name": "multilingual-e5", "strength": "다국어 범용성", "cost": "중상"},
    {"name": "bge-m3", "strength": "검색/재정렬 균형", "cost": "중상"},
]

def resolve_mode():
    if "RAG 개요" in TOPIC:
        return "overview"
    if "문서 수집 전략" in TOPIC:
        return "pipeline"
    if "문서 청크 설계" in TOPIC:
        return "chunking"
    if "임베딩 생성" in TOPIC:
        return "embedding"
    if "벡터DB 기초" in TOPIC:
        return "vector_db"
    if "검색 품질 개선" in TOPIC:
        return "retrieval_tuning"
    if "프롬프트 결합" in TOPIC:
        return "langchain_rag"
    if "응답 검증/출처화" in TOPIC:
        return "grounding"
    if "평가 지표 설계" in TOPIC:
        return "evaluation"
    if "Agent 시스템 통합 구현" in TOPIC:
        return "practice"
    return "rag_general"

def tokenize(text):
    cleaned = str(text).lower()
    for ch in [",", ".", "(", ")", "/", ":", ";", "-", "_", "\n"]:
        cleaned = cleaned.replace(ch, " ")
    return [tok for tok in cleaned.split() if tok]

def load_documents():
    docs = list(DOCUMENTS)
    if EXAMPLE_VARIANT >= 4:
        docs.append(
            {
                "id": "D6",
                "title": "사내 위키 업데이트",
                "type": "TXT",
                "section": "위키",
                "text": "사내 문서 Q&A 시스템은 source 반환을 기본으로 하고 근거 없는 문장은 확인 필요로 표시한다.",
            }
        )
    if EXAMPLE_VARIANT >= 5:
        docs.append(
            {
                "id": "D7",
                "title": "릴리즈 노트",
                "type": "HTML",
                "section": "릴리즈",
                "text": "신규 버전은 PDF 검색과 FAQ 챗봇을 통합했고 검색 지연을 20퍼센트 줄였다.",
            }
        )
    return docs

def split_text_tokens(tokens, chunk_size, overlap):
    step = max(1, chunk_size - overlap)
    groups = []
    for start in range(0, len(tokens), step):
        part = tokens[start : start + chunk_size]
        if not part:
            continue
        groups.append(part)
        if start + chunk_size >= len(tokens):
            break
    return groups

def build_chunks(docs, chunk_size, overlap):
    chunks = []
    for doc in docs:
        token_groups = split_text_tokens(tokenize(doc["text"]), chunk_size, overlap)
        for idx, group in enumerate(token_groups, start=1):
            chunks.append(
                {
                    "chunk_id": f"{doc['id']}-c{idx}",
                    "source_id": doc["id"],
                    "source_type": doc["type"],
                    "title": doc["title"],
                    "section": doc["section"],
                    "text": " ".join(group),
                    "metadata": {
                        "doc_id": doc["id"],
                        "title": doc["title"],
                        "section": doc["section"],
                        "source_type": doc["type"],
                    },
                }
            )
    return chunks

def embed_text(text):
    vec = {}
    for tok in tokenize(text):
        vec[tok] = vec.get(tok, 0.0) + 1.0
    return vec

def cosine_similarity(vec_a, vec_b):
    keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(k, 0.0) * vec_b.get(k, 0.0) for k in keys)
    norm_a = sum(v * v for v in vec_a.values()) ** 0.5
    norm_b = sum(v * v for v in vec_b.values()) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)

def select_embedding_model(mode):
    if mode == "embedding":
        return EMBEDDING_MODELS[min(len(EMBEDDING_MODELS) - 1, EXAMPLE_VARIANT - 1)]
    if mode == "vector_db":
        return EMBEDDING_MODELS[2 if EXAMPLE_VARIANT >= 3 else 1]
    return EMBEDDING_MODELS[0 if EXAMPLE_VARIANT <= 2 else 1]

def build_index(chunks, model_name):
    index = []
    for chunk in chunks:
        row = dict(chunk)
        row["embedding_model"] = model_name
        row["vector"] = embed_text(chunk["text"])
        index.append(row)
    return index

def lexical_score(query, text):
    q_tokens = set(tokenize(query))
    if not q_tokens:
        return 0.0
    overlap = len(q_tokens & set(tokenize(text)))
    return overlap / len(q_tokens)

def vector_search(query, index, top_k=3):
    q_vec = embed_text(query)
    scored = []
    for row in index:
        vec_score = cosine_similarity(q_vec, row["vector"])
        key_score = lexical_score(query, row["text"])
        scored.append(
            {
                "chunk_id": row["chunk_id"],
                "source_id": row["source_id"],
                "source_type": row["source_type"],
                "title": row["title"],
                "section": row["section"],
                "text": row["text"],
                "vector_score": round(vec_score, 4),
                "keyword_score": round(key_score, 4),
            }
        )
    scored.sort(key=lambda x: x["vector_score"], reverse=True)
    return scored[:top_k]

def rerank_hits(query, hits):
    q_tokens = set(tokenize(query))
    reranked = []
    for item in hits:
        boost = 0.0
        if "사내" in q_tokens and item["source_id"] in {"D1", "D2", "D6"}:
            boost += 0.08
        if "faq" in q_tokens and item["source_type"] in {"HTML", "CSV"}:
            boost += 0.06
        if "pdf" in q_tokens and item["source_type"] == "PDF":
            boost += 0.06
        final = item["vector_score"] + 0.2 * item["keyword_score"] + boost
        row = dict(item)
        row["rerank_score"] = round(final, 4)
        reranked.append(row)
    reranked.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
    return reranked

def hybrid_search(query, index, top_k=3, use_rerank=False):
    candidates = vector_search(query, index, top_k=max(top_k, 6))
    merged = []
    for item in candidates:
        hybrid = 0.65 * item["vector_score"] + 0.35 * item["keyword_score"]
        row = dict(item)
        row["hybrid_score"] = round(hybrid, 4)
        merged.append(row)
    merged.sort(key=lambda x: x["hybrid_score"], reverse=True)
    if use_rerank:
        merged = rerank_hits(query, merged)
    return merged[:top_k]

def build_prompt(query, hits):
    contexts = []
    for h in hits:
        contexts.append(f"[{h['source_id']}|{h['chunk_id']}] {h['text']}")
    context_block = "\n".join(contexts) if contexts else "근거 문서 없음"
    return (
        "너는 사내 문서 Q&A 도우미다.\n"
        "규칙: 근거 없는 내용은 추측하지 말고 '확인 필요'라고 답해라.\n"
        f"질문: {query}\n"
        f"근거:\n{context_block}\n"
        "출력: 핵심 답변 + 출처 목록"
    )

def generate_answer(query, hits):
    prompt = build_prompt(query, hits)
    if not hits:
        return {
            "answer": "검색된 근거가 부족해 확인이 필요합니다.",
            "sources": [],
            "source_count": 0,
            "needs_review": True,
            "prompt_preview": prompt.splitlines()[0],
        }
    top_titles = ", ".join(dict.fromkeys(h["title"] for h in hits[:2]))
    sources = [f"{h['source_id']}:{h['title']}" for h in hits]
    answer = f"{query}에 대한 근거 문서는 {top_titles}입니다. 주요 정책/절차를 근거로 답변했습니다."
    return {
        "answer": answer,
        "sources": sources,
        "source_count": len(sources),
        "needs_review": False,
        "prompt_preview": prompt.splitlines()[0],
    }

def grounded_ratio(answer_text, hits):
    evidence_tokens = set()
    for h in hits:
        evidence_tokens.update(tokenize(h["text"]))
    ans_tokens = tokenize(answer_text)
    if not ans_tokens:
        return 0.0
    matched = sum(1 for tok in ans_tokens if tok in evidence_tokens)
    return round(matched / len(ans_tokens), 4)

def eval_retrieval(expected_sources, hits):
    expected = set(expected_sources)
    found = {h["source_id"] for h in hits}
    if not expected:
        return {
            "precision": round(1.0 if not found else 0.0, 4),
            "recall": 1.0,
            "matched": 0,
        }
    matched = len(expected & found)
    precision = matched / max(1, len(found))
    recall = matched / len(expected)
    return {"precision": round(precision, 4), "recall": round(recall, 4), "matched": matched}

def eval_answer(expected_keywords, report):
    answer = report.get("answer", "").lower()
    total = max(1, len(expected_keywords))
    matched = sum(1 for kw in expected_keywords if kw.lower() in answer)
    return {
        "keyword_accuracy": round(matched / total, 4),
        "with_source": report.get("source_count", 0) > 0,
    }

def build_cases(mode):
    cases = [
        {
            "name": "사내QnA",
            "query": "사내 보안 정책에서 다중인증은 언제 적용하나요?",
            "expected_sources": ["D1"],
            "expected_keywords": ["사내", "근거"],
        },
        {
            "name": "FAQ봇",
            "query": "FAQ 챗봇은 어떤 질문을 처리하나요?",
            "expected_sources": ["D3"],
            "expected_keywords": ["FAQ", "질문"],
        },
        {
            "name": "PDF검색",
            "query": "PDF 문서 기반 검색 품질을 어떻게 높이나요?",
            "expected_sources": ["D1", "D5"],
            "expected_keywords": ["검색", "품질"],
        },
    ]
    if EXAMPLE_VARIANT >= 2:
        cases.append(
            {
                "name": "파이프라인",
                "query": "RAG 전체 파이프라인 순서를 알려줘",
                "expected_sources": ["D2"],
                "expected_keywords": ["파이프라인", "근거"],
            }
        )
    if EXAMPLE_VARIANT >= 3:
        cases.append(
            {
                "name": "rerank",
                "query": "검색 실패 사례를 reranking으로 개선하는 방법은?",
                "expected_sources": ["D5"],
                "expected_keywords": ["검색", "개선"],
            }
        )
    if EXAMPLE_VARIANT >= 4:
        cases.append(
            {
                "name": "출처검증",
                "query": "출처 없는 답변을 줄이려면 무엇이 필요한가요?",
                "expected_sources": ["D6"],
                "expected_keywords": ["출처", "확인"],
            }
        )
    if mode == "overview":
        return cases[:2]
    if mode in {"embedding", "vector_db"}:
        return cases[:4]
    return cases

def run_case(case, mode, index):
    top_k = 2 + min(2, EXAMPLE_VARIANT // 2)
    use_hybrid = mode in {"retrieval_tuning", "evaluation", "practice"}
    use_rerank = mode in {"vector_db", "retrieval_tuning", "evaluation", "practice"}
    if use_hybrid:
        hits = hybrid_search(case["query"], index, top_k=top_k, use_rerank=use_rerank)
    else:
        hits = vector_search(case["query"], index, top_k=top_k)
        if use_rerank:
            hits = rerank_hits(case["query"], hits)[:top_k]
    report = generate_answer(case["query"], hits)
    retrieval_metrics = eval_retrieval(case["expected_sources"], hits)
    answer_metrics = eval_answer(case["expected_keywords"], report)
    ground = grounded_ratio(report.get("answer", ""), hits)
    return {
        "name": case["name"],
        "query": case["query"],
        "hit_sources": [h["source_id"] for h in hits],
        "report": report,
        "retrieval": retrieval_metrics,
        "answer": answer_metrics,
        "grounded_ratio": ground,
        "hallucination_risk": ground < 0.2 and report.get("source_count", 0) == 0,
    }

def summarize_mode(mode, docs, chunks, rows, model_name, chunk_size, overlap):
    avg_recall = round(sum(r["retrieval"]["recall"] for r in rows) / max(1, len(rows)), 4)
    avg_answer = round(sum(r["answer"]["keyword_accuracy"] for r in rows) / max(1, len(rows)), 4)
    avg_grounded = round(sum(r["grounded_ratio"] for r in rows) / max(1, len(rows)), 4)
    with_source_count = sum(1 for r in rows if r["report"]["source_count"] > 0)

    if mode == "overview":
        return {
            "goals": [
                "RAG 필요성과 구조 이해",
                "외부 문서 검색으로 답변 품질 개선",
                "벡터DB·임베딩·검색 파이프라인 습득",
                "사내 문서 Q&A 구현 역량 확보",
            ],
            "llm_limitations": ["최신 정보 반영 한계", "사내 정보 접근 한계", "근거 없는 환각 위험"],
            "architecture": ["검색", "문맥 주입", "생성", "출처 반환"],
        }
    if mode == "pipeline":
        return {
            "pipeline_steps": ["문서 수집", "chunking", "임베딩", "벡터 저장", "검색", "프롬프트 주입", "답변 생성"],
            "document_count": len(docs),
            "chunk_count": len(chunks),
        }
    if mode == "chunking":
        return {
            "formats": ["PDF", "TXT", "HTML", "CSV"],
            "chunking": {"chunk_size": chunk_size, "overlap": overlap},
            "metadata": ["doc_id", "title", "section", "source_type"],
        }
    if mode == "embedding":
        return {
            "embedding": ["임베딩 개념", "문장 의미 벡터", "cosine similarity", "모델 선택 기준"],
            "selected_model": model_name,
            "avg_recall": avg_recall,
        }
    if mode == "vector_db":
        return {
            "vector_db": ["Chroma", "FAISS", "Qdrant"],
            "indexing": "벡터 upsert + Top-K 검색",
            "reranking": "후보 재정렬로 정답률 향상",
            "avg_recall": avg_recall,
        }
    if mode == "retrieval_tuning":
        return {
            "improvements": ["Top-K 조정", "reranking", "검색 실패 사례 분석"],
            "hybrid_search": "키워드 + 벡터 결합",
            "avg_recall": avg_recall,
            "avg_answer_accuracy": avg_answer,
        }
    if mode == "langchain_rag":
        return {
            "langchain_rag": ["Retriever 구성", "Prompt 문맥 주입", "검색 기반 생성", "source 반환", "hallucination 감소"],
            "with_source_count": with_source_count,
        }
    if mode == "grounding":
        return {
            "source_return": "doc_id:title 형식",
            "avg_grounded_ratio": avg_grounded,
            "hallucination_flags": sum(1 for r in rows if r["hallucination_risk"]),
        }
    if mode == "evaluation":
        return {
            "evaluation_points": ["검색 정확도", "답변 정확도", "chunking 개선", "프롬프트 튜닝", "하이브리드 검색"],
            "avg_recall": avg_recall,
            "avg_answer_accuracy": avg_answer,
            "avg_grounded_ratio": avg_grounded,
        }
    if mode == "practice":
        return {
            "practice": ["사내 문서 질의응답", "FAQ 챗봇", "PDF 기반 검색 시스템", "출처 포함 답변 생성"],
            "result_count": len(rows),
            "with_source_count": with_source_count,
        }
    return {"result_count": len(rows), "avg_recall": avg_recall, "avg_answer_accuracy": avg_answer}

def _lm_studio_rag_demo():
    """
    LM Studio 를 LLM 백엔드로 사용하는 간이 RAG 데모.
    검색된 컨텍스트를 프롬프트에 주입해 답변을 생성합니다.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        from lmstudio_config import call_lm, LM_STUDIO_AVAILABLE, LM_MODEL
    except ImportError:
        return

    if not LM_STUDIO_AVAILABLE:
        return

    # 간이 문서 컬렉션
    docs = [
        "RAG 파이프라인은 문서 수집, 청크 분할, 임베딩 생성, 벡터 검색, 프롬프트 주입, 답변 생성 단계로 구성됩니다.",
        "임베딩은 텍스트를 고차원 벡터로 변환해 의미 기반 유사도 검색을 가능하게 합니다.",
        "Chroma, FAISS, Qdrant 는 대표적인 로컬 벡터 데이터베이스입니다.",
        "LM Studio 는 GGUF 형식의 모델을 로컬에서 실행하며 OpenAI 호환 API 를 제공합니다.",
    ]

    query = "RAG 에서 임베딩의 역할이 무엇인가요?"

    # 키워드 기반 간이 검색 (실습용)
    keywords = set(query.replace("?", "").replace(".", "").split())
    scored = []
    for doc in docs:
        score = sum(1 for kw in keywords if kw in doc)
        scored.append((score, doc))
    retrieved = [doc for _, doc in sorted(scored, reverse=True)[:2]]

    context = "\n".join(f"- {d}" for d in retrieved)
    messages = [
        {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다. 제공된 컨텍스트만 사용해 답변하세요."},
        {"role": "user", "content": f"[컨텍스트]\n{context}\n\n[질문]\n{query}"},
    ]

    print(f"\n{'='*60}")
    print(f"[LM Studio RAG 실습] 모델: {LM_MODEL}")
    print(f"질문: {query}")
    print(f"검색된 컨텍스트:\n{context}")
    print(f"{'='*60}")

    result = call_lm(messages, temperature=0.3, max_tokens=256)
    if result:
        print(f"\n[LM Studio 생성 답변]\n{result}")
    else:
        print("[LM Studio] 연결 실패 — LM Studio 가 실행 중인지 확인하세요 (포트 1234).")


def main():
    print("오늘 주제:", TOPIC)
    mode = resolve_mode()
    docs = load_documents()
    chunk_size = 8 + EXAMPLE_VARIANT
    overlap = min(3, 1 + EXAMPLE_VARIANT // 2)
    chunks = build_chunks(docs, chunk_size=chunk_size, overlap=overlap)
    model = select_embedding_model(mode)
    index = build_index(chunks, model_name=model["name"])
    cases = build_cases(mode)

    rows = []
    for case in cases:
        rows.append(run_case(case, mode, index))

    summary = summarize_mode(mode, docs, chunks, rows, model["name"], chunk_size, overlap)
    print("모드:", mode)
    print("선택 임베딩 모델:", model)
    print("요약:", summary)

    # LM Studio RAG 실습
    _lm_studio_rag_demo()

    return {
        "variant": EXAMPLE_VARIANT,
        "mode": mode,
        "documents": len(docs),
        "chunks": len(chunks),
        "cases": len(cases),
        "summary": summary,
    }

if __name__ == "__main__":
    main()
