"""
mock_docs.py - Mock 文档集 + 模拟 RAG 检索

职责：加载 Mock 文档、模拟 RAG 检索、计算匹配分数、获取文档页面内容
对应 PRD：Step 4.10 Mock 文档集规格 + Step 5.2.4
"""

import os
import re
from models import Source
from config import MOCK_DOCS_DIR


# ── 文档缓存 ──────────────────────────────────────────────

_documents_cache: list[dict] | None = None


def load_mock_documents() -> list[dict]:
    """
    加载 mock_documents/ 目录下所有 .md 文件。
    解析每份文档的元数据（标题、页码标记、章节）。

    返回: [{"name": str, "content": str, "pages": [{"page": int, "text": str}]}]
    """
    global _documents_cache
    if _documents_cache is not None:
        return _documents_cache

    documents = []

    if not os.path.exists(MOCK_DOCS_DIR):
        print(f"[mock_docs] Directory not found: {MOCK_DOCS_DIR}")
        return documents

    for filename in sorted(os.listdir(MOCK_DOCS_DIR)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(MOCK_DOCS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析页码标记: > page=X
        pages = _parse_pages(content)

        documents.append({
            "name": filename,
            "content": content,
            "pages": pages,
        })

    _documents_cache = documents
    print(f"[mock_docs] Loaded {len(documents)} documents")
    return documents


def _parse_pages(content: str) -> list[dict]:
    """
    解析文档中的页码标记。
    格式: [页面内容] > page=X [下一页内容] > page=Y ...
    每个页码标记之前的内容属于该页。
    """
    pages = []
    # 按 > page=X 分割
    parts = re.split(r'>\s*page=(\d+)', content)

    # parts[0] = 第一个标记之前的内容（属于第一个页码）
    # parts[1] = 第一个页码数字
    # parts[2] = 第一个标记之后到第二个标记之前的内容（属于第二个页码）
    # parts[3] = 第二个页码数字
    # 以此类推：parts[i] 是内容，parts[i+1] 是该内容对应的页码

    if len(parts) <= 1:
        # 没有页码标记，整篇文档作为第1页
        pages.append({"page": 1, "text": content[:500]})
        return pages

    for i in range(0, len(parts) - 1, 2):
        page_text = parts[i].strip()
        page_num = int(parts[i + 1])
        pages.append({"page": page_num, "text": page_text[:500]})

    return pages


def mock_rag_retrieve(query: str, top_k: int = 3) -> list[Source]:
    """
    模拟 RAG 检索：
    1. 对 query 做简单关键词分词
    2. 遍历所有文档页，计算关键词匹配分数
    3. 按分数降序排列，取前 top_k
    4. 返回 Source 对象列表
    """
    documents = load_mock_documents()
    scored_results = []

    # 简单分词：按空格和标点分割，过滤太短的词
    keywords = [w for w in re.split(r'[\s，。、？？]+', query) if len(w) >= 2]

    if not keywords:
        return []

    for doc in documents:
        for page in doc["pages"]:
            score = _calculate_match_score(keywords, doc["name"], page["text"])
            if score > 0.1:  # 最低匹配阈值
                excerpt = page["text"][:200] if page["text"] else None
                scored_results.append(Source(
                    document_name=doc["name"],
                    page_number=page["page"],
                    match_score=round(min(score, 1.0), 2),
                    excerpt=excerpt,
                ))

    # 按 match_score 降序，取前 top_k
    scored_results.sort(key=lambda x: x.match_score, reverse=True)
    return scored_results[:top_k]


def _calculate_match_score(keywords: list[str], doc_name: str, page_text: str) -> float:
    """
    计算关键词匹配分数：
    - 精确匹配关键词：+0.3
    - 部分匹配（子串）：+0.15
    - 文档标题匹配：+0.2
    - 最终归一化到 0.0-1.0
    """
    score = 0.0
    text_lower = page_text.lower()
    name_lower = doc_name.lower()

    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in name_lower:
            score += 0.2
        if kw_lower in text_lower:
            score += 0.3
        elif any(c in text_lower for c in kw_lower if len(c) > 1):
            score += 0.15

    return score


def get_document_page(doc_name: str, page_number: int) -> str | None:
    """
    根据 document_name 和 page_number 获取文档页面内容。
    用于 DOCUMENT_VIEW 状态的跳转。
    """
    documents = load_mock_documents()

    for doc in documents:
        if doc["name"] == doc_name:
            for page in doc["pages"]:
                if page["page"] == page_number:
                    return page["text"]
            # 文档存在但页码不匹配，返回第一个页面
            if doc["pages"]:
                return doc["pages"][0]["text"]

    return None
