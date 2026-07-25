# AI Trust Layer

A prototype trust interface layer for enterprise RAG systems — designed to help non-technical users **understand, trust, and act on** AI-generated answers.

![AI Trust Layer — Home Onboarding](screenshots/new_01_home_onboarding.png)

> Every AI answer, accountable. See where it comes from. Know how much to trust it. Verify when it matters.

## Problem

Enterprise RAG systems (e.g., AI-powered tender assistants) produce technically correct answers, but non-technical users can't assess **where** the information comes from, **how confident** the AI is, or **when to verify**. This "trust gap" renders the system unused in practice.

## Solution

AI Trust Layer is an interface component that attaches to any RAG system's output, providing:

- **Source Transparency** — Every answer cites its source documents with page numbers and match scores
- **Confidence Calibration** — Three-tier labels (High / Medium / Low) with differentiated UI behavior
- **Progressive Disclosure** — Minimal default view; details expand on demand (anti-information-overload)
- **Low-Confidence Alerts** — Plain-language warnings with direct links to source documents when AI is uncertain
- **Jargon Translation** — Technical terms auto-translated to plain language, with formal definitions on demand
- **Admin Dashboard** — Trust health metrics, low-confidence rates, and frequently-viewed jargon for system iteration

![Low-Confidence Alert — Redesigned](screenshots/new_02_low_confidence_alert.png)

> When confidence is low, the system doesn't just show a score — it warns in plain language with a direct link to the source document. This is trust calibration, not trust automation.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Set MOCK_LLM_MODE=true for offline demo (no API key needed)

# 3. Run
streamlit run app.py

# 4. Open browser
# http://localhost:8501
```

## Demo Queries

| Query | Triggers | What to look for |
|-------|----------|-----------------|
| "What signaling system does Project XX use?" | High confidence | Green label, collapsed details, clean sources |
| "What are the technical parameters of ZDJ-200 switch machine?" | Medium confidence | Yellow label, auto-expanded sources, collapsed jargon |
| "What is the construction budget for YY Line?" | Low confidence | Red alert banner, action link, inferred answer |

## Architecture

```
Streamlit Frontend (Li Ming + Wang Fang)
    |
Python Controller (JSON Validation + Confidence Logic)
    |
OpenAI API (Structured Output) + Mock Document Store
```

### Bulletproof Demo Mode

Set `MOCK_LLM_MODE=true` in `.env` to bypass OpenAI API entirely. The system returns pre-written static JSON responses (0ms latency, 100% deterministic). Use this for:
- Recording demo videos
- Live presentations
- Offline development

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Web UI | Streamlit | Pure Python, no HTML/CSS/JS needed |
| LLM API | OpenAI (gpt-4o-mini) | Structured JSON output |
| Data Validation | Pydantic v2 | JSON Schema enforcement |
| Config | python-dotenv | Environment variable management |

## Project Structure

```
ai_trust_layer/
├── app.py              # Entry point, routing, session state
├── config.py           # Global config, MOCK_LLM_MODE switch
├── models.py           # Pydantic data contract (TrustLayerResponse)
├── mock_docs.py        # Mock document store + simulated RAG retrieval
├── llm_api.py          # LLM API calls + mock mode dispatcher
├── frontend.py         # Li Ming's view: F1-F4 rendering
├── admin.py            # Wang Fang's view: F7 Admin Dashboard
├── interaction_log.py  # Interaction logging + metrics calculation
├── mock_documents/     # 10 simulated project documents
├── requirements.txt    # 4 dependencies only
└── .env.example        # Configuration template
```

## Design Principles

1. **Progressive Disclosure** — Default minimal, expand on demand
2. **Trust Calibration** — Three tiers, never binary trust/distrust
3. **Plain Language First** — Show `plain_language` by default, formal definitions on demand
4. **Structured Data Contract** — JSON Schema between frontend and backend, no NLP guessing
5. **Human-AI Loop** — Frontend trust interface + backend admin dashboard = iterative system

## Academic Context

This prototype is developed as part of a portfolio for the MSc in Interaction and Experience Design at the University of Limerick. It addresses the HCI core topic of **Explainable AI (XAI)** and **Trust Calibration** in enterprise AI systems.

---

Built with Python, Streamlit, and a commitment to making AI trustworthy for everyone.

**Designed by Shuting Fan** · MSc Interaction & Experience Design Portfolio · University of Limerick
