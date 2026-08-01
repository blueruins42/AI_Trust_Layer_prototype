
-  Working prototype name: AI Trust Layer
- Phase: Full Product Design Process - Step 5
- Date: 2026-08-01
- Upstream inputs: All confirmed deliverables from Step 1–4
- This step delivers: project directory structure, module breakdown, dependency list, environment configuration, development milestones, and core function signatures

---

## 5.0 Architecture Decision Lock-in

### N1 Latency Control: Option A (single-request full response) 

| Decision Item | Specification |
|--------|------|
| Number of API calls | 1 |
| Returned content | Complete JSON (answer + sources + jargon_glossary + verification_advice + metadata) |
| First-response target | ≤ 2s (show st.spinner loading animation) |
| Total timeout ceiling | 3s (show degraded prompt on timeout) |
| Detail-expansion latency | 0s (data is already in memory; user clicks expander and it renders instantly) |

> **Consistency note**: The progressive disclosure pseudo-code in Step 3.6 demonstrated a "two-request" pattern, which has now been superseded by Option A confirmed in Step 4.8. All architecture design in Step 5 follows Option A.

---

## 5.1 Project Directory Structure

```
ai_trust_layer/
├── app.py                      # Streamlit entry file (main controller)
├── config.py                   # Global configuration (API key, model name, timeout threshold)
├── models.py                   # Pydantic data contract models (DC)
├── mock_docs.py                # Mock document set + simulated RAG retrieval
├── llm_api.py                  # LLM API call layer (OpenAI structured output)
├── frontend.py                 # Front-end trust interface rendering (Li Ming's perspective: F1–F4)
├── admin.py                    # Admin Dashboard rendering (Wang Fang's perspective: F7)
├── interaction_log.py          # Interaction logging and metric calculation
├── .env                        # Environment variables (API key, not in version control)
├── .env.example                # Environment variable template (in version control)
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependency list
├── README.md                   # Project documentation
└── mock_documents/             # Mock document set (5–10 simulated project documents)
    ├── proj_XX_tech_spec_v3.2.md
    ├── proj_XX_signal_design.md
    ├── equipment_catalog_2024.md
    ├── national_standard_GB_T.md
    ├── proj_YY_line_overview.md
    ├── proj_YY_signal_plan.md
    ├── tender_template_standard.md
    ├── zdj200_manual.md
    ├── cable_spec_railway.md
    └── pricing_guide_2024.md
```

### Directory Design Principles

| Principle | Description |
|------|------|
| **Single responsibility per file** | Each .py file owns one clear functional domain, no more than 200 lines |
| **Minimal entry point** | app.py only performs routing dispatch (front-end / back-end switching), contains no business logic |
| **Data-code separation** | mock_documents/ holds pure Markdown files, dynamically loaded by code |
| **Externalized config** | Sensitive info such as API key goes in .env; config.py reads it |
| **Prototype-friendly** | No tests/ directory (testing planned separately in Step 8), no CI/CD |

---

## 5.2 Module Breakdown and Core Function Signatures

### 5.2.1 `app.py` — Streamlit Entry File

**Responsibility**: Page routing, session_state initialization, front-end / back-end switching

```python
import streamlit as st
from frontend import render_frontend
from admin import render_admin
from interaction_log import init_log

def init_session_state():
    """
    Initialize all session_state variables:
    - view_mode: "front" | "admin"
    - interaction_log: list[dict]
    - current_response: TrustLayerResponse | None
    - jargon_views: dict[str, int]  # jargon view count
    - verification_clicks: int       # verification click count
    """

def main():
    """
    Main function:
    1. st.set_page_config(title, icon, layout)
    2. init_session_state()
    3. Render front-end or back-end based on st.session_state["view_mode"]
    4. Provide switch button
    """
```

**Key implementation details**:
- `st.set_page_config(page_title="AI Trust Layer", layout="wide")`
- Front-end / back-end switching is controlled via `st.session_state["view_mode"]`, not URL routing
- The switch button is placed at the top of the page sidebar or main area

---

### 5.2.2 `config.py` — Global Configuration

**Responsibility**: Centrally manage all configuration items; read sensitive info from .env

```python
import os
from dotenv import load_dotenv

load_dotenv()

# LLM API configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "3.0"))  # seconds

# ── Bulletproof Demo Mode ────────────────────────────────
# True  → llm_api.py skips the OpenAI call and returns a pre-written static JSON (0 latency, 100% controllable)
# False → normal OpenAI API call
#
# Use cases:
#   - Recording demo videos / live interview demos → set to True
#   - Debugging the front-end UI → set to True (no API quota consumed)
#   - Verifying API integration / testing real confidence → set to False
#
# How to toggle: modify the MOCK_LLM_MODE value in .env, or change the default here
MOCK_LLM_MODE: bool = os.getenv("MOCK_LLM_MODE", "true").lower() == "true"
# ──────────────────────────────────────────────────────────

# Confidence thresholds
CONFIDENCE_HIGH_THRESHOLD: float = 0.75
CONFIDENCE_LOW_THRESHOLD: float = 0.50

# Data contract constraints
MAX_SOURCES: int = 5
MAX_JARGON_TERMS: int = 10
MAX_ANSWER_LENGTH: int = 2000

# Mock document path
MOCK_DOCS_DIR: str = os.path.join(os.path.dirname(__file__), "mock_documents")
```

#### `.env.example` update (MOCK_LLM_MODE added)

```bash
# OpenAI API configuration
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT=3.0

# Bulletproof Demo Mode: true=offline static response (for recordings/demos) / false=real API call
MOCK_LLM_MODE=true
```

> **Default value `true`**: During development, mock mode is the default to avoid consuming API quota. Switch to `false` only when verifying real API integration. For Demo video recording, `true` must be kept.

---

### 5.2.3 `models.py` — Pydantic Data Contract Models

**Responsibility**: Define TrustLayerResponse and all sub-models, validation logic, and degradation handling

**Directly reuse the complete Pydantic model definitions from Step 4.7**, including:

```python
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from enum import Enum
from datetime import datetime

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Answer(BaseModel): ...
class Source(BaseModel): ...
class JargonTerm(BaseModel): ...
class ActionLink(BaseModel): ...
class VerificationAdvice(BaseModel): ...
class QueryMetadata(BaseModel): ...
class TrustLayerResponse(BaseModel): ...

def validate_response(raw_json: dict) -> TrustLayerResponse | None:
    """Validate JSON returned by the LLM; return object if passed, otherwise return degraded response"""

def create_fallback_response(raw_json: dict) -> TrustLayerResponse:
    """Degradation handling: construct a minimal usable response"""

def determine_confidence_level(score: float) -> ConfidenceLevel:
    """Calculate confidence tier from score (fallback logic used when LLM does not return a level)"""
```

> **Estimated file length**: ~120 lines (model definitions + validation logic + degradation handling)

---

### 5.2.4 `mock_docs.py` — Mock Document Set + Simulated RAG Retrieval

**Responsibility**: Load mock documents, simulate RAG retrieval, compute match scores

```python
import os
from models import Source
from config import MOCK_DOCS_DIR

def load_mock_documents() -> list[dict]:
    """
    Load all .md files under mock_documents/.
    Parse metadata (title, page markers, sections) for each document.
    Return [{"name", "content", "pages": [{"page": int, "text": str}]}]
    """

def mock_rag_retrieve(query: str, top_k: int = 3) -> list[Source]:
    """
    Simulate RAG retrieval:
    1. Simple keyword tokenization of query
    2. Iterate all document pages and compute keyword match scores
    3. Sort by score descending, take top_k
    4. Return list of Source objects
    
    Match score calculation:
    - Exact keyword match: +0.3
    - Partial match (substring): +0.15
    - Document title match: +0.2
    - Final normalization to 0.0-1.0
    """

def get_document_page(doc_name: str, page_number: int) -> str | None:
    """
    Get document page content by document_name and page_number.
    Used for DOCUMENT_VIEW state navigation.
    """
```

**Example mock document structure** (`proj_XX_tech_spec_v3.2.md`):

```markdown
# XX Project Technical Specification

**Document No.**: DOC-001
**Version**: v3.2

---

## Page 1: Project Overview

This project is the railway low-voltage systems integration works for the signalling system of the XX urban rail transit line...

> page=1

## Page 2: Equipment List

Main equipment includes:
- ZDJ-200 electric point machine ×24 units
- Wayside signal ×36 units
- Track circuit ×48 sections

> page=2

## Page 15: Technical Specifications

The signalling system adopts the CBTC standard; core equipment...

> page=15
```

> **Estimated file length**: ~100 lines (loading + retrieval + page fetch)

---

### 5.2.5 `llm_api.py` — LLM API Call Layer (with Bulletproof Demo Mode)

**Responsibility**: Call OpenAI API, construct prompt, handle timeout and exceptions, **Mock-mode dispatch**

```python
import json
import time
from datetime import datetime
from openai import OpenAI
from models import TrustLayerResponse, validate_response, create_fallback_response, ConfidenceLevel
from mock_docs import mock_rag_retrieve
from config import OPENAI_API_KEY, LLM_MODEL, LLM_TIMEOUT, MOCK_LLM_MODE

# System Prompt (reuse the template from Step 4.7 directly)
SYSTEM_PROMPT: str = """You are an answer generator for an enterprise RAG system... (full template in Step 4.7)"""

# ── Bulletproof Demo Mode: pre-written static responses ─────────────────
# 3 perfect JSONs, precisely matching Scene 2/3/4 of the Step 6 Demo Script
# Each strictly conforms to the Step 4.7 Pydantic Schema and returns with 0 latency

MOCK_RESPONSES: dict[str, dict] = {
    # Scene 2: high confidence (green label, details collapsed, no alert)
    "high": {
        "answer": {
            "text": "The XX project signalling system adopts the CBTC (Communication-Based Train Control) standard. Through train-to-ground communication, the system achieves real-time train positioning and moving block operation, increasing line capacity by approximately 15-20% compared with conventional fixed block systems.",
            "confidence_score": 0.92,
            "confidence_level": "high",
            "is_inferred": False
        },
        "sources": [
            {"document_name": "proj_XX_tech_spec_v3.2.md", "page_number": 15, "match_score": 0.95, "excerpt": "The signalling system adopts the CBTC standard; core equipment includes the ZDJ-200 electric point machine, wayside signals and track circuits..."},
            {"document_name": "proj_XX_signal_design.md", "page_number": 3, "match_score": 0.88, "excerpt": "The signalling system design of this project is based on the CBTC standard, implementing moving block control..."}
        ],
        "jargon_glossary": [
            {"term": "CBTC", "definition": "Communication-Based Train Control, a train control system based on continuous train-to-ground communication", "plain_language": "It uses radio to let trains and wayside equipment chat in real time, so the system always knows where each train is and how fast it is going"},
            {"term": "moving block", "definition": "Moving Block, a block system in which the safe separation between trains is calculated dynamically based on real-time speed", "plain_language": "The safe gap between trains is not fixed; it is calculated on the fly—faster trains get more space, stopped trains can be closer"}
        ],
        "verification_advice": {
            "needs_verification": False,
            "fields_to_check": [],
            "action_link": None
        },
        "metadata": {
            "query_id": "mock-high-001",
            "timestamp": "2026-07-24T10:00:00",
            "response_time_ms": 120,
            "model_used": "mock-static",
            "documents_searched": 10,
            "documents_matched": 2
        }
    },

    # Scene 3: low confidence (red alert banner, not closable, action link)
    "low": {
        "answer": {
            "text": "Based on the available documents, no explicit cost budget record for the YY line project was found in the current database. The following answer is inferred from similar project experience and is for reference only: railway low-voltage systems integration works generally account for 8-12% of total line investment, and the signalling system accounts for approximately 35-40% of the low-voltage portion.",
            "confidence_score": 0.28,
            "confidence_level": "low",
            "is_inferred": True
        },
        "sources": [
            {"document_name": "pricing_guide_2024.md", "page_number": 22, "match_score": 0.31, "excerpt": "Cost reference ranges for various line projects... (specific data for YY line not included)"}
        ],
        "jargon_glossary": [
            {"term": "low-voltage integration", "definition": "An engineering model that unifies the design, construction and management of low-voltage railway subsystems such as communications, signalling and security", "plain_language": "It means bundling all the non-power-heavy stuff on the platform—communications, CCTV, public address—under one team"}
        ],
        "verification_advice": {
            "needs_verification": True,
            "fields_to_check": ["specific cost amount", "budget approval document number", "funding source"],
            "action_link": {
                "text": "View source document page 22",
                "document": "pricing_guide_2024.md",
                "page": 22
            }
        },
        "metadata": {
            "query_id": "mock-low-001",
            "timestamp": "2026-07-24T10:01:00",
            "response_time_ms": 95,
            "model_used": "mock-static",
            "documents_searched": 10,
            "documents_matched": 1
        }
    },

    # Scene 4: medium confidence (yellow label, source expander expanded, jargon expander collapsed)
    "medium": {
        "answer": {
            "text": "Main technical parameters of the ZDJ-200 electric point machine: rated voltage DC160V, rated current ≤4.5A, switching force 5880N, operating time ≤6s, suitable for 50kg/m and 60kg/m rail. Some parameters come from the equipment manual and some are inferred from similar equipment; it is recommended to check the original specification.",
            "confidence_score": 0.62,
            "confidence_level": "medium",
            "is_inferred": True
        },
        "sources": [
            {"document_name": "zdj200_manual.md", "page_number": 8, "match_score": 0.71, "excerpt": "ZDJ-200 electric point machine technical parameter table: rated voltage DC160V, switching force 5880N..."},
            {"document_name": "equipment_catalog_2024.md", "page_number": 12, "match_score": 0.58, "excerpt": "Point machine selection reference table (including ZDJ-200 parameter comparison)..."}
        ],
        "jargon_glossary": [
            {"term": "electric point machine", "definition": "Electric Switch Machine, an electric device used to throw and lock turnouts/points", "plain_language": "It is the electric motor that controls which direction a rail turnout points"},
            {"term": "switching force", "definition": "Point Machine Force, the force output by the point machine when pulling a turnout to switch, measured in newtons (N)", "plain_language": "How much force the motor has to move the rails"},
            {"term": "operating time", "definition": "Operating Time, the time from when the point machine starts switching until it completes locking", "plain_language": "How many seconds it takes to move a turnout from one position to the other"}
        ],
        "verification_advice": {
            "needs_verification": True,
            "fields_to_check": ["rated current value", "applicable rail type"],
            "action_link": {
                "text": "View ZDJ-200 manual page 8",
                "document": "zdj200_manual.md",
                "page": 8
            }
        },
        "metadata": {
            "query_id": "mock-medium-001",
            "timestamp": "2026-07-24T10:02:00",
            "response_time_ms": 108,
            "model_used": "mock-static",
            "documents_searched": 10,
            "documents_matched": 2
        }
    },

    # No-match: query does not map to any known topic -> zero relevant documents.
    # Surfaces the graceful "no relevant documents" banner on the frontend instead of
    # silently returning a high-confidence answer. The 3 demo scenes (signal/budget/switch) above are untouched.
    "nomatch": {
        "answer": {
            "text": "I couldn't find any documents relevant to your question in the current database. Try rephrasing with project-specific keywords (e.g. signalling system, point machine, construction budget).",
            "confidence_score": 0.0,
            "confidence_level": "low",
            "is_inferred": True
        },
        "sources": [],
        "jargon_glossary": [],
        "verification_advice": {
            "needs_verification": False,
            "fields_to_check": [],
            "action_link": None
        },
        "metadata": {
            "query_id": "mock-nomatch-001",
            "timestamp": "2026-07-24T10:03:00",
            "response_time_ms": 60,
            "model_used": "mock-static",
            "documents_searched": 10,
            "documents_matched": 0
        }
    }
}

# Query keywords -> mock scenario mapping (ensures queries in the Demo Script precisely trigger the corresponding scenario; falls back to nomatch when no keyword matches)
MOCK_QUERY_MAP: list[tuple[list[str], str]] = [
    (["budget", "cost", "quotation", "price", "investment"], "low"),       # Scene 3
    (["point machine", "parameter", "specification", "technical parameter"], "medium"),        # Scene 4
    (["signal", "standard", "CBTC", "equipment", "system"], "high"),       # Scene 2 (default scenario)
]


def get_mock_response(user_query: str) -> TrustLayerResponse:
    """
    Bulletproof demo mode: Match pre-written static responses based on query keywords.
    
    Matching logic:
    1. Iterate MOCK_QUERY_MAP; the first keyword group hit wins
    2. No match -> "nomatch" scenario (empty sources -> frontend shows no-docs banner)
    
    Returns: Pydantic-validated TrustLayerResponse object
    """
    query_lower = user_query.lower()
    matched_scenario = "nomatch"  # default: no keyword match => no relevant documents

    for keywords, scenario in MOCK_QUERY_MAP:
        if any(kw in user_query for kw in keywords):
            matched_scenario = scenario
            break

    raw_json = MOCK_RESPONSES[matched_scenario]
    
    # Update timestamp to current time (so logs look realistic)
    raw_json["metadata"]["timestamp"] = datetime.now().isoformat()
    raw_json["metadata"]["query_id"] = f"mock-{matched_scenario}-{int(time.time())}"
    
    response = validate_response(raw_json)
    if response is None:
        # Pre-written data should not fail validation, but keep as bulletproof insurance
        response = create_fallback_response(raw_json)
    
    return response


def call_llm_api(user_query: str) -> TrustLayerResponse:
    """
    Complete API call flow (Option A: single request returns full payload):
    
    Warning: Bulletproof Demo Mode is checked first:
    if MOCK_LLM_MODE == True:
        -> Skip OpenAI and directly return get_mock_response(user_query)
        -> 0 latency, 100% controllable, no API quota consumed
    
    Normal flow (MOCK_LLM_MODE == False):
    1. Call mock_rag_retrieve to get relevant document snippets
    2. Build user prompt (document snippets + user query)
    3. Call OpenAI API (structured output mode)
    4. Record response time
    5. Pydantic validation
    6. Return TrustLayerResponse object
    
    Exception handling:
    - Timeout -> return degraded response
    - API error -> return degraded response
    - JSON validation failure -> return degraded response
    """

    # ── Bulletproof Demo Mode: return pre-written response with 0 latency ──
    if MOCK_LLM_MODE:
        return get_mock_response(user_query)

    # ── Normal mode: real OpenAI API call ──
    start_time = time.time()
    try:
        retrieved_docs = mock_rag_retrieve(user_query)
        user_prompt = build_user_prompt(retrieved_docs, user_query)

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            timeout=LLM_TIMEOUT
        )

        raw_json = json.loads(response.choices[0].message.content)
        trust_response = validate_response(raw_json)
        
        if trust_response is None:
            trust_response = create_fallback_response(raw_json)
        
        return trust_response

    except Exception as e:
        # Timeout / API error / JSON parse failure -> degraded response
        return create_fallback_response({})


def build_user_prompt(retrieved_docs: list, user_query: str) -> str:
    """Build User Prompt: retrieved document snippets + user question (only called when MOCK_LLM_MODE=False)"""

def generate_query_id() -> str:
    """Generate a unique query ID (timestamp + random number)"""

def calculate_response_time(start_time: float) -> int:
    """Calculate response time in milliseconds"""
```

#### Bulletproof Demo Mode Data Flow

```
User enters query
    │
    ▼
call_llm_api(user_query)
    │
    ├── MOCK_LLM_MODE == True ?
    │       │
    │       ├── YES → get_mock_response(query)
    │       │            │
    │       │            ├── Keyword match → "high" / "medium" / "low" / "nomatch"
    │       │            ├── Take MOCK_RESPONSES[scenario]
    │       │            ├── Update timestamp + query_id
    │       │            ├── Pydantic validation
    │       │            └── Return TrustLayerResponse (0 latency)
    │       │
    │       └── NO  → Normal OpenAI API flow (Option A)
    │                    │
    │                    ├── mock_rag_retrieve(query)
    │                    ├── build_user_prompt(docs, query)
    │                    ├── openai.chat.completions.create(...)
    │                    ├── validate_response(raw_json)
    │                    └── Return TrustLayerResponse (≤3s or degraded)
    │
    ▼
Return TrustLayerResponse → frontend.py renders
```

> **Option A implementation note**: A single `create()` call returns the complete JSON with no second request. After receiving `trust_response`, the front-end directly renders Level 0 + Level 1 (expander collapsed state); when the user clicks to expand, latency is 0.

> **Bulletproof Demo Mode note**: When `MOCK_LLM_MODE = True`, the entire OpenAI call chain is short-circuited and returns the pre-written static JSON. Response time is ~0ms; during Demo recording, the confidence tiers, source counts, and jargon content for Scene 2/3/4 are 100% controllable. It even runs offline during a live interview demo.

> **Estimated file length**: ~160 lines (original ~100 lines + mock response data ~40 lines + mock dispatch logic ~20 lines)

---

### 5.2.6 `frontend.py` — Front-end Trust Interface Rendering

**Responsibility**: Render all UI from Li Ming's perspective (F1–F4 + low-confidence alert + progressive disclosure)

```python
import streamlit as st
from models import TrustLayerResponse, ConfidenceLevel

def render_frontend():
    """
    Front-end main render function:
    1. Display search box + placeholder text (IDLE state)
    2. User submits query → call llm_api.call_llm_api()
    3. Render response result (render_response)
    4. Record interaction log
    """

def render_response(response: TrustLayerResponse):
    """
    Progressive rendering core function (Option A: data already in memory, 0-latency expansion):
    
    Render order:
    1. render_confidence_label()     — confidence label (always shown)
    2. render_alert_banner()          — low-confidence alert (only shown for low)
    3. st.markdown(response.answer.text)  — AI answer text
    4. render_details_expander()      — details expander (progressive disclosure core)
    """

def render_confidence_label(level: ConfidenceLevel, is_inferred: bool):
    """
    Three-tier differentiated label rendering:
    - high  → st.success("High Confidence")
    - medium → st.warning("Partial Match · Verify Recommended")
    - low   → st.error("Low Confidence · Human Verification Required")
    - is_inferred → append st.caption("(AI inferred)")
    """

def render_alert_banner(verification_advice):
    """
    Low-confidence alert banner (only called when confidence_level == "low"):
    - Light red background + red border
    - Plain-language warning text
    - Action link button (st.button + session_state navigation)
    - Not closable
    """

def render_details_expander(response: TrustLayerResponse):
    """
    Details expander (post-bug-fix version):
    
    Core implementation:
        expanded = (response.answer.confidence_level == ConfidenceLevel.MEDIUM)
        
        with st.expander("Details", expanded=expanded):
            render_sources(response.sources)                    # source list
            with st.expander("Jargon explanation", expanded=False):    # independent jargon expander
                render_jargon_glossary(response.jargon_glossary)
            render_verification_advice(response.verification_advice)
    
    Warning: Do NOT use st.button to control expand/collapse (Bug 1 fix)
    Warning: Do NOT use a "half-expanded" concept (Bug 2 fix; use dual expanders instead)
    """

def render_sources(sources: list):
    """
    F1 Source attribution rendering:
    - Sort descending by match_score
    - Each entry: document name · page X + match score % + excerpt expander
    - Empty array fallback text
    """

def render_jargon_glossary(jargon_glossary: list):
    """
    F3 Jargon explanation rendering:
    - Each term: plain-language explanation (shown by default) + formal definition expander (collapsed)
    - Update st.session_state["jargon_views"] on view
    """

def render_verification_advice(verification_advice):
    """
    F4 Verification advice rendering:
    - needs_verification == false → do not show
    - confidence_level == "low" → show "See alert banner above"
    - Others → show field list + action link button
    - Clicking action link → st.session_state navigation to DOCUMENT_VIEW
    """

def render_document_view(doc_name: str, page_number: int):
    """
    DOCUMENT_VIEW state rendering:
    - Get content from mock_docs.get_document_page()
    - Show document name + page number + original content
    - Back button
    """
```

> **Estimated file length**: ~250 lines (largest file; could be split, but acceptable at prototype stage)

---

### 5.2.7 `admin.py` — Admin Dashboard Rendering

**Responsibility**: Render Wang Fang's perspective, the F7 monitoring dashboard

```python
import streamlit as st
from interaction_log import calculate_admin_metrics

def render_admin():
    """
    Admin Dashboard main render function:
    1. Get logs from st.session_state["interaction_log"]
    2. Call calculate_admin_metrics() to compute metrics
    3. Render three metric cards
    4. Render top 5 high-frequency jargon terms
    5. Render recent query records table
    """

def render_metric_cards(metrics: dict):
    """
    Three metric cards (st.columns(3) + st.metric):
    - Trust health (verification click rate)
    - Low-confidence trigger rate
    - Total query count
    """

def render_top_jargon(jargon_list: list):
    """Top 5 most-viewed jargon terms (st.table or st.dataframe)"""

def render_recent_queries(queries: list):
    """Most recent 10 query records (st.dataframe)"""
```

> **Estimated file length**: ~80 lines

---

### 5.2.8 `interaction_log.py` — Interaction Logging and Metric Calculation

**Responsibility**: Manage interaction logs, calculate Admin Dashboard metrics

```python
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import List
import uuid
from datetime import datetime

@dataclass
class InteractionLogEntry:
    query_id: str
    timestamp: str
    user_query: str
    confidence_level: str
    response_time_ms: int
    viewed_details: bool = False
    viewed_jargon: list = field(default_factory=list)
    clicked_verification: bool = False
    documents_searched: int = 0
    documents_matched: int = 0

def init_log():
    """Initialize log-related variables in st.session_state"""

def log_interaction(response, user_query: str, response_time: int):
    """Create a log entry and store it in st.session_state["interaction_log"]"""

def update_jargon_view(term: str):
    """Record that the user viewed a jargon term"""

def update_verification_click():
    """Record that the user clicked verification advice"""

def update_details_viewed():
    """Record that the user viewed details"""

def calculate_admin_metrics(log: list) -> dict:
    """
    Compute the three Admin Dashboard metrics (reuse logic from Step 4.11):
    - total_queries
    - trust_health (verification click rate)
    - low_conf_rate (low-confidence trigger rate)
    - top_jargon (top 5 high-frequency jargon terms)
    - recent_queries (most recent 10 entries)
    """
```

> **Estimated file length**: ~80 lines

---

## 5.3 Dependency List (requirements.txt)

```
streamlit==1.45.0
openai==1.35.0
pydantic==2.7.0
python-dotenv==1.0.1
```

### Dependency Notes

| Package | Version | Purpose | Why chosen |
|----|------|------|-----------|
| streamlit | ≥1.45.0 | Web UI framework | Pure Python, no HTML/CSS/JS needed; st.expander / st.metric / st.columns natively supported |
| openai | ≥1.35.0 | LLM API calls | Supports structured output / json_object mode |
| pydantic | ≥2.7.0 | JSON Schema validation | Native Python data validation, naturally pairs with OpenAI structured output |
| python-dotenv | ≥1.0.0 | Environment variable management | Loads API key from .env file |

### Packages Not Needed (excluded at prototype stage)

| Excluded | Reason |
|--------|------|
| langchain / llama-index | Prototype uses mock_rag_retrieve to simulate retrieval; no full RAG framework needed |
| chromadb / faiss | No vector database needed; keyword matching is used to simulate |
| fastapi / flask | Streamlit ships its own web server |
| pandas | Admin Dashboard data volume is small; native list/dict suffices |
| pytest | Testing planned separately in Step 8 |

---

## 5.4 Environment Configuration

### `.env.example` (in version control)

```bash
# OpenAI API configuration
OPENAI_API_KEY=sk-your-api-key-here

# Model selection (gpt-4o-mini recommended, low cost)
LLM_MODEL=gpt-4o-mini

# Timeout setting (seconds)
LLM_TIMEOUT=3.0

# Bulletproof Demo Mode: true=offline static response (for recordings/demos) / false=real API call
MOCK_LLM_MODE=true
```

### `.env` (not in version control)

```
OPENAI_API_KEY=sk-your-real-key-here
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT=3.0
MOCK_LLM_MODE=true
```

### `.gitignore`

```
.env
__pycache__/
*.pyc
.streamlit/
```

### `README.md` (minimal)

```markdown
# AI Trust Layer

A prototype trust interface layer for enterprise RAG systems.

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`
3. Set `MOCK_LLM_MODE=true` for offline demo (no API key needed)
4. Run: `streamlit run app.py`
5. Open browser: http://localhost:8501

## Project Structure

See PRD Step 5 for full architecture documentation.
```

---

## 5.5 Development Milestones (Phased Coding Plan)

### Milestone Overview

```
Phase A: Infrastructure (Day 1)     → Runnable empty shell
Phase B: Data layer (Day 2)         → Mock data loads and retrieves
Phase C: API layer (Day 3)          → LLM callable, JSON validates
Phase D: Front-end UI (Day 4–5)     → Li Ming's perspective fully usable
Phase E: Admin dashboard (Day 6)    → Wang Fang's perspective fully usable
Phase F: Integration & polish (Day 7) → End-to-end pass, edge-case handling
```

> **Estimation premise**: a Python beginner, investing 3–4 hours per day. Each Phase ends with a "verification checkpoint" — it must pass before proceeding to the next stage.

---

### Phase A: Infrastructure (Day 1)

**Goal**: Streamlit empty shell runs, session_state initialization complete

| Task | File | Verification point |
|------|------|--------|
| Create project directory structure | All | `ls` to confirm structure |
| Install dependencies | requirements.txt | `pip install -r requirements.txt` succeeds |
| Configure .env | .env | `python -c "from config import OPENAI_API_KEY; print(OPENAI_API_KEY)"` |
| Write app.py skeleton | app.py | `streamlit run app.py` opens a blank page |
| Initialize session_state | app.py | No page errors; session_state variables exist |
| Write config.py | config.py | Config items importable by other modules |

**Phase A acceptance**: `streamlit run app.py` opens the browser, displays the title "AI Trust Layer", no errors.

---

### Phase B: Data Layer + Bulletproof Demo Mode (Day 2)

**Goal**: Mock documents load, simulated RAG retrieval returns results, **Mock LLM mode returns pre-written responses**

| Task | File | Verification point |
|------|------|--------|
| Write 5 mock documents | mock_documents/*.md | `load_mock_documents()` returns 5 documents |
| Implement load_mock_documents() | mock_docs.py | Print document list, confirm metadata parsed correctly |
| Implement mock_rag_retrieve() | mock_docs.py | Searching "point machine" returns documents containing that keyword |
| Implement get_document_page() | mock_docs.py | Pass document name + page number, return page content |
| Write models.py (Pydantic models) | models.py | `TrustLayerResponse(**test_json)` validates |
| **Implement MOCK_RESPONSES static data** | **llm_api.py** | **3 pre-written JSONs pass Pydantic validation** |
| **Implement get_mock_response()** | **llm_api.py** | **Input "signalling standard" → returns high; input "budget" → returns low; input "point machine" → returns medium** |
| **Implement call_llm_api() mock branch** | **llm_api.py** | **With MOCK_LLM_MODE=True, returns TrustLayerResponse with 0 latency** |

**Phase B acceptance**: Add a temporary test snippet in app.py:
1. Search "XX project equipment" and print retrieval results, confirm it returns a list of Source objects
2. Call `call_llm_api("What standard does the signalling system adopt")`, confirm it returns a high-confidence response (0 latency)
3. Call `call_llm_api("What is the project cost budget")`, confirm it returns a low-confidence response + alert data
4. Call `call_llm_api("random unrelated query")`, confirm it returns the `nomatch` response (`sources=[]`) and the UI shows the "No relevant documents" status banner

> **Key strategy**: The Mock mode is implemented in Phase B; during Phase D front-end development you can test directly against mock mode — no need to wait for the API to work, and no API quota consumed. The real API integration of Phase C can be deferred or skipped.

---

### Phase C: API Layer (Day 3) — Warning: Optional (Mock mode )

**Goal**: OpenAI API callable, returns JSON conforming to the data contract

> **Note**: If time is tight, Phase C can be skipped or deferred. The Phase B Mock mode already supports all of Phase D–F development. Phase C is executed only when real API integration needs verification.

| Task | File | Verification point |
|------|------|--------|
| Implement SYSTEM_PROMPT | llm_api.py | Prompt content consistent with Step 4.7 |
| Implement build_user_prompt() | llm_api.py | Print prompt, confirm document fragments and query are assembled correctly |
| Implement call_llm_api() | llm_api.py | Input query, returns TrustLayerResponse object |
| Implement validate_response() | models.py | Valid JSON in → passes; missing-field JSON in → degrades |
| Implement create_fallback_response() | models.py | Degraded response confidence_level == "low" |
| Test timeout handling | llm_api.py | LLM_TIMEOUT=0.1 triggers degradation |

**Phase C acceptance**: In app.py, input "What equipment does the XX project need?"; the LLM returns complete JSON, Pydantic validation passes, print the TrustLayerResponse object.

> **Key risk point**: OpenAI `json_object` mode does not guarantee a perfect schema match. If the JSON field names or types returned by the LLM differ from the Pydantic model, degraded handling is triggered. This is expected behavior, not a Bug.

---

### Phase D: Front-end UI (Day 4–5)

**Goal**: Li Ming's perspective fully usable — from search to viewing details to navigating to documents

#### Day 4: Core Rendering

| Task | File | Verification point |
|------|------|--------|
| Implement render_frontend() | frontend.py | Search box displays; loading animation shows after query input |
| Implement render_confidence_label() | frontend.py | Three-tier label colors correct (green/yellow/red) |
| Implement render_details_expander() | frontend.py | Expander expand/collapse normal, **internal sub-actions do not close the expander** |
| Implement render_sources() | frontend.py | Source list sorted descending by match_score, excerpts expandable |
| Verify Bug 1 fix | frontend.py | Clicking "view excerpt" inside the details area keeps the details expander open |

#### Day 5: Supplementary Features + Edge-case Handling

| Task | File | Verification point |
|------|------|--------|
| Implement render_alert_banner() | frontend.py | Low confidence shows alert banner above the answer, not closable |
| Implement render_jargon_glossary() | frontend.py | Jargon plain-language shown by default, formal definition expandable on demand |
| Verify Bug 2 fix | frontend.py | Medium confidence: source expander expanded + jargon expander collapsed |
| Implement render_verification_advice() | frontend.py | needs_verification controls show/hide |
| Implement render_document_view() | frontend.py | Clicking action link navigates to document page |
| Implement interaction_log basic functions | interaction_log.py | Log entries can be created and stored |

**Phase D acceptance**:
1. Search a high-confidence query → green label, details collapsed by default, sources/jargon/verification advice render correctly after expansion
2. Search a medium-confidence query → yellow label, source expander auto-expands, jargon expander collapsed
3. Search a low-confidence query → red label + alert banner + action link navigation works
4. Operating inside the details area (expanding excerpt, viewing jargon definition) does not dismiss the details expander

---

### Phase E: Admin Dashboard (Day 6)

**Goal**: Wang Fang's perspective fully usable — three metrics + high-frequency jargon + query records

| Task | File | Verification point |
|------|------|--------|
| Implement calculate_admin_metrics() | interaction_log.py | Input log list, return correct metric dict |
| Implement render_admin() | admin.py | Switch to back-end, display three metric cards |
| Implement render_metric_cards() | admin.py | Trust health / low-confidence trigger rate / total query count correct |
| Implement render_top_jargon() | admin.py | High-frequency jargon Top 5 sorted correctly |
| Implement render_recent_queries() | admin.py | Most recent 10 query records display correctly |
| Front/back switching | app.py | Switch button works, data persists across switches |

**Phase E acceptance**: Perform 5 queries on the front-end (including 1 low-confidence, 2 jargon views, 1 verification click), switch to back-end, the three metric values are correct, and high-frequency jargon is recorded.

---

### Phase F: Integration & Polish (Day 7)

**Goal**: End-to-end pass, edge-case handling, code cleanup

| Task | Description |
|------|------|
| End-to-end test | From search → answer → details → jargon → verification → document navigation → back-end dashboard, no errors across the full flow |
| Empty-data test | Degraded display when sources is empty, jargon_glossary is empty, or verification_advice is missing |
| Timeout test | Simulate LLM timeout, confirm degraded prompt displays correctly |
| Code cleanup | Remove debug prints, unify comment style, confirm .gitignore is effective |
| Screenshot recording | Record 3 scenario screenshots (high/medium/low confidence) + 1 back-end dashboard screenshot |
| README update | Supplement run instructions and project overview |

**Phase F acceptance**: A person with zero project knowledge can read the README + run `streamlit run app.py` and understand the product and complete a query within 10 minutes.

---

## 5.6 Data Flow Sequence Diagram (Option A + Bulletproof Demo Mode)

```
User enters query
    │
    ▼
┌─ app.py ─────────────────────────────────┐
│  st.session_state["view_mode"] == "front" │
│  → call frontend.render_frontend()        │
└──────────────┬───────────────────────────┘
               │
               ▼
┌─ frontend.py ────────────────────────────┐
│  st.spinner("Retrieving documents and generating answer...")   │
│  → call llm_api.call_llm_api(query)      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌─ llm_api.py ─────────────────────────────┐
│                                          │
│  ┌─ MOCK_LLM_MODE == True ? ───────────┐ │
│  │                                      │ │
│  │  YES (Bulletproof Demo Mode)          │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │ get_mock_response(query)        │ │ │
│  │  │  ├ Keyword match → scenario     │ │ │
│  │  │  │   (high/medium/low/nomatch)  │ │ │
│  │  │  ├ Take MOCK_RESPONSES[scenario]│ │ │
│  │  │  ├ Update timestamp + query_id  │ │ │
│  │  │  ├ Pydantic validation          │ │ │
│  │  │  └ → TrustLayerResponse (0ms)   │ │ │
│  │  └──────────────┬──────────────────┘ │ │
│  │                 │                     │ │
│  │  NO (Real API mode)                   │ │
│  │  ┌──────────────┴──────────────────┐ │ │
│  │  │ 1. mock_rag_retrieve(query)     │ │ │
│  │  │    → list[Source] (≤3 items)   │ │ │
│  │  │ 2. build_user_prompt(docs,q)    │ │ │
│  │  │ 3. openai.chat.completions      │ │ │
│  │  │    .create(json_object, 3s)     │ │ │
│  │  │    → full JSON (single call)    │ │ │
│  │  │ 4. validate_response(raw_json)  │ │ │
│  │  │    → pass: Response object      │ │ │
│  │  │    → fail: fallback_response()  │ │ │
│  │  └──────────────┬──────────────────┘ │ │
│  └─────────────────┼────────────────────┘ │
└────────────────────┼──────────────────────┘
                     │ TrustLayerResponse
                     ▼
┌─ frontend.py ────────────────────────────┐
│  render_response(response):              │
│                                          │
│  if response.sources is empty:           │
│     → render_no_docs_banner()            │
│     → return                             │
│                                          │
│  ① render_confidence_label(level)        │
│     high  → st.success("High Confidence")│
│     medium → st.warning("Partial Match") │
│     low   → st.error("Low Confidence")   │
│                                          │
│  ② if level == "low":                    │
│       render_alert_banner(verif_advice)  │
│                                          │
│  ③ st.markdown(response.answer.text)     │
│                                          │
│  ④ with st.expander("Details",           │
│       expanded=(level=="medium")):       │
│       │                                  │
│       ├─ render_sources(sources)         │
│       │                                  │
│       ├─ with st.expander("Jargon",      │
│       │    expanded=False):              │
│       │    └─ render_jargon_glossary()   │
│       │                                  │
│       └─ render_verification_advice()    │
│                                          │
│  ⑤ interaction_log.log_interaction()     │
└──────────────────────────────────────────┘
```

> **In Mock mode `st.spinner` flashes by instantly** — because `get_mock_response()` executes in <1ms, the spinner disappears as soon as it appears. This is expected behavior and needs no special handling. If the flash looks unappealing, you can add `time.sleep(0.3)` in mock mode to simulate a "thinking" feel.

---

## 5.7 Streamlit Session State Architecture

```python
# st.session_state complete variable list

st.session_state = {
    # --- Routing control ---
    "view_mode": "front",          # "front" | "admin"
    "doc_view": None,              # {"doc_name": str, "page": int} | None
    
    # --- Current response ---
    "current_response": None,      # TrustLayerResponse | None
    
    # --- Interaction log ---
    "interaction_log": [],         # list[InteractionLogEntry]
    "jargon_views": {},            # {term: count}
    "verification_clicks": 0,      # int
    "details_viewed": False,       # bool (whether current query has viewed details)
    
    # --- Query count ---
    "query_count": 0,              # int (total query count)
}
```

### Session State Lifecycle

| Variable | Init timing | Update timing | Clear timing |
|------|-----------|---------|---------|
| view_mode | app.py init | Click switch button | Not cleared (persistent) |
| current_response | User submits query | After API returns | Overwritten on new query |
| interaction_log | app.py init | Appended after each query | Not cleared (persistent within session) |
| jargon_views | app.py init | Updated when user views jargon | Not cleared (persistent within session) |
| verification_clicks | app.py init | +1 when user clicks verify | Not cleared (persistent within session) |
| details_viewed | User submits query | True when user expands details | Reset to False on new query |

> **Important**: Streamlit's session_state is cleared when the user refreshes the browser. At the prototype stage this is expected behavior — data is not persisted.

---

## 5.8 Key Implementation Risks and Mitigations

| Risk                                                                                                                             | Probability | Impact    | Mitigation strategy                                                                                                                                                                                       |
| -------------------------------------------------------------------------------------------------------------------------------- | ----------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OpenAI `json_object` mode returns JSON not matching the Pydantic schema                                                          | Medium      | High      | `validate_response()` + `create_fallback_response()` degradation already built in                                                                                                                         |
| LLM response time > 3s                                                                                                           | Low         | Medium    | `timeout=3.0` parameter + timeout degradation response                                                                                                                                                    |
| **interview demo suddenly loses API access**                                                                                     | **Medium**  | **Fatal** | **Solved: `MOCK_LLM_MODE = True` skips the API, returns pre-written static JSON, 0 latency, 100% controllable**                                                                                           |
| **On-site interview loses network**                                                                                              | **Low**     | **Fatal** | **Solved: Mock mode needs no network; runs locally on localhost**                                                                                                                                         |
| Mock document keyword match scores unreasonable (all 0 or all 1)                                                                 | Medium      | Low       | Add normalization logic + minimum match threshold 0.1 in `mock_rag_retrieve()`                                                                                                                            |
| Streamlit rerun causes session_state loss                                                                                        | Low         | High      | session_state is Streamlit's officially recommended persistence method, auto-preserved across reruns                                                                                                      |
| Medium-confidence expander auto-expands, then user manually collapses it, and state isn't refreshed when querying a new question | Medium      | Low       | Each new query overwrites `current_response`; the expander's `expanded` param is recomputed from the new response                                                                                         |
| No-Match Fallback: mock keyword miss                                                                                             | Low         | Medium    | Return the `nomatch` static response (`sources=[]`); frontend renders an amber "No relevant documents found — please verify your query" status banner, guiding the user to rephrase with project keywords |

---

## 5.9 Traceability Matrix to Step 4 Specifications

| Step 4 Spec item                             | Step 5 Implementation location                                                  | Status      |
| -------------------------------------------- | ------------------------------------------------------------------------------- | ----------- |
| 4.1 UI state machine                         | app.py (view_mode routing) + frontend.py (render_response)                      | Planned     |
| 4.2 F1 Source attribution                    | frontend.py → render_sources()                                                  | Planned     |
| 4.3 F2 Confidence + alert                    | frontend.py → render_confidence_label() + render_alert_banner()                 | Planned     |
| 4.3 Bug 2 fix (dual expander)                | frontend.py → render_details_expander()                                         | Planned     |
| 4.4 F3 Jargon explanation                    | frontend.py → render_jargon_glossary()                                          | Planned     |
| 4.5 F4 Verification advice                   | frontend.py → render_verification_advice()                                      | Planned     |
| 4.6 F7 Admin Dashboard                       | admin.py → render_admin() + three sub-functions                                 | Planned     |
| 4.7 DC data contract                         | models.py (Pydantic models + validation + degradation)                          | Planned     |
| 4.8 N1 Latency control (Option A)            | llm_api.py → call_llm_api() (single request)                                    | Planned     |
| 4.8 Bug 1 fix (st.expander)                  | frontend.py → render_details_expander()                                         | Planned     |
| 4.9 N2 JSON validation                       | models.py → validate_response() + Pydantic Field constraints                    | Planned     |
| 4.10 Mock document set                       | mock_docs.py + mock_documents/*.md                                              | Planned     |
| 4.11 Interaction log                         | interaction_log.py (InteractionLogEntry + metric calculation)                   | Planned     |
| 4.12 Feature-Component-Data master table     | All modules mapped                                                              | Planned     |
| **Bulletproof Demo Mode (driven by Step 6)** | **config.py (MOCK_LLM_MODE) + llm_api.py (get_mock_response + MOCK_RESPONSES)** | **Planned** |
