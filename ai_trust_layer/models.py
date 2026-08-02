"""
models.py - Pydantic data contract models (Data Contract)

Responsibility: define TrustLayerResponse and all sub-models, validation logic, and fallback handling
Maps to PRD: Step 4.7 DC data contract implementation spec
"""

from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from enum import Enum
from datetime import datetime


# ── Enums ──────────────────────────────────────────────────────────

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ── Sub-models ─────────────────────────────────────────────────────

class Answer(BaseModel):
    text: str = Field(..., max_length=2000, description="AI-generated answer text")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level")
    is_inferred: bool = Field(..., description="Whether this is an AI inference")


class Source(BaseModel):
    document_name: str = Field(..., description="Document name")
    page_number: int = Field(..., ge=0, description="Page number")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Retrieval match score")
    excerpt: Optional[str] = Field(None, description="Original excerpt")


class JargonTerm(BaseModel):
    term: str = Field(..., description="Technical term")
    definition: str = Field(..., description="Formal definition")
    plain_language: str = Field(..., description="Plain-language explanation")


class ActionLink(BaseModel):
    text: str = Field(..., description="Link display text")
    document: str = Field(..., description="Target document name")
    page: int = Field(..., ge=0, description="Target page number")


class VerificationAdvice(BaseModel):
    needs_verification: bool = Field(..., description="Whether manual verification is needed")
    fields_to_check: List[str] = Field(default=[], description="Specific fields to verify")
    action_link: Optional[ActionLink] = Field(None, description="Action suggestion link")


class QueryMetadata(BaseModel):
    query_id: str = Field(..., description="Unique query ID")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    response_time_ms: int = Field(..., ge=0, description="Response time (ms)")
    model_used: str = Field(..., description="Model name used")
    documents_searched: int = Field(..., ge=0, description="Total number of documents searched")
    documents_matched: int = Field(..., ge=0, description="Number of matched documents")


# ── Top-level model ────────────────────────────────────────────────

class TrustLayerResponse(BaseModel):
    """The complete data contract of the AI Trust Layer"""
    answer: Answer
    sources: List[Source] = Field(default=[], max_length=5)
    jargon_glossary: List[JargonTerm] = Field(default=[], max_length=10)
    verification_advice: Optional[VerificationAdvice] = None
    metadata: QueryMetadata


# ── Validation logic ───────────────────────────────────────────────

def validate_response(raw_json: dict) -> TrustLayerResponse | None:
    """
    Validate whether the JSON returned by the LLM conforms to the data contract.
    Pass -> return a TrustLayerResponse object
    Fail -> return None (the caller should use create_fallback_response)
    """
    try:
        response = TrustLayerResponse(**raw_json)
        return response
    except (ValidationError, TypeError) as e:
        print(f"[models] Validation error: {e}")
        return None


def create_fallback_response(raw_json: dict | None = None) -> TrustLayerResponse:
    """
    Fallback handling: when JSON validation fails, construct a minimally usable response.
    Preserve fields that can be parsed; fill missing fields with default values.
    """
    raw = raw_json or {}
    answer_data = raw.get("answer", {})

    return TrustLayerResponse(
        answer=Answer(
            text=answer_data.get("text", "Sorry, the response could not be parsed. Please try asking again."),
            confidence_score=answer_data.get("confidence_score", 0.0),
            confidence_level=ConfidenceLevel.LOW,
            is_inferred=True,
        ),
        sources=[],
        jargon_glossary=[],
        verification_advice=VerificationAdvice(
            needs_verification=True,
            fields_to_check=["Response parsing error - all content should be manually verified"],
            action_link=None,
        ),
        metadata=QueryMetadata(
            query_id="fallback",
            timestamp=datetime.now().isoformat(),
            response_time_ms=0,
            model_used="fallback",
            documents_searched=0,
            documents_matched=0,
        ),
    )


def determine_confidence_level(score: float) -> ConfidenceLevel:
    """
    Compute the confidence level from the confidence score (fallback logic, used when the LLM does not return a level).
    """
    if score >= 0.75:
        return ConfidenceLevel.HIGH
    elif score >= 0.50:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW
