"""
config.py - AI Trust Layer 全局配置

职责：集中管理所有配置项，从 .env 读取敏感信息
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM API 配置 ──────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "3.0"))

# ── 防弹演示模式（Bulletproof Demo Mode）──────────────────
# True  -> llm_api.py 跳过 OpenAI 调用，直接返回预写静态 JSON（0 延迟、100% 可控）
# False -> 正常调用 OpenAI API
#
# 使用场景：
#   - 录制 Demo 视频 / 面试 Live 演示 -> 设为 True
#   - 开发调试前台界面 -> 设为 True（不消耗 API 额度）
#   - 验证 API 集成 / 测试真实置信度 -> 设为 False
MOCK_LLM_MODE: bool = os.getenv("MOCK_LLM_MODE", "true").lower() == "true"

# ── 置信度阈值 ────────────────────────────────────────────
CONFIDENCE_HIGH_THRESHOLD: float = 0.75
CONFIDENCE_LOW_THRESHOLD: float = 0.50

# ── 数据契约约束 ──────────────────────────────────────────
MAX_SOURCES: int = 5
MAX_JARGON_TERMS: int = 10
MAX_ANSWER_LENGTH: int = 2000

# ── Mock 文档路径 ─────────────────────────────────────────
MOCK_DOCS_DIR: str = os.path.join(os.path.dirname(__file__), "mock_documents")
