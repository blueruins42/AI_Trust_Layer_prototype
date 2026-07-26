# PRD Step 5: Technical Architecture & Implementation Plan

> Product working name: AI Trust Layer
> Stage: Full Product Design Process - Step 5
> Date: 2026-07-24
> Upstream inputs: All confirmed deliverables from Step 1–4
> This step delivers: project directory structure, module breakdown, dependency list, environment configuration, development milestones, and core function signatures

---

## 5.0 Architecture Decision Lock-in

### N1 Latency Control: Option A (single-request full response) — Confirmed

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
    初始化所有 session_state 变量：
    - view_mode: "front" | "admin"
    - interaction_log: list[dict]
    - current_response: TrustLayerResponse | None
    - jargon_views: dict[str, int]  # 术语查看计数
    - verification_clicks: int       # 核实点击计数
    """

def main():
    """
    主函数：
    1. st.set_page_config(title, icon, layout)
    2. init_session_state()
    3. 根据 st.session_state["view_mode"] 渲染前台或后台
    4. 提供切换按钮
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

# LLM API 配置
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "3.0"))  # 秒

# ── 防弹演示模式（Bulletproof Demo Mode）──────────────────
# True  → llm_api.py 跳过 OpenAI 调用，直接返回预写静态 JSON（0 延迟、100% 可控）
# False → 正常调用 OpenAI API
#
# 使用场景：
#   - 录制 Demo 视频 / 面试 Live 演示 → 设为 True
#   - 开发调试前台界面 → 设为 True（不消耗 API 额度）
#   - 验证 API 集成 / 测试真实置信度 → 设为 False
#
# 切换方式：修改 .env 中的 MOCK_LLM_MODE 值，或直接改此处默认值
MOCK_LLM_MODE: bool = os.getenv("MOCK_LLM_MODE", "true").lower() == "true"
# ──────────────────────────────────────────────────────────

# 置信度阈值
CONFIDENCE_HIGH_THRESHOLD: float = 0.75
CONFIDENCE_LOW_THRESHOLD: float = 0.50

# 数据契约约束
MAX_SOURCES: int = 5
MAX_JARGON_TERMS: int = 10
MAX_ANSWER_LENGTH: int = 2000

# Mock 文档路径
MOCK_DOCS_DIR: str = os.path.join(os.path.dirname(__file__), "mock_documents")
```

#### `.env.example` update (MOCK_LLM_MODE added)

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT=3.0

# 防弹演示模式：true=离线静态响应(录屏/演示用) / false=真实API调用
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
    """验证 LLM 返回的 JSON，通过返回对象，不通过返回降级响应"""

def create_fallback_response(raw_json: dict) -> TrustLayerResponse:
    """降级处理：构造最小可用响应"""

def determine_confidence_level(score: float) -> ConfidenceLevel:
    """根据置信度分数计算档位（兜底逻辑，当 LLM 未返回 level 时使用）"""
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
    加载 mock_documents/ 目录下所有 .md 文件。
    解析每份文档的元数据（标题、页码标记、章节）。
    返回 [{"name", "content", "pages": [{"page": int, "text": str}]}]
    """

def mock_rag_retrieve(query: str, top_k: int = 3) -> list[Source]:
    """
    模拟 RAG 检索：
    1. 对 query 做简单关键词分词
    2. 遍历所有文档页，计算关键词匹配分数
    3. 按分数降序排列，取前 top_k
    4. 返回 Source 对象列表
    
    匹配分数计算逻辑：
    - 精确匹配关键词：+0.3
    - 部分匹配（子串）：+0.15
    - 文档标题匹配：+0.2
    - 最终归一化到 0.0-1.0
    """

def get_document_page(doc_name: str, page_number: int) -> str | None:
    """
    根据 document_name 和 page_number 获取文档页面内容。
    用于 DOCUMENT_VIEW 状态的跳转。
    """
```

**Example mock document structure** (`proj_XX_tech_spec_v3.2.md`):

```markdown
# XX项目技术规格书

**文档编号**: DOC-001
**版本**: v3.2

---

## 第1页：项目概述

本项目为XX城市轨道交通信号系统弱电集成工程...

> page=1

## 第2页：设备清单

主要设备包括：
- ZDJ-200型电动转辙机 ×24台
- 信号机 ×36架
- 轨道电路 ×48区段

> page=2

## 第15页：技术规格

信号系统采用 CBTC 制式，核心设备...

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

# System Prompt（直接复用 Step 4.7 的模板）
SYSTEM_PROMPT: str = """你是一个企业 RAG 系统的回答生成器...（完整模板见 Step 4.7）"""

# ── 防弹演示模式：预写静态响应 ──────────────────────────────
# 3 份完美 JSON，精确对应 Step 6 Demo Script 的 Scene 2/3/4
# 每份都严格符合 Step 4.7 Pydantic Schema，0 延迟返回

MOCK_RESPONSES: dict[str, dict] = {
    # Scene 2: 高置信度（绿色标签，详情收起，无警报）
    "high": {
        "answer": {
            "text": "XX项目信号系统采用 CBTC（基于通信的列车运行控制）制式。该制式通过车地通信实现列车实时定位和移动闭塞，相比传统固定闭塞制式可提升线路通过能力约 15-20%。",
            "confidence_score": 0.92,
            "confidence_level": "high",
            "is_inferred": False
        },
        "sources": [
            {"document_name": "proj_XX_tech_spec_v3.2.md", "page_number": 15, "match_score": 0.95, "excerpt": "信号系统采用 CBTC 制式，核心设备包括 ZDJ-200 型电动转辙机、信号机及轨道电路..."},
            {"document_name": "proj_XX_signal_design.md", "page_number": 3, "match_score": 0.88, "excerpt": "本项目信号系统设计基于 CBTC 制式，实现移动闭塞控制..."}
        ],
        "jargon_glossary": [
            {"term": "CBTC", "definition": "Communication-Based Train Control，基于通信的列车运行控制系统", "plain_language": "就是用无线电让列车和地面设备实时聊天，随时知道列车在哪、跑多快"},
            {"term": "移动闭塞", "definition": "Moving Block，列车间安全距离根据实时速度动态计算的闭塞方式", "plain_language": "列车之间保持的安全距离不是固定的，而是根据当前速度实时算出来的——跑得快就拉开点，停着就靠拢点"}
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

    # Scene 3: 低置信度（红色警报横幅，不可关闭，行动链接）
    "low": {
        "answer": {
            "text": "根据现有文档，YY线路工程的造价预算信息未在当前数据库中找到明确记录。以下回答基于类似项目经验推断，仅供参考：轨道交通弱电集成工程的整体造价通常占线路总投资的 8-12%，其中信号系统约占弱电部分的 35-40%。",
            "confidence_score": 0.28,
            "confidence_level": "low",
            "is_inferred": True
        },
        "sources": [
            {"document_name": "pricing_guide_2024.md", "page_number": 22, "match_score": 0.31, "excerpt": "各线路工程造价参考区间...（未包含YY线路具体数据）"}
        ],
        "jargon_glossary": [
            {"term": "弱电集成", "definition": "将通信、信号、安防等弱电子系统统一设计、施工和管理的工程模式", "plain_language": "就是 把站台上那些不扛重的东西（通讯、监控、广播）打包给一个团队一起做"}
        ],
        "verification_advice": {
            "needs_verification": True,
            "fields_to_check": ["具体造价金额", "预算批复文件编号", "资金来源"],
            "action_link": {
                "text": "查看原文档第22页",
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

    # Scene 4: 中置信度（黄色标签，来源expander展开，术语expander收起）
    "medium": {
        "answer": {
            "text": "ZDJ-200型电动转辙机的主要技术参数：额定电压 DC160V，额定电流 ≤4.5A，转换力 5880N，动作时间 ≤6秒，适用于 50kg/m 及 60kg/m 钢轨。以上参数部分来自设备手册，部分基于同类设备推断，建议核对原始规格书。",
            "confidence_score": 0.62,
            "confidence_level": "medium",
            "is_inferred": True
        },
        "sources": [
            {"document_name": "zdj200_manual.md", "page_number": 8, "match_score": 0.71, "excerpt": "ZDJ-200型电动转辙机技术参数表：额定电压DC160V，转换力5880N..."},
            {"document_name": "equipment_catalog_2024.md", "page_number": 12, "match_score": 0.58, "excerpt": "转辙机选型参考表（含ZDJ-200参数对照）..."}
        ],
        "jargon_glossary": [
            {"term": "电动转辙机", "definition": "Electric Switch Machine，用于转换和锁闭道岔的电动设备", "plain_language": "就是控制铁轨岔路口往哪边开的电动马达"},
            {"term": "转换力", "definition": "Switch Machine Force，转辙机拉动道岔转换时输出的力，单位牛顿(N)", "plain_language": "就是这个马达有多大力气能扳动铁轨"},
            {"term": "动作时间", "definition": "Operating Time，转辙机从开始转换到完成锁闭的时间", "plain_language": "岔路口从一边切到另一边需要几秒钟"}
        ],
        "verification_advice": {
            "needs_verification": True,
            "fields_to_check": ["额定电流值", "适用钢轨型号"],
            "action_link": {
                "text": "查看ZDJ-200手册第8页",
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
    }
}

# 查询关键词 → mock 场景映射（确保 Demo 脚本中的查询精准触发对应场景）
MOCK_QUERY_MAP: list[tuple[list[str], str]] = [
    (["预算", "造价", "报价", "成本", "投资"], "low"),       # Scene 3
    (["转辙机", "参数", "规格", "技术参数"], "medium"),        # Scene 4
    (["信号", "制式", "CBTC", "设备", "系统"], "high"),       # Scene 2（默认场景）
]


def get_mock_response(user_query: str) -> TrustLayerResponse:
    """
    防弹演示模式：根据查询关键词匹配预写静态响应。
    
    匹配逻辑：
    1. 遍历 MOCK_QUERY_MAP，第一个命中关键词组的场景胜出
    2. 全部未命中 → 默认返回 high 场景
    
    返回：已通过 Pydantic 验证的 TrustLayerResponse 对象
    """
    query_lower = user_query.lower()
    matched_scenario = "high"  # 默认场景

    for keywords, scenario in MOCK_QUERY_MAP:
        if any(kw in user_query for kw in keywords):
            matched_scenario = scenario
            break

    raw_json = MOCK_RESPONSES[matched_scenario]
    
    # 更新 timestamp 为当前时间（让日志看起来真实）
    raw_json["metadata"]["timestamp"] = datetime.now().isoformat()
    raw_json["metadata"]["query_id"] = f"mock-{matched_scenario}-{int(time.time())}"
    
    response = validate_response(raw_json)
    if response is None:
        # 预写数据理论上不会验证失败，但作为防弹保险
        response = create_fallback_response(raw_json)
    
    return response


def call_llm_api(user_query: str) -> TrustLayerResponse:
    """
    完整的 API 调用流程（方案 A：单次请求全量返回）：
    
    ⚠️ 防弹演示模式优先检查：
    if MOCK_LLM_MODE == True:
        → 跳过 OpenAI，直接返回 get_mock_response(user_query)
        → 0 延迟、100% 可控、不消耗 API 额度
    
    正常流程（MOCK_LLM_MODE == False）：
    1. 调用 mock_rag_retrieve 获取相关文档片段
    2. 构造 user prompt（文档片段 + 用户查询）
    3. 调用 OpenAI API（structured output 模式）
    4. 记录响应时间
    5. Pydantic 验证
    6. 返回 TrustLayerResponse 对象
    
    异常处理：
    - 超时 → 返回降级响应
    - API 错误 → 返回降级响应
    - JSON 验证失败 → 返回降级响应
    """

    # ── 防弹演示模式：0 延迟返回预写响应 ──
    if MOCK_LLM_MODE:
        return get_mock_response(user_query)

    # ── 正常模式：真实调用 OpenAI API ──
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
        # 超时 / API 错误 / JSON 解析失败 → 降级响应
        return create_fallback_response({})


def build_user_prompt(retrieved_docs: list, user_query: str) -> str:
    """构造 User Prompt：检索到的文档片段 + 用户问题（仅 MOCK_LLM_MODE=False 时调用）"""

def generate_query_id() -> str:
    """生成唯一查询 ID（时间戳 + 随机数）"""

def calculate_response_time(start_time: float) -> int:
    """计算响应时间（毫秒）"""
```

#### Bulletproof Demo Mode Data Flow

```
用户输入查询
    │
    ▼
call_llm_api(user_query)
    │
    ├── MOCK_LLM_MODE == True ?
    │       │
    │       ├── YES → get_mock_response(query)
    │       │            │
    │       │            ├── 关键词匹配 → "high" / "medium" / "low"
    │       │            ├── 取 MOCK_RESPONSES[scenario]
    │       │            ├── 更新 timestamp + query_id
    │       │            ├── Pydantic 验证
    │       │            └── 返回 TrustLayerResponse（0 延迟）
    │       │
    │       └── NO  → 正常 OpenAI API 调用流程（方案 A）
    │                    │
    │                    ├── mock_rag_retrieve(query)
    │                    ├── build_user_prompt(docs, query)
    │                    ├── openai.chat.completions.create(...)
    │                    ├── validate_response(raw_json)
    │                    └── 返回 TrustLayerResponse（≤3s 或降级）
    │
    ▼
返回 TrustLayerResponse → frontend.py 渲染
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
    前台主渲染函数：
    1. 显示搜索框 + 引导语（IDLE 状态）
    2. 用户提交查询 → 调用 llm_api.call_llm_api()
    3. 渲染响应结果（render_response）
    4. 记录交互日志
    """

def render_response(response: TrustLayerResponse):
    """
    渐进式渲染核心函数（方案 A：数据已在内存，0 延迟展开）：
    
    渲染顺序：
    1. render_confidence_label()     — 置信度标签（始终显示）
    2. render_alert_banner()          — 低置信度警报（仅 low 时显示）
    3. st.markdown(response.answer.text)  — AI 回答文本
    4. render_details_expander()      — 详情 expander（渐进式呈现核心）
    """

def render_confidence_label(level: ConfidenceLevel, is_inferred: bool):
    """
    三档差异化标签渲染：
    - high  → st.success("🟢 高可信")
    - medium → st.warning("🟡 部分匹配 · 建议核对")
    - low   → st.error("🔴 低可信 · 需人工核实")
    - is_inferred → 追加 st.caption("(AI推断)")
    """

def render_alert_banner(verification_advice):
    """
    低置信度警报横幅（仅 confidence_level == "low" 时调用）：
    - 浅红色背景 + 红色边框
    - 大白话警告文案
    - 行动链接按钮（st.button + session_state 导航）
    - 不可关闭
    """

def render_details_expander(response: TrustLayerResponse):
    """
    详情 expander（⚠️ Bug 修正后版本）：
    
    核心实现：
        expanded = (response.answer.confidence_level == ConfidenceLevel.MEDIUM)
        
        with st.expander("📄 详情", expanded=expanded):
            render_sources(response.sources)                    # 来源列表
            with st.expander("ℹ️ 术语解释", expanded=False):    # 术语独立 expander
                render_jargon_glossary(response.jargon_glossary)
            render_verification_advice(response.verification_advice)
    
    ⚠️ 严禁使用 st.button 控制展开/收起（Bug 1 修正）
    ⚠️ 严禁使用"半展开"概念（Bug 2 修正，用双 expander 替代）
    """

def render_sources(sources: list):
    """
    F1 来源标注渲染：
    - 按 match_score 降序排列
    - 每条：📄 文档名 · 第X页 + 匹配度% + 摘录 expander
    - 空数组降级文案
    """

def render_jargon_glossary(jargon_glossary: list):
    """
    F3 术语解释渲染：
    - 每个术语：💬 大白话（默认显示）+ 📖 正式定义 expander（收起）
    - 查看时更新 st.session_state["jargon_views"]
    """

def render_verification_advice(verification_advice):
    """
    F4 核实建议渲染：
    - needs_verification == false → 不显示
    - confidence_level == "low" → 显示"详见上方警报"
    - 其他 → 显示字段列表 + 行动链接按钮
    - 点击行动链接 → st.session_state 导航到 DOCUMENT_VIEW
    """

def render_document_view(doc_name: str, page_number: int):
    """
    DOCUMENT_VIEW 状态渲染：
    - 从 mock_docs.get_document_page() 获取内容
    - 显示文档名 + 页码 + 原文内容
    - 返回按钮
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
    Admin Dashboard 主渲染函数：
    1. 从 st.session_state["interaction_log"] 获取日志
    2. 调用 calculate_admin_metrics() 计算指标
    3. 渲染三项指标卡片
    4. 渲染高频术语 Top 5
    5. 渲染最近查询记录表
    """

def render_metric_cards(metrics: dict):
    """
    三项指标卡片（st.columns(3) + st.metric）：
    - 信任健康度（核实点击率）
    - 低置信度触发率
    - 总查询数
    """

def render_top_jargon(jargon_list: list):
    """高频查看术语 Top 5（st.table 或 st.dataframe）"""

def render_recent_queries(queries: list):
    """最近 10 条查询记录（st.dataframe）"""
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
    """初始化 st.session_state 中的日志相关变量"""

def log_interaction(response, user_query: str, response_time: int):
    """创建日志条目并存入 st.session_state["interaction_log"]"""

def update_jargon_view(term: str):
    """记录用户查看了某个术语"""

def update_verification_click():
    """记录用户点击了核实建议"""

def update_details_viewed():
    """记录用户查看了详情"""

def calculate_admin_metrics(log: list) -> dict:
    """
    计算 Admin Dashboard 三项指标（直接复用 Step 4.11 的逻辑）：
    - total_queries
    - trust_health (核实点击率)
    - low_conf_rate (低置信度触发率)
    - top_jargon (高频术语 Top 5)
    - recent_queries (最近 10 条)
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
# OpenAI API 配置
OPENAI_API_KEY=sk-your-api-key-here

# 模型选择（推荐 gpt-4o-mini，成本低）
LLM_MODEL=gpt-4o-mini

# 超时设置（秒）
LLM_TIMEOUT=3.0

# 防弹演示模式：true=离线静态响应(录屏/演示用) / false=真实API调用
MOCK_LLM_MODE=true
```

### `.env` (not in version control)

```
OPENAI_API_KEY=sk-你的真实key
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

> **Estimation premise**: User is a Python beginner, investing 3–4 hours per day. Each Phase ends with a "verification checkpoint" — it must pass before proceeding to the next stage.

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
| Implement mock_rag_retrieve() | mock_docs.py | Searching "转辙机" returns documents containing that keyword |
| Implement get_document_page() | mock_docs.py | Pass document name + page number, return page content |
| Write models.py (Pydantic models) | models.py | `TrustLayerResponse(**test_json)` validates |
| **Implement MOCK_RESPONSES static data** | **llm_api.py** | **3 pre-written JSONs pass Pydantic validation** |
| **Implement get_mock_response()** | **llm_api.py** | **Input "信号制式" → returns high; input "预算" → returns low; input "转辙机" → returns medium** |
| **Implement call_llm_api() mock branch** | **llm_api.py** | **With MOCK_LLM_MODE=True, returns TrustLayerResponse with 0 latency** |

**Phase B acceptance**: Add a temporary test snippet in app.py:
1. Search "XX项目设备" and print retrieval results, confirm it returns a list of Source objects
2. Call `call_llm_api("信号系统采用什么制式")`, confirm it returns a high-confidence response (0 latency)
3. Call `call_llm_api("工程造价预算是多少")`, confirm it returns a low-confidence response + alert data

> **Key strategy**: The Mock mode is implemented in Phase B; during Phase D front-end development you can test directly against mock mode — no need to wait for the API to work, and no API quota consumed. The real API integration of Phase C can be deferred or skipped (Demo recording does not require a real API).

---

### Phase C: API Layer (Day 3) — ⚠️ Optional (Mock mode already covers Demo needs)

**Goal**: OpenAI API callable, returns JSON conforming to the data contract

> **Note**: If time is tight, Phase C can be skipped or deferred. The Phase B Mock mode already supports all of Phase D–F development and Demo recording. Phase C is executed only when real API integration needs verification.

| Task | File | Verification point |
|------|------|--------|
| Implement SYSTEM_PROMPT | llm_api.py | Prompt content consistent with Step 4.7 |
| Implement build_user_prompt() | llm_api.py | Print prompt, confirm document fragments and query are assembled correctly |
| Implement call_llm_api() | llm_api.py | Input query, returns TrustLayerResponse object |
| Implement validate_response() | models.py | Valid JSON in → passes; missing-field JSON in → degrades |
| Implement create_fallback_response() | models.py | Degraded response confidence_level == "low" |
| Test timeout handling | llm_api.py | LLM_TIMEOUT=0.1 triggers degradation |

**Phase C acceptance**: In app.py, input "XX项目需要什么设备？"; the LLM returns complete JSON, Pydantic validation passes, print the TrustLayerResponse object.

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
用户输入查询
    │
    ▼
┌─ app.py ─────────────────────────────────┐
│  st.session_state["view_mode"] == "front" │
│  → 调用 frontend.render_frontend()       │
└──────────────┬───────────────────────────┘
               │
               ▼
┌─ frontend.py ────────────────────────────┐
│  st.spinner("正在检索文档并生成回答...")   │
│  → 调用 llm_api.call_llm_api(query)      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌─ llm_api.py ─────────────────────────────┐
│                                          │
│  ┌─ MOCK_LLM_MODE == True ? ───────────┐ │
│  │                                      │ │
│  │  YES (防弹演示模式)                   │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │ get_mock_response(query)        │ │ │
│  │  │  ├ 关键词匹配 → scenario        │ │ │
│  │  │  ├ 取 MOCK_RESPONSES[scenario]  │ │ │
│  │  │  ├ 更新 timestamp + query_id   │ │ │
│  │  │  ├ Pydantic 验证               │ │ │
│  │  │  └ → TrustLayerResponse (0ms)  │ │ │
│  │  └──────────────┬──────────────────┘ │ │
│  │                 │                     │ │
│  │  NO (真实API模式)                     │ │
│  │  ┌──────────────┴──────────────────┐ │ │
│  │  │ 1. mock_rag_retrieve(query)     │ │ │
│  │  │    → list[Source] (≤3条)        │ │ │
│  │  │ 2. build_user_prompt(docs,q)    │ │ │
│  │  │ 3. openai.chat.completions      │ │ │
│  │  │    .create(json_object, 3s)     │ │ │
│  │  │    → 完整 JSON (一次调用)        │ │ │
│  │  │ 4. validate_response(raw_json)  │ │ │
│  │  │    → 通过: Response 对象         │ │ │
│  │  │    → 失败: fallback_response()  │ │ │
│  │  └──────────────┬──────────────────┘ │ │
│  └─────────────────┼────────────────────┘ │
└────────────────────┼──────────────────────┘
                     │ TrustLayerResponse
                     ▼
┌─ frontend.py ────────────────────────────┐
│  render_response(response):              │
│                                          │
│  ① render_confidence_label(level)        │
│     high  → st.success("🟢 高可信")      │
│     medium → st.warning("🟡 部分匹配")   │
│     low   → st.error("🔴 低可信")        │
│                                          │
│  ② if level == "low":                    │
│       render_alert_banner(verif_advice)  │
│                                          │
│  ③ st.markdown(response.answer.text)     │
│                                          │
│  ④ with st.expander("📄 详情",           │
│       expanded=(level=="medium")):       │
│       │                                  │
│       ├─ render_sources(sources)         │
│       │                                  │
│       ├─ with st.expander("ℹ️ 术语",     │
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

| Risk | Probability | Impact | Mitigation strategy |
|------|------|------|---------|
| OpenAI `json_object` mode returns JSON not matching the Pydantic schema | Medium | High | `validate_response()` + `create_fallback_response()` degradation already built in |
| LLM response time > 3s | Low | Medium | `timeout=3.0` parameter + timeout degradation response |
| **Demo recording / interview demo suddenly loses API access** | **Medium** | **Fatal** | **✅ Solved: `MOCK_LLM_MODE = True` skips the API, returns pre-written static JSON, 0 latency, 100% controllable** |
| **On-site interview loses network** | **Low** | **Fatal** | **✅ Solved: Mock mode needs no network; runs locally on localhost** |
| Mock document keyword match scores unreasonable (all 0 or all 1) | Medium | Low | Add normalization logic + minimum match threshold 0.1 in `mock_rag_retrieve()` |
| Streamlit rerun causes session_state loss | Low | High | session_state is Streamlit's officially recommended persistence method, auto-preserved across reruns |
| Medium-confidence expander auto-expands, then user manually collapses it, and state isn't refreshed when querying a new question | Medium | Low | Each new query overwrites `current_response`; the expander's `expanded` param is recomputed from the new response |
| **Mock response keywords miss, causing wrong Demo scenario** | **Low** | **Medium** | **Demo script fixes predefined query statements (locked in Step 6), not relying on free input** |

---

## 5.9 Traceability Matrix to Step 4 Specifications

| Step 4 Spec item | Step 5 Implementation location | Status |
|---------------|----------------|---------|
| 4.1 UI state machine | app.py (view_mode routing) + frontend.py (render_response) | ✅ Planned |
| 4.2 F1 Source attribution | frontend.py → render_sources() | ✅ Planned |
| 4.3 F2 Confidence + alert | frontend.py → render_confidence_label() + render_alert_banner() | ✅ Planned |
| 4.3 Bug 2 fix (dual expander) | frontend.py → render_details_expander() | ✅ Planned |
| 4.4 F3 Jargon explanation | frontend.py → render_jargon_glossary() | ✅ Planned |
| 4.5 F4 Verification advice | frontend.py → render_verification_advice() | ✅ Planned |
| 4.6 F7 Admin Dashboard | admin.py → render_admin() + three sub-functions | ✅ Planned |
| 4.7 DC data contract | models.py (Pydantic models + validation + degradation) | ✅ Planned |
| 4.8 N1 Latency control (Option A) | llm_api.py → call_llm_api() (single request) | ✅ Planned |
| 4.8 Bug 1 fix (st.expander) | frontend.py → render_details_expander() | ✅ Planned |
| 4.9 N2 JSON validation | models.py → validate_response() + Pydantic Field constraints | ✅ Planned |
| 4.10 Mock document set | mock_docs.py + mock_documents/*.md | ✅ Planned |
| 4.11 Interaction log | interaction_log.py (InteractionLogEntry + metric calculation) | ✅ Planned |
| 4.12 Feature-Component-Data master table | All modules mapped | ✅ Planned |
| **Bulletproof Demo Mode (driven by Step 6)** | **config.py (MOCK_LLM_MODE) + llm_api.py (get_mock_response + MOCK_RESPONSES)** | **✅ Planned** |

---

## 5.10 Next Steps Preview

After confirming Step 5, proceed to:

**Step 6: Prototype Scope Definition (Portfolio Deliverables)**

- Determine which files to submit for the Portfolio (code + docs + screenshots/recordings)
- Portfolio narrative structure (how to write the README for admissions officers)
- Interview demo script (3-minute Demo flow)
- Alignment check against UL MSc thesis requirements

Or, if you are ready to start coding, go directly to:

**Step 7: Design & Implementation (Coding)**

- Code in Phase A → F order
- Verify after each Phase before proceeding to the next

---
