"""
models.py - Pydantic 数据契约模型（Data Contract）

职责：定义 TrustLayerResponse 及所有子模型、验证逻辑、降级处理
对应 PRD：Step 4.7 DC 数据契约实现规格
"""

from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from enum import Enum
from datetime import datetime


# ── 枚举 ──────────────────────────────────────────────────

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ── 子模型 ────────────────────────────────────────────────

class Answer(BaseModel):
    text: str = Field(..., max_length=2000, description="AI生成的回答文本")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="置信度分数")
    confidence_level: ConfidenceLevel = Field(..., description="置信度档位")
    is_inferred: bool = Field(..., description="是否为AI推断")


class Source(BaseModel):
    document_name: str = Field(..., description="文档名称")
    page_number: int = Field(..., ge=0, description="页码")
    match_score: float = Field(..., ge=0.0, le=1.0, description="检索匹配分数")
    excerpt: Optional[str] = Field(None, description="原文摘录")


class JargonTerm(BaseModel):
    term: str = Field(..., description="技术术语")
    definition: str = Field(..., description="正式定义")
    plain_language: str = Field(..., description="大白话解释")


class ActionLink(BaseModel):
    text: str = Field(..., description="链接显示文字")
    document: str = Field(..., description="目标文档名")
    page: int = Field(..., ge=0, description="目标页码")


class VerificationAdvice(BaseModel):
    needs_verification: bool = Field(..., description="是否需要人工核实")
    fields_to_check: List[str] = Field(default=[], description="需核实的具体字段")
    action_link: Optional[ActionLink] = Field(None, description="行动建议链接")


class QueryMetadata(BaseModel):
    query_id: str = Field(..., description="查询唯一ID")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    response_time_ms: int = Field(..., ge=0, description="响应时间(毫秒)")
    model_used: str = Field(..., description="使用的模型名称")
    documents_searched: int = Field(..., ge=0, description="检索的文档总数")
    documents_matched: int = Field(..., ge=0, description="匹配的文档数")


# ── 顶层模型 ──────────────────────────────────────────────

class TrustLayerResponse(BaseModel):
    """AI Trust Layer 的完整数据契约"""
    answer: Answer
    sources: List[Source] = Field(default=[], max_length=5)
    jargon_glossary: List[JargonTerm] = Field(default=[], max_length=10)
    verification_advice: Optional[VerificationAdvice] = None
    metadata: QueryMetadata


# ── 验证逻辑 ──────────────────────────────────────────────

def validate_response(raw_json: dict) -> TrustLayerResponse | None:
    """
    验证 LLM 返回的 JSON 是否符合数据契约。
    通过 -> 返回 TrustLayerResponse 对象
    不通过 -> 返回 None（调用方应使用 create_fallback_response）
    """
    try:
        response = TrustLayerResponse(**raw_json)
        return response
    except (ValidationError, TypeError) as e:
        print(f"[models] Validation error: {e}")
        return None


def create_fallback_response(raw_json: dict | None = None) -> TrustLayerResponse:
    """
    降级处理：当 JSON 验证失败时，构造最小可用响应。
    保留能解析的字段，缺失字段用默认值填充。
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
    根据置信度分数计算档位（兜底逻辑，当 LLM 未返回 level 时使用）。
    """
    if score >= 0.75:
        return ConfidenceLevel.HIGH
    elif score >= 0.50:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW
