# PRD Step 6: Portfolio Scope Definition

> Product working name: AI Trust Layer
> Phase: Full Product Design Process — Step 6
> Date: 2026-07-24
> Upstream inputs: All confirmed deliverables from Steps 1–5
> This step's outputs: Portfolio deliverables list, GitHub README structure, 3-minute Demo script, Must-Work vs Mock matrix, Portfolio narrative structure

---

## 6.0 Core Principle: Begin with the End in Mind

**You are not selling software; you are demonstrating the depth of your thinking to the admissions officer.**

| Dimension | Software Product Mindset | Portfolio Mindset |
|-----------|--------------------------|-------------------|
| Goal | User adoption, DAU, revenue | Persuade the admissions officer within 3 minutes |
| Metrics | Feature completeness, performance, stability | Problem insight × Design reasoning × Technical execution |
| Code requirement | Every feature must work | Features covered by the Demo script must work; the rest may be Mocked |
| Documentation requirement | API docs, user manuals | README narrative + PRD chain + Demo screen recording |
| Visual requirement | UI polish | Screenshots that tell a story (high / medium / low three tiers + Admin dashboard) |

**Iron rule**: When writing code in Step 7, first consult the §6.4 Must-Work vs Mock matrix in this step. For any feature not in the Must-Work column, implement it in the simplest way or Mock it directly — never spend more than 30 minutes on it.

---

## 6.1 Portfolio Deliverables List

### Complete file package to submit to UL

```
portfolio_submission/
├── README.md                          # GitHub homepage (the first thing the admissions officer sees)
├── PRD/                               # Product design document chain (Step 1-6)
│   ├── 01_PRD_Step1_Problem_Definition_EN.md
│   ├── 02_PRD_Step2_User_Personas_EN.md
│   ├── 03_PRD_Step3_Product_Vision_EN.md
│   ├── 04_PRD_Step4_Functional_Specs_EN.md
│   ├── 05_PRD_Step5_Technical_Architecture_EN.md
│   └── 06_PRD_Step6_Portfolio_Scope_EN.md
├── ai_trust_layer/                    # Runnable prototype code
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── mock_docs.py
│   ├── llm_api.py
│   ├── frontend.py
│   ├── admin.py
│   ├── interaction_log.py
│   ├── requirements.txt
│   ├── .env.example
│   └── mock_documents/
├── demo/
│   ├── demo_video.mp4                 # 3-minute screen recording
│   └── screenshots/                   # 4 key screenshots for the README
│       ├── 01_high_confidence.png     # High confidence scenario
│       ├── 02_low_confidence_alert.png # Low confidence alert scenario
│       ├── 03_progressive_disclosure.png # Progressive disclosure expanded
│       └── 04_admin_dashboard.png     # Admin dashboard
└── PORTFOLIO_NARRATIVE.md             # 1-page narrative summary (if UL requires a separate document)
```

### Deliverable priorities

| Priority | Deliverable | Rationale |
|----------|-------------|-----------|
| **P0 Required** | README.md + demo_video.mp4 + screenshots/ | The admissions officer's attention is 90% here |
| **P0 Required** | ai_trust_layer/ runnable code | Proves "I actually wrote code," not a PowerPoint project |
| **P1 Should submit** | PRD/ Step 1–5 document chain | Proves "my design reasoning process," not guesswork |
| **P2 Optional** | PORTFOLIO_NARRATIVE.md | Only if the UL application system requires uploading a separate document |

---

## 6.2 GitHub README Structure

After the admissions officer opens the GitHub repository, the **first 30 seconds** decide whether they keep looking. The README must accomplish three things above the fold: state the problem clearly, show the solution, and prove technical capability.

### README structure design

```markdown
# AI Trust Layer
### Helping non-technical users understand, trust, and use AI answers

> A trust interface layer for enterprise RAG systems — designed for non-technical users who need to understand, trust, and act on AI-generated information.

[One-line positioning] | [Tech stack tags] | [MSc Portfolio label]

---

## 🎯 The Problem

[2-3 sentences describing the problem: the RAG system is technically perfect, but non-technical users dare not use it and do not know how to use it]

[Insert screenshot 01_high_confidence.png — showing "even normal scenarios show sources and confidence"]

---

## 💡 The Solution

[3-4 sentences describing the solution: progressive disclosure + three-tier confidence + low-confidence alert + Admin monitoring]

### Key Features

| Feature | What It Does | Why It Matters |
|---------|--------------|----------------|
| 📊 Confidence Indicator | Three-tier labels (high / medium / low) recognizable at a glance | Users don't need to read a score — they know by color whether to trust it |
| 🚨 Low-Confidence Alert | Low confidence pops up a plain-language alert + action link | Not a cold score, but tells the user "what to do" |
| 📄 Source Transparency | Every answer is annotated with the source document and page number | Trust requires traceability |
| 📖 Jargon Translation | Technical jargon is automatically translated into plain language | Eliminates the "cognitive translation gap" |
| 📈 Admin Dashboard | Monitors trust health, low-confidence rate, high-frequency jargon | Upgrades from "one-way display" to a "human-in-the-loop closed loop" |

[Insert screenshot 02_low_confidence_alert.png — showing the low-confidence alert]

---

## 🏗️ Architecture

[Insert architecture diagram — simplified version copied from Step 5]

```
Streamlit Frontend (Li Ming + Wang Fang)
    ↕
Python Controller (JSON Validation + Confidence Logic)
    ↕
OpenAI API (Structured Output) + Mock Document Store
    ↕
Bulletproof Demo Mode (MOCK_LLM_MODE toggle)
```

**Design Principles:**
1. Progressive Disclosure — minimal by default, expand on demand
2. Trust Calibration — three-tier differentiation, doesn't make decisions for the user
3. Structured Data Contract — JSON Schema driven, no NLP guessing
4. Human-AI Loop — front-end trust interface + back-end Admin = iterative system

---

## 🎬 Demo

[Insert screenshot 03_progressive_disclosure.png — showing the expanded detail view]

**3-minute demo video:** `demo/demo_video.mp4`

**Try it yourself:**
```bash
pip install -r requirements.txt
cp .env.example .env  # Set MOCK_LLM_MODE=true for offline demo
streamlit run app.py
```

> **Bulletproof Demo Mode**: When `MOCK_LLM_MODE=true` in `.env`, the app does not call the OpenAI API and directly returns pre-written static JSON (0 latency, 100% controllable). Keep this mode on when recording the Demo video and during live interview demos. Set it to `false` to enable real API calls.

---

## 📐 Design Process

This prototype was developed through a structured 6-step product design process:

1. **Problem Definition** — extracted 4 formalized problems from real work experience
2. **User Research** — 3 user personas + user journey + requirement prioritization matrix
3. **Product Vision** — vision statement + 5 design principles + MVP scope
4. **Functional Specs** — detailed specs for 6 features + Pydantic data contract + Gherkin acceptance criteria
5. **Technical Architecture** — 8-module architecture + Plan A latency control + 7-day development plan
6. **Portfolio Scope** — begin with the end in mind, Demo-driven implementation priority

Full PRD documents in `/PRD` folder.

---

## 🔬 MSc Thesis Alignment

**Proposed thesis title:** *An AI Trust Layer for Enterprise RAG Systems: Designing Transparency and Trust Calibration for Non-Technical Users*

This portfolio demonstrates:
- ✅ Significant technical challenge (LLM structured output + Pydantic validation + Streamlit state management)
- ✅ HCI theoretical grounding (Progressive Disclosure, Trust Calibration, Cognitive Load Theory)
- ✅ Real-world problem (based on enterprise RAG system deployment experience)
- ✅ Prototype implementation (runnable code, not just mockups)

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| Frontend | Streamlit | Pure Python, no HTML/CSS/JS needed |
| LLM | OpenAI API (gpt-4o-mini) | Structured output (JSON mode) |
| Validation | Pydantic v2 | Type-safe data contract enforcement |
| Config | python-dotenv | Environment variable management |

---

## 📄 License

MIT — This is a portfolio project for academic application purposes.
```

### README above-the-fold screenshot selection logic

| Screenshot location | Choice | Rationale |
|---------------------|--------|-----------|
| Below the Problem section | 01_high_confidence.png | Shows "even in normal scenarios, there are sources and confidence" — this is the differentiator |
| Below the Solution section | 02_low_confidence_alert.png | The low-confidence alert is the most visually striking feature; the red alert banner grabs attention at a glance |
| Below the Demo section | 03_progressive_disclosure.png | The expanded detail view, proving "progressive disclosure is not empty talk" |
| Architecture or bottom | 04_admin_dashboard.png | Proves "this is not a one-way display; there is a back-end monitoring closed loop" |

---

## 6.3 Three-Minute Demo Script

**This is the most core deliverable of Step 6.** The Demo script determines which code in Step 7 must work and which can be Mocked.

### Screen recording technical requirements

| Item | Specification |
|------|---------------|
| Duration | 2:45 - 3:15 (strictly within 3 minutes) |
| Resolution | 1920×1080 |
| Recording tool | OBS Studio / Windows built-in screen recorder |
| Speaking pace | Bilingual Chinese-English subtitles (can be added later), narration or voice-over |
| Browser | Chrome, full-screen mode with bookmarks bar hidden |
| **Run mode** | **`MOCK_LLM_MODE=true` (bulletproof demo mode)** — ensure the API does not stall, disconnect, or fail to trigger the expected scenario 100% of the time during recording |

> **⚠️ Pre-recording checklist**:
> 1. `MOCK_LLM_MODE=true` in `.env` ✓
> 2. Use the locked Demo query statements below (precisely matched with mock keywords) ✓
> 3. 3 seed logs pre-filled when `app.py` initializes ✓
> 4. Do a dry run of all 6 Scenes first to confirm no errors before the official recording ✓

### Scene breakdown (6 scenes, each 25–35 seconds)

---

#### Scene 1: Opening & Problem Statement (0:00 - 0:30)

**Screen**: Browser opens `localhost:8501`, showing the AI Trust Layer homepage (empty search box + guidance text)

**Narration/subtitles**:
> "In enterprise RAG systems, AI can retrieve information perfectly — but non-technical users often don't trust or understand the output. AI Trust Layer solves this by making AI answers transparent, calibrated, and actionable."

**Action**: No operation, static display of homepage

**Must-Work code**: `app.py` can start, `frontend.py`'s `render_frontend()` can render the search box and guidance text

---

#### Scene 2: High-Confidence Query — "Even Normal Scenarios Have Transparency" (0:30 - 1:00)

**Screen**: Enter `XX项目信号系统采用什么制式` in the search box, click search

**Action chain**:
1. Enter query (contains "信号" + "制式" → triggers high scenario)
2. Show loading animation `st.spinner("正在检索文档并生成回答...")`
3. Render result after ~0 seconds (0 latency in Mock mode):
   - 🟢 High confidence label (green)
   - AI answer text (CBTC system description)
   - 📄 Details expander (collapsed state)
4. Mouse click to expand "📄 Details"
5. After expanding, show: source list (📄 XX项目技术规格书 · Page 15 · Match 95%) + jargon explanation expander (collapsed) + verification suggestion (no verification needed)

**Narration/subtitles**:
> "Even for high-confidence answers, users can see where the information comes from. Sources are ranked by match score, and technical jargon is translated into plain language — but only when the user chooses to expand."

**Must-Work code**:
- `llm_api.call_llm_api()` — Mock mode returns pre-written high JSON
- `models.validate_response()` — Pydantic validation passes
- `frontend.render_confidence_label()` — green label
- `frontend.render_details_expander()` — expander expands without crashing (Bug 1 verification)
- `frontend.render_sources()` — source list rendering
- `frontend.render_jargon_glossary()` — jargon expander rendering

**Can be Mocked**: The LLM API call itself (`MOCK_LLM_MODE=true`). UI rendering and interaction must genuinely work — this is the Demo's "trust anchor."

---

#### Scene 3: Low-Confidence Query — "The Alert Mechanism Is the Core Differentiator" (1:00 - 1:35)

**Screen**: Clear the search box, enter `YY线路的工程造价预算是多少` (no fully matching content in the Mock documents → triggers low scenario)

**Action chain**:
1. Enter query (contains "造价" + "预算" → triggers low scenario)
2. Loading animation (flashes by in Mock mode)
3. Render result:
   - 🔴 Low confidence label (red)
   - 🚨 Red alert banner: "⚠️ No fully matching specification was found in the database; this answer is for reference only. Please be sure to click [source document Page 22] to manually verify."
   - AI answer text (marked with "(AI inference)")
   - 📄 Details expander (collapsed state)
4. Mouse click the action link "📄 View the most relevant document, Page 15" in the alert banner
5. Jump to the document view, showing the original text content

**Narration/subtitles**:
> "When confidence is low, the system doesn't just show a score — it proactively warns the user in plain language and provides a direct link to the source document for manual verification. This is trust calibration, not trust automation."

**Must-Work code**:
- `mock_docs.mock_rag_retrieve()` — returns a low match score for vague queries
- `frontend.render_alert_banner()` — red alert banner rendering
- `frontend.render_document_view()` — document jump and original text display
- `interaction_log.log_interaction()` — logs low-confidence query + verification click

**Can be Mocked**: The LLM API call itself (`MOCK_LLM_MODE=true`, the pre-written low-scenario JSON already contains the alert data and action link). UI rendering (alert banner + document jump + log recording) must genuinely work.

---

#### Scene 4: Progressive Disclosure — "Minimal by Default, Expand on Demand" (1:35 - 2:05)

**Screen**: Return to the search box, enter "ZDJ-200转辙机的技术参数是什么？" (medium match query)

**Action chain**:
1. Enter query
2. Render result:
   - 🟡 Partial match label (yellow)
   - AI answer text
   - 📄 Details expander (**auto-expanded** — medium confidence strategy)
   - Source list visible
   - ℹ️ Jargon explanation expander (**collapsed state** — dual expander strategy)
3. Mouse click to expand "ℹ️ Jargon explanation"
4. After expanding, show jargon list: 💬 Plain-language definition + 📖 Formal definition expander (collapsed)
5. Mouse click to expand a jargon's "📖 Formal definition"
6. **Key verification**: At this point both the details expander and the jargon expander remain expanded, without crashing

**Narration/subtitles**:
> "For medium-confidence answers, sources are shown by default but jargon stays collapsed — progressive disclosure reduces cognitive load. The user decides when to go deeper."

**Must-Work code**:
- `frontend.render_details_expander()` — medium confidence `expanded=True`
- Jargon expander's `expanded=False`
- **Bug 1 verification**: nested expander operations do not cause the outer expander to close
- **Bug 2 verification**: dual expander strategy works correctly

**Can be Mocked**: None. This scene is the verification scene for the bug fix and must genuinely work.

---

#### Scene 5: Admin Dashboard — "Human-in-the-Loop Closed Loop" (2:05 - 2:40)

**Screen**: Click the "🔄 Switch to Admin" button at the top of the page

**Action chain**:
1. Switch to Admin Dashboard view
2. Show three metric cards:
   - 📊 Trust health: 33% (1/3 queries triggered a verification click)
   - 🚨 Low-confidence trigger rate: 33% (1/3 queries were low confidence)
   - 📝 Total queries: 3
3. Show Top 5 high-frequency jargon (based on jargon viewed earlier)
4. Show recent query log table (3 records)

**Narration/subtitles**:
> "The Admin Dashboard turns this from a one-way display into a human-AI collaboration loop. Product owners can monitor trust health, identify knowledge gaps, and prioritize document updates."

**Must-Work code**:
- `app.py`'s front/back-end switching logic
- `admin.render_admin()` — full rendering
- `admin.render_metric_cards()` — three metrics correctly calculated
- `admin.render_top_jargon()` — high-frequency jargon sorted
- `admin.render_recent_queries()` — query log table
- `interaction_log.calculate_admin_metrics()` — metric calculation logic

**Can be Mocked**: The metric data comes from the real interaction logs of Scenes 2–4 earlier, so no extra Mock is needed. But to ensure the Demo data is not empty, you can pre-fill 2–3 seed logs when `app.py` initializes.

---

#### Scene 6: Closing & Design Philosophy (2:40 - 3:00)

**Screen**: Switch back to the front end, show the homepage

**Narration/subtitles**:
> "AI Trust Layer — because the last mile of AI adoption isn't about better models, it's about better trust. Designed through a 6-step product process, from real-world problem to runnable prototype. Full PRD documentation in the repository."

**Action**: No operation, static display

**Must-Work code**: The front/back-end switch can be switched back

---

### Demo Script → Must-Work Mapping Summary

| Scene | Duration | Core showcase | Must-Work feature |
|-------|----------|---------------|-------------------|
| 1 | 0:30 | Problem statement | app.py startup + frontend homepage rendering |
| 2 | 0:30 | High confidence + transparency | LLM API call + Pydantic validation + confidence label + source annotation + expander expansion |
| 3 | 0:35 | Low-confidence alert | Low match retrieval + alert banner + document jump |
| 4 | 0:30 | Progressive disclosure | Medium-confidence dual expander + nested operations without crashing |
| 5 | 0:35 | Admin closed loop | Front/back-end switch + three metrics + high-frequency jargon + query log |
| 6 | 0:20 | Closing | Switch front/back-end back |

---

## 6.4 Must-Work vs Mock Matrix

**This is the priority constitution for Step 7 coding.** For any feature not in the Must-Work column, implement it in the simplest way or Mock it.

### Must-Work (must genuinely work — Demo will showcase)

| # | Feature | Module | Demo Scene | Rationale |
|---|---------|--------|------------|-----------|
| MW-1 | Streamlit app startup | app.py | 1,6 | Foundation of the entire Demo |
| MW-2 | Search box + guidance text rendering | frontend.py | 1 | First glance above the fold |
| MW-3 | LLM API call (dual support for Mock mode + real mode) | llm_api.py | 2,3,4 | Proves "I understand API integration + data contract"; Mock mode ensures the Demo doesn't fail |
| MW-4 | Pydantic data contract validation | models.py | 2,3,4 | Proves "I understand data contracts" |
| MW-5 | Three-tier confidence label rendering | frontend.py | 2,3,4 | Core differentiator feature |
| MW-6 | Low-confidence alert banner | frontend.py | 3 | Most visually striking feature |
| MW-7 | Source annotation rendering | frontend.py | 2,4 | Core transparency feature |
| MW-8 | Jargon explanation (dual expander) | frontend.py | 2,4 | Bug 2 fix verification |
| MW-9 | Details expander expand/collapse | frontend.py | 2,3,4 | Bug 1 fix verification |
| MW-10 | Document jump view | frontend.py | 3 | Alert action link clickable |
| MW-11 | Interaction log recording | interaction_log.py | 2,3,4 | Admin data source |
| MW-12 | Front/back-end switch | app.py | 5,6 | Proves "dual-perspective system" |
| MW-13 | Admin three metrics | admin.py | 5 | Core back-end feature |
| MW-14 | Admin Top 5 high-frequency jargon | admin.py | 5 | Core back-end feature |
| MW-15 | Admin query log table | admin.py | 5 | Core back-end feature |
| MW-16 | Mock document loading + retrieval | mock_docs.py | 2,3,4 | RAG simulation foundation |

**Total 16 Must-Work features** — these are the coding core of Step 7 Phases A–F.

### Can-Simplify (can be simplified — Demo will not drill into)

| # | Feature | Simplification | Rationale |
|---|---------|----------------|-----------|
| CS-1 | `mock_rag_retrieve()` matching algorithm | Use simple keyword matching, not TF-IDF or vector retrieval | Demo only needs "can find" and "reasonable match score," not precise retrieval |
| CS-2 | Jargon explanation's plain_language | Pre-write the jargon glossary directly in the Mock documents, don't rely on the LLM to generate dynamically | Reduces uncertainty, Demo effect is controllable |
| CS-3 | Confidence calculation | Rely on the confidence_score returned by the LLM, no secondary calculation | Plan A already has the LLM return confidence |
| CS-4 | Admin metric calculation | Use native list/dict + Counter, don't introduce pandas | Small data volume (Demo only has 3–5 entries) |
| CS-5 | Error handling UI | Only do timeout degradation, don't do fine-grained handling of network errors / permission errors, etc. | Demo won't deliberately trigger network errors |

### Can-Mock (can be directly Mocked — Demo doesn't involve at all)

| # | Feature | Mock method | Rationale |
|---|---------|-------------|-----------|
| CM-1 | Multi-user support | Not implemented, session_state only stores single user | Demo is a single-person demonstration |
| CM-2 | Data persistence | Not implemented, cleared on refresh | Expected behavior at prototype stage |
| CM-3 | API rate limiting / cost control | Not implemented N3 | Demo won't run a large number of queries |
| CM-4 | Complete F8 trust health monitoring | Only do basic version (verification click rate), no trend chart | Step 2 already listed the full version as future work |
| CM-5 | F9 jargon heatmap | Not implemented | Step 2 already listed as future work |
| CM-6 | F5 format adaptation | Not implemented | Step 2 already listed as future work |
| CM-7 | F6 interaction log persistence | Not implemented, session_state in-memory is sufficient | Demo doesn't need cross-session data |
| CM-8 | Unit tests | Do in Step 8 | Get features working first in the coding phase |

---

## 6.5 Portfolio Narrative Structure

The admissions officer's attention curve when viewing the Portfolio:

```
Attention
  ↑
  │  ██████████
  │  ██        ██                 ████████
  │  ██        ██                 ██      ██
  │  ██        ██     ████████    ██      ██
  │  ██        ██     ██      ██  ██      ██     ████████
  │  ██        ██     ██      ██  ██      ██     ██      ██
  └────────────────────────────────────────────────────────→ Time
     README    Demo    PRD chain   Code    Demo video
   
     0-30s     30s-1m  1-2m        2-3m    3m+
     Above-fold impact   Feature showcase   Reasoning depth   Technical capability   Complete closed loop
```

### Three-act narrative structure

**Act 1: Problem (README above the fold + Demo Scene 1)**
- "AI systems are technically perfect, but users dare not use them and don't know how to use them"
- Backed by your real experience at Huaxin
- 1 high-confidence screenshot proving "even normal scenarios have transparency"

**Act 2: Solution (Demo Scene 2–4 + PRD Step 2–4)**
- Progressive disclosure → reduces cognitive load
- Three-tier confidence → trust calibration
- Low-confidence alert → plain-language guided action
- Dual expander strategy → design compromise under Streamlit's physical constraints
- PRD document chain proves "this is not guesswork design"

**Act 3: Closed Loop (Demo Scene 5–6 + PRD Step 5)**
- Admin Dashboard → human-in-the-loop iteration
- Technical architecture → 8 modules + Plan A + Pydantic data contract
- Closing → "the last mile is not better models, but better trust"

### "Signal words" that must appear in the narrative

Key terms the admissions officer cares about in HCI, ensure they appear in README / PRD / Demo subtitles:

| Signal word | Where it appears | Corresponding HCI theory |
|-------------|------------------|--------------------------|
| Progressive Disclosure | README + Demo Scene 4 | Nielsen's Heuristic |
| Trust Calibration | README + Demo Scene 3 | Lee & See (2004) |
| Cognitive Load | PRD Step 2 + Demo Scene 4 | Sweller's CLT |
| Explainable AI (XAI) | PRD Step 1 | XAI Research |
| Human-in-the-Loop | Demo Scene 5 | HITL Systems |
| Structured Output | README + PRD Step 4 | LLM Engineering |
| Data Contract | PRD Step 4 + README | API Design |

> **Note**: Signal words should be naturally embedded in the narrative, not piled up. Each word appearing 1–2 times is enough; too many seems deliberate.

---

## 6.6 Screenshot Shooting Guide

The 4 screenshots are the visual core of the README and must be carefully shot.

### Screenshot 01: High-Confidence Scenario

| Element | Specification |
|---------|---------------|
| Query | "XX项目需要什么信号设备？" |
| Display state | Answer rendered + details expander expanded + source list visible + jargon expander collapsed |
| Key visuals | 🟢 Green label + 📄 source list + match percentage |
| Purpose | Prove "normal scenarios also have transparency" |

### Screenshot 02: Low-Confidence Alert Scenario

| Element | Specification |
|---------|---------------|
| Query | "有没有能在隧道里用的通信设备？" |
| Display state | 🔴 Red label + 🚨 red alert banner + AI answer + action link |
| Key visuals | Red alert banner + plain-language warning copy + "📄 View the most relevant document, Page 15" link |
| Purpose | The most striking screenshot, proving "trust calibration is not empty talk" |

### Screenshot 03: Progressive Disclosure Expanded

| Element | Specification |
|---------|---------------|
| Query | "ZDJ-200转辙机的技术参数是什么？" |
| Display state | 🟡 Yellow label + details expander expanded + jargon expander expanded + formal definition expander expanded |
| Key visuals | Nested expander fully expanded + 💬 plain language + 📖 formal definition |
| Purpose | Prove "the hierarchy of progressive disclosure" + nested expander works correctly after bug fix |

### Screenshot 04: Admin Dashboard

| Element | Specification |
|---------|---------------|
| Display state | Three metric cards + Top 5 high-frequency jargon + recent query log table |
| Key visuals | st.metric cards × 3 + st.table jargon ranking + st.dataframe query log |
| Purpose | Prove "human-in-the-loop closed loop" |

### Suggested screenshot shooting order

```
1. Run Scene 2 first (high confidence) → Screenshot 01
2. Run Scene 4 (medium confidence) → expand all expanders → Screenshot 03
3. Run Scene 3 (low confidence) → Screenshot 02
4. Switch to Admin → Screenshot 04
```

> Shoot high confidence first because its interaction log is the "cleanest"; the low-confidence and medium-confidence shots taken later are appended to the log, making the Admin Dashboard data richer.

---

## 6.7 Demo Seed Data Strategy

To ensure the Admin Dashboard is not empty during the Demo, pre-fill seed logs in `app.py`'s `init_session_state()`:

```python
def init_session_state():
    if "interaction_log" not in st.session_state:
        # Seed logs: simulate that a user has used it before
        st.session_state["interaction_log"] = [
            InteractionLogEntry(
                query_id="seed-001",
                timestamp="2026-07-24 10:15:00",
                user_query="XX项目信号系统采用什么制式？",
                confidence_level="high",
                response_time_ms=1850,
                viewed_details=True,
                viewed_jargon=["CBTC"],
                clicked_verification=False,
                documents_searched=10,
                documents_matched=3
            ),
            InteractionLogEntry(
                query_id="seed-002",
                timestamp="2026-07-24 10:22:00",
                user_query="有没有能在隧道里用的通信设备？",
                confidence_level="low",
                response_time_ms=2100,
                viewed_details=True,
                viewed_jargon=[],
                clicked_verification=True,
                documents_searched=10,
                documents_matched=1
            ),
            InteractionLogEntry(
                query_id="seed-003",
                timestamp="2026-07-24 10:30:00",
                user_query="ZDJ-200转辙机技术参数",
                confidence_level="medium",
                response_time_ms=1950,
                viewed_details=True,
                viewed_jargon=["转辙机", "ZDJ-200"],
                clicked_verification=False,
                documents_searched=10,
                documents_matched=2
            ),
        ]
        st.session_state["jargon_views"] = {"CBTC": 1, "转辙机": 1, "ZDJ-200": 1}
        st.session_state["verification_clicks"] = 1
        st.session_state["query_count"] = 3
```

**Seed data design principles**:
- 3 records, covering high / medium / low three tiers of confidence
- Includes 1 verification click (trust health = 33%)
- Includes 3 jargon views (Top 5 high-frequency jargon has data)
- Append 2–3 more real queries during the Demo for richer Admin data

---

## 6.8 Alignment Check with UL MSc Requirements

| UL MSc Requirement | How the Portfolio Proves It | Corresponding Deliverable |
|--------------------|------------------------------|---------------------------|
| Significant technical challenge | LLM structured output + Pydantic validation + Streamlit state management + dual expander nesting | Code + PRD Step 4–5 |
| HCI theoretical grounding | Progressive Disclosure + Trust Calibration + Cognitive Load Theory | PRD Step 1–3 + README signal words |
| Prototype implementation | Runnable Streamlit application | Code + Demo video |
| Design reasoning process | 6-step PRD document chain | PRD/ folder |
| Real-world problem | Based on real experience with Huaxin's RAG bidding assistant | PRD Step 1 + README |
| User-centered design | 3 user personas + user journey + requirement prioritization | PRD Step 2 |
| Iterative design | Bug 1/2 fix records + v2 revision records | PRD Step 4 fix records |

---

## 6.9 Time Budget

### Step 7 Coding (re-estimated based on the Must-Work matrix)

| Phase | Original plan (Step 5) | After Must-Work adjustment | Saved |
|-------|------------------------|----------------------------|-------|
| Phase A: Infrastructure | Day 1 | Day 1 (unchanged) | — |
| Phase B: Data layer | Day 2 | Day 2 (simplified matching algorithm) | ~1h |
| Phase C: API layer | Day 3 | Day 3 (unchanged, Plan A already minimal) | — |
| Phase D: Front-end UI | Day 4-5 | Day 4-5 (bug verification is Must-Work) | — |
| Phase E: Admin dashboard | Day 6 | Day 6 (seed data pre-fill simplified) | ~0.5h |
| Phase F: Integration | Day 7 | Day 7 (screenshots + recording + README) | — |

**Conclusion**: The Step 6 Must-Work matrix has little impact on coding time (because the MVP itself is already focused), but the **psychological benefit is huge** — when coding, you know for each feature "why it's written" and "how it's showcased in the Demo," so you won't fall into "Performative Coding."

### Screenshot + recording time budget

| Task | Estimated time |
|------|----------------|
| 4 screenshots (including re-shoots) | 30 minutes |
| 3-minute recording (including re-recording + subtitles) | 1.5 hours |
| README writing | 1 hour |
| PRD document organizing and packaging | 30 minutes |

---

## 6.10 Next Step Preview

After confirming Step 6, proceed to:

**Step 7: Design & Implementation (Coding)**

- Code in Phase A → F order
- Verify each Phase before moving to the next
- Refer to the §6.4 Must-Work vs Mock matrix at any time while coding
- After Phase F, record the video per the §6.3 Demo script + take screenshots per §6.6

---
