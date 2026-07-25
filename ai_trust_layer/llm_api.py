"""
llm_api.py - LLM API Layer (with bulletproof demo mode)

Responsibilities: Call OpenAI API, construct prompts, handle timeouts/exceptions, mock mode dispatch
Corresponds to: PRD Step 4.7 LLM Prompt + Step 4.8 N1 Plan A + Step 5.2.5
"""

import json
import time
import uuid
from datetime import datetime
from models import TrustLayerResponse, validate_response, create_fallback_response
from mock_docs import mock_rag_retrieve
from config import OPENAI_API_KEY, LLM_MODEL, LLM_TIMEOUT, MOCK_LLM_MODE


# -- System Prompt (Step 4.7) ----------------------------------

SYSTEM_PROMPT: str = """You are a response generator for an enterprise RAG system. Answer the user's question based on the following retrieved document excerpts.
You must return your answer in JSON format, strictly following this structure:

{
  "answer": {
    "text": "Answer text (max 2000 characters)",
    "confidence_score": 0.0-1.0,
    "confidence_level": "high" | "medium" | "low",
    "is_inferred": true/false
  },
  "sources": [
    {"document_name": "...", "page_number": 0, "match_score": 0.0-1.0, "excerpt": "..."}
  ],
  "jargon_glossary": [
    {"term": "...", "definition": "...", "plain_language": "..."}
  ],
  "verification_advice": {
    "needs_verification": true/false,
    "fields_to_check": ["..."],
    "action_link": {"text": "...", "document": "...", "page": 0}
  }
}

Confidence level rules:
- high (>=0.75): Answer is directly from document references, no inference needed
- medium (0.50-0.74): Answer is partially from documents, partially inferred
- low (<0.50): No direct match found in documents, answer is mainly inferred

plain_language must use everyday language that non-technical users can understand instantly."""


# -- Bulletproof Demo Mode: Pre-written Static Responses ----------
# 3 perfect JSONs, precisely matching Step 6 Demo Script Scene 2/3/4
# Each strictly conforms to the Step 4.7 Pydantic Schema, returns in 0ms

MOCK_RESPONSES: dict[str, dict] = {
    # Scene 2: High confidence (green label, details collapsed, no alert)
    "high": {
        "answer": {
            "text": "Project XX uses a CBTC (Communication-Based Train Control) system. This system achieves real-time train positioning and moving block control through train-to-ground communication, increasing line capacity by approximately 15-20% compared to traditional fixed block systems.",
            "confidence_score": 0.92,
            "confidence_level": "high",
            "is_inferred": False
        },
        "sources": [
            {"document_name": "proj_XX_tech_spec_v3.2.md", "page_number": 15, "match_score": 0.95, "excerpt": "The signaling system adopts CBTC technology. Core equipment includes ZDJ-200 electric switch machines, signals, and track circuits..."},
            {"document_name": "proj_XX_signal_design.md", "page_number": 3, "match_score": 0.88, "excerpt": "The signaling system design is based on CBTC technology, implementing moving block control..."}
        ],
        "jargon_glossary": [
            {"term": "CBTC", "definition": "Communication-Based Train Control - a train control system that uses wireless communication between trains and trackside equipment for real-time positioning", "plain_language": "It uses radio to let trains and ground equipment talk in real-time, always knowing where each train is and how fast it's going"},
            {"term": "Moving Block", "definition": "A signaling concept where the safe distance between trains is dynamically calculated based on real-time speed, rather than using fixed track sections", "plain_language": "The safe distance between trains isn't fixed - it's calculated on the fly based on current speed. Fast = spread out, stopped = close together"}
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

    # Scene 3: Low confidence (red alert banner, not dismissible, action link)
    "low": {
        "answer": {
            "text": "Based on available documents, specific cost budget information for the YY Line project was not found in the current database. The following is inferred from similar project experience and is for reference only: For rail transit low-voltage integration projects, the overall cost typically accounts for 8-12% of the total line investment, with the signaling system accounting for approximately 35-40% of the low-voltage portion.",
            "confidence_score": 0.28,
            "confidence_level": "low",
            "is_inferred": True
        },
        "sources": [
            {"document_name": "pricing_guide_2024.md", "page_number": 22, "match_score": 0.31, "excerpt": "Reference cost ranges for various line projects... (does not include specific data for YY Line)"}
        ],
        "jargon_glossary": [
            {"term": "Low-Voltage Integration", "definition": "An engineering approach that unifies the design, construction, and management of low-voltage subsystems including communications, signaling, security, and broadcasting", "plain_language": "It's when you hand all the low-power stuff on a platform - communications, cameras, PA systems - to one team to do together, instead of splitting it up"}
        ],
        "verification_advice": {
            "needs_verification": True,
            "fields_to_check": ["Specific cost amounts", "Budget approval document number", "Funding source"],
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

    # Scene 4: Medium confidence (yellow label, sources expander open, jargon expander closed)
    "medium": {
        "answer": {
            "text": "Main technical parameters of the ZDJ-200 electric switch machine: rated voltage DC160V, rated current <=4.5A, switching force 5880N, operating time <=6 seconds, suitable for 50kg/m and 60kg/m rails. Some parameters are from the equipment manual and some are inferred from similar equipment. Please verify against the original specification.",
            "confidence_score": 0.62,
            "confidence_level": "medium",
            "is_inferred": True
        },
        "sources": [
            {"document_name": "zdj200_manual.md", "page_number": 8, "match_score": 0.71, "excerpt": "ZDJ-200 electric switch machine technical parameters: rated voltage DC160V, switching force 5880N..."},
            {"document_name": "equipment_catalog_2024.md", "page_number": 12, "match_score": 0.58, "excerpt": "Switch machine selection reference table (includes ZDJ-200 parameter comparison)..."}
        ],
        "jargon_glossary": [
            {"term": "Electric Switch Machine", "definition": "An electric device used to move and lock railway turnouts (switches) to the desired position", "plain_language": "It's the electric motor that controls which way a track junction splits"},
            {"term": "Switching Force", "definition": "The force output by the switch machine when moving the turnout, measured in Newtons (N)", "plain_language": "How hard this motor can push to move the rail tracks"},
            {"term": "Operating Time", "definition": "The time required for the switch machine to complete the turnout movement and locking", "plain_language": "How many seconds it takes to switch the track from one direction to the other"}
        ],
        "verification_advice": {
            "needs_verification": True,
            "fields_to_check": ["Rated current value", "Applicable rail types"],
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
            "text": "I couldn't find any documents relevant to your question in the current database. Try rephrasing with project-specific keywords (e.g. signaling system, switch machine, construction budget).",
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

# Query keywords -> mock scenario mapping
MOCK_QUERY_MAP: list[tuple[list[str], str]] = [
    (["budget", "cost", "price", "investment", "报价"], "low"),        # Scene 3
    (["switch", "machine", "ZDJ", "parameter", "specification", "转辙"], "medium"),  # Scene 4
    (["signal", "signaling", "CBTC", "system", "equipment", "信号"], "high"),    # Scene 2 (default)
]


def get_mock_response(user_query: str) -> TrustLayerResponse:
    """
    Bulletproof demo mode: Match pre-written static responses based on query keywords.

    Matching logic:
    1. Iterate MOCK_QUERY_MAP, first keyword group hit wins
    2. No match -> "nomatch" scenario (empty sources -> frontend shows no-docs banner)

    Returns: Pydantic-validated TrustLayerResponse object
    """
    matched_scenario = "nomatch"  # default: no keyword match => no relevant documents

    for keywords, scenario in MOCK_QUERY_MAP:
        if any(kw in user_query for kw in keywords):
            matched_scenario = scenario
            break

    # Deep copy to avoid mutating original data
    raw_json = json.loads(json.dumps(MOCK_RESPONSES[matched_scenario]))

    # Update timestamp and query_id to make logs look realistic
    raw_json["metadata"]["timestamp"] = datetime.now().isoformat()
    raw_json["metadata"]["query_id"] = f"mock-{matched_scenario}-{int(time.time())}"

    response = validate_response(raw_json)
    if response is None:
        # Pre-written data should never fail validation, but as a safety net:
        response = create_fallback_response(raw_json)

    return response


def call_llm_api(user_query: str) -> TrustLayerResponse:
    """
    Full API call flow (Plan A: single request, full response).

    Bulletproof demo mode checked first:
    if MOCK_LLM_MODE == True:
        -> Skip OpenAI, return get_mock_response(user_query)
        -> 0 latency, 100% controllable, no API cost

    Normal flow (MOCK_LLM_MODE == False):
    1. Call mock_rag_retrieve to get relevant document excerpts
    2. Construct user prompt (document excerpts + user query)
    3. Call OpenAI API (json_object mode)
    4. Pydantic validation
    5. Return TrustLayerResponse object
    """

    # -- Bulletproof demo mode: return pre-written response in 0ms --
    if MOCK_LLM_MODE:
        return get_mock_response(user_query)

    # -- Normal mode: real OpenAI API call --
    start_time = time.time()
    try:
        retrieved_docs = mock_rag_retrieve(user_query)
        user_prompt = build_user_prompt(retrieved_docs, user_query)

        from openai import OpenAI
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
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Update metadata
        raw_json.setdefault("metadata", {})
        raw_json["metadata"]["response_time_ms"] = elapsed_ms
        raw_json["metadata"]["query_id"] = generate_query_id()
        raw_json["metadata"]["timestamp"] = datetime.now().isoformat()
        raw_json["metadata"]["model_used"] = LLM_MODEL

        trust_response = validate_response(raw_json)
        if trust_response is None:
            trust_response = create_fallback_response(raw_json)

        return trust_response

    except Exception as e:
        print(f"[llm_api] Error: {e}")
        return create_fallback_response({})


def build_user_prompt(retrieved_docs: list, user_query: str) -> str:
    """Construct User Prompt: retrieved document excerpts + user question"""
    docs_text = ""
    for i, doc in enumerate(retrieved_docs, 1):
        docs_text += f"\n--- Document {i}: {doc.document_name} (page {doc.page_number}, match score {doc.match_score:.0%}) ---\n"
        if doc.excerpt:
            docs_text += doc.excerpt + "\n"

    return f"Retrieved document excerpts:\n{docs_text}\n\nUser question: {user_query}"


def generate_query_id() -> str:
    """Generate unique query ID (timestamp + random)"""
    return f"q-{int(time.time())}-{uuid.uuid4().hex[:6]}"


def calculate_response_time(start_time: float) -> int:
    """Calculate response time in milliseconds"""
    return int((time.time() - start_time) * 1000)
