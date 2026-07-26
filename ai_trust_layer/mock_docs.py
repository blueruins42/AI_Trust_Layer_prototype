"""
mock_docs.py - Mock document set + simulated RAG retrieval

Responsibility: load mock documents, simulate RAG retrieval, compute match scores, fetch document page content
Maps to PRD: Step 4.10 Mock document set spec + Step 5.2.4
"""

import os
import re
from models import Source
from config import MOCK_DOCS_DIR


# ── Document cache ─────────────────────────────────────────────────

_documents_cache: list[dict] | None = None


def load_mock_documents() -> list[dict]:
    """
    Load all .md files under the mock_documents/ directory.
    Parse each document's metadata (title, page markers, sections).

    Returns: [{"name": str, "content": str, "pages": [{"page": int, "text": str}]}]
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

        # Parse page markers: > page=X
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
    Parse page markers in the document.
    Format: [page content] > page=X [next page content] > page=Y ...
    Content before each page marker belongs to that page.
    """
    pages = []
    # Split by > page=X
    parts = re.split(r'>\s*page=(\d+)', content)

    # parts[0] = content before the first marker (belongs to the first page number)
    # parts[1] = the first page number
    # parts[2] = content between the first and second marker (belongs to the second page number)
    # parts[3] = the second page number
    # and so on: parts[i] is content, parts[i+1] is the page number for that content

    if len(parts) <= 1:
        # No page marker, treat the whole document as page 1
        pages.append({"page": 1, "text": content[:500]})
        return pages

    for i in range(0, len(parts) - 1, 2):
        page_text = parts[i].strip()
        page_num = int(parts[i + 1])
        pages.append({"page": page_num, "text": page_text[:500]})

    return pages


def mock_rag_retrieve(query: str, top_k: int = 3) -> list[Source]:
    """
    Simulate RAG retrieval:
    1. Do simple keyword tokenisation on the query
    2. Iterate over all document pages, compute keyword match scores
    3. Sort in descending order by score, take the top top_k
    4. Return a list of Source objects
    """
    documents = load_mock_documents()
    scored_results = []

    # Simple tokenisation: split by whitespace and ASCII punctuation, filter out words that are too short
    keywords = [w for w in re.split(r'[\s\.,;:!?]+', query) if len(w) >= 2]

    if not keywords:
        return []

    for doc in documents:
        for page in doc["pages"]:
            score = _calculate_match_score(keywords, doc["name"], page["text"])
            if score > 0.1:  # Minimum match threshold
                excerpt = page["text"][:200] if page["text"] else None
                scored_results.append(Source(
                    document_name=doc["name"],
                    page_number=page["page"],
                    match_score=round(min(score, 1.0), 2),
                    excerpt=excerpt,
                ))

    # Sort by match_score descending, take top top_k
    scored_results.sort(key=lambda x: x.match_score, reverse=True)
    return scored_results[:top_k]


def _calculate_match_score(keywords: list[str], doc_name: str, page_text: str) -> float:
    """
    Compute the keyword match score:
    - Exact keyword match: +0.3
    - Partial match (substring): +0.15
    - Document title match: +0.2
    - Finally normalised to 0.0-1.0
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
    Fetch document page content by document_name and page_number.
    Used for navigation in the DOCUMENT_VIEW state.
    """
    documents = load_mock_documents()

    for doc in documents:
        if doc["name"] == doc_name:
            for page in doc["pages"]:
                if page["page"] == page_number:
                    return page["text"]
            # Document exists but page number does not match, return the first page
            if doc["pages"]:
                return doc["pages"][0]["text"]

    return None
