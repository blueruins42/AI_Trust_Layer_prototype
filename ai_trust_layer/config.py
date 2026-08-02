"""
config.py - AI Trust Layer global configuration

Responsibility: centralise all configuration items, read sensitive info from .env
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM API configuration ──────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "3.0"))

# ── Bulletproof Demo Mode ──────────────────────────────────────────
# True  -> llm_api.py skips the OpenAI call and returns pre-written static JSON directly (0 latency, 100% controllable)
# False -> call the OpenAI API normally
#
# Use cases:
#   - Record demo video / live interview demo -> set to True
#   - Develop/debug the frontend UI -> set to True (no API quota consumed)
#   - Verify API integration / test real confidence -> set to False
MOCK_LLM_MODE: bool = os.getenv("MOCK_LLM_MODE", "true").lower() == "true"

# No API key configured -> the real OpenAI path cannot succeed, so force the
# bulletproof demo (mock) mode. This keeps `streamlit run app.py` working out of
# the box (no env setup) instead of silently falling back to red "could not be
# parsed" responses whenever an LLM key is absent.
if not OPENAI_API_KEY:
    MOCK_LLM_MODE = True

# ── Confidence thresholds ──────────────────────────────────────────
CONFIDENCE_HIGH_THRESHOLD: float = 0.75
CONFIDENCE_LOW_THRESHOLD: float = 0.50

# ── Data contract constraints ──────────────────────────────────────
MAX_SOURCES: int = 5
MAX_JARGON_TERMS: int = 10
MAX_ANSWER_LENGTH: int = 2000

# ── Mock document path ─────────────────────────────────────────────
MOCK_DOCS_DIR: str = os.path.join(os.path.dirname(__file__), "mock_documents")
