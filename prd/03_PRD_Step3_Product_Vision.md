
- Working prototype name: AI Trust Layer
- Phase: Full Product Design Process - Step 3
- Date: 2026-07-24

---

## 3.1 Product Vision Statement

### One-Sentence Vision

> **Enable non-technical users not only to "receive" AI's answers, but also to "understand, trust, and effectively use" them.**

### Full Vision

Currently, enterprise AI systems (especially RAG-based Retrieval-Augmented Generation systems) are technically quite mature — they can retrieve documents, generate answers, and handle complex queries. Yet a technically perfect system is as good as non-existent if users dare not use it, do not know how to use it, or remain uneasy after using it.

**AI Trust Layer is a trust interface layer attached to the output end of a RAG system.** It does not change the AI's "brain" (model capability); instead, it redesigns the "face" of AI output (its presentation), enabling non-technical users to:

1. **See the sources** — know which page of which source document each answer comes from
2. **Perceive confidence** — know whether an answer is a "high-confidence fact" or a "low-confidence speculation"
3. **Understand jargon** — translate the engineers' language into their own working language
4. **Calibrate trust** — know when to use directly and when human verification is required
5. **Close the feedback loop** — let administrators see the system's "trust health" and continuously improve

---

## 3.2 Product Positioning

### Positioning Formula

```
For [non-technical business users] who, when using an [enterprise RAG AI system],
face the problem of [being unable to understand and trust AI output].

AI Trust Layer is a [trust interface layer]
that [attaches to the RAG system's output end and redesigns the presentation of AI answers],
enabling users to [see sources, perceive confidence, understand jargon, calibrate trust].

Unlike [solutions such as ChatGPT / Perplexity / Copilot that optimize "AI answer quality"],
we focus on [optimizing "users' understanding and trust of AI answers"] —
this is the last mile for AI systems to move from "technical success" to "user adoption."
```

### What It Is / What It Is Not

| Dimension | It IS | It IS NOT |
|------|-----------|----------------|
| Product Form | Interface-layer component attached to the RAG output end | A standalone AI assistant product |
| Core Value | Enable users to trust and effectively use AI output | Improve the answer quality of the AI model itself |
| Technological Innovation | Trust presentation design + data contract + progressive disclosure | RAG retrieval algorithm / LLM training |
| Users | Non-technical business users (bid specialists, etc.) | Technical developers / AI researchers |
| Product Positioning | "Translator and trust anchor for AI output" | "AI answer generator" |

### Differentiation Matrix vs. Existing Solutions

| Solution | Optimization Focus | Source Transparency | Confidence Visualization | Jargon Translation | Trust Calibration | Backend Monitoring |
|------|---------|---------|------------|---------|---------|---------|
| ChatGPT (OpenAI) | Answer quality | ❌ | ❌ | ❌ | ❌ | ❌ |
| Perplexity AI | Search provenance | ✅ Basic | ❌ | ❌ | ❌ | ❌ |
| Copilot (Microsoft) | Productivity integration | ⚠️ Partial | ❌ | ❌ | ❌ | ❌ |
| **AI Trust Layer** | **User Trust** | ✅ **Progressive** | ✅ **Three-tier + Alert** | ✅ **Plain Language** | ✅ **Action Guidance** | ✅ **Health Dashboard** |

**Differentiation core**: Everyone wants AI to answer "better"; we want users to "use AI's answers better."

---

## 3.3 Product Design Principles

Five design principles distilled from the requirements analysis in Step 1–2 will guide all subsequent design and implementation decisions:

### Principle 1: Progressive Disclosure

> **Minimal by default, expand on demand.**

Users first see the "answer itself" rather than the "metadata of the answer." Trust widgets such as sources, jargon, and verification suggestions only expand when the user actively requests them. Low confidence is the only exception — it proactively pops up an alert.

- **Source**: Blind Spot 1 fix (Step 2 v2)
- **Constraint**: Default view ≤ 3 visual elements (answer text + confidence label + details button)

### Principle 2: Calibration, Not Replacement

> **Tell users "when to trust," rather than letting them "trust everything or nothing."**

The system does not make decisions on behalf of the user; instead, it provides the basis for decision-making. High confidence = can be used directly; medium confidence = verification suggested; low confidence = for reference only. Each tier comes with clear action guidance.

- **Source**: Blind Spot 2 fix (Step 2 v2)
- **Constraint**: The three-tier confidence must have differentiated presentation, not merely a color change

### Principle 3: Plain Language First

> **Speak in the user's language, not the engineer's language.**

Jargon explanations display the "plain-language version" (plain_language) by default; the formal definition (definition) appears only after expansion. Low-confidence alerts use everyday language rather than technical metrics.

- **Source**: Missing cognitive translation (Step 1)
- **Constraint**: All user-facing copy must pass the "38-year-old bid specialist readability" test

### Principle 4: Structured Data Contract

> **Frontend and backend communicate via JSON Schema, not natural-language guessing.**

All AI output must be structured JSON; the frontend renders by field without NLP parsing. This guarantees determinism and testability of the interface.

- **Source**: Blind Spot 3 fix (Step 2 v2)
- **Constraint**: Backend API responses must pass JSON Schema validation

### Principle 5: Human-AI Co-evolution Loop

> **The product is not a one-way output tool, but a human-AI collaborative iteration system.**

The front-end trust interface helps users make better use of AI; the backend Admin Dashboard lets administrators see the "trust health," driving continuous optimization of the RAG database and jargon glossary. Every user "verification click" is a signal for system improvement.

- **Source**: Activation of secondary user Wang Fang (Step 2 v2)
- **Constraint**: The prototype must include a basic version of the Admin Dashboard

---

## 3.4 Success Metrics

### Two-Tier Metric System

The product must answer two questions simultaneously:
1. **Product level**: Has the trust layer truly solved users' trust problem?
2. **Prototype level**: Does this prototype control scope creep?

### Product-Level Metrics

| Metric Category | Metric Name | Definition | Measurement Method | Target Value |
|---------|---------|------|---------|--------|
| **Trust Calibration** | Trust Accuracy | Adoption rate of high-confidence answers by users vs. verification rate of low-confidence answers | Interaction log analysis | High adoption ≥80%, low verification ≥70% |
| **Cognitive Load Reduction** | First-Interaction Completion Rate | Proportion of new users who, on first use, complete a full query→decision→use without assistance | UAT observation | ≥60% |
| **Jargon Comprehension** | Jargon Query Rate | Frequency with which users hover/click to view jargon explanations | Interaction log | ≥40% on first use, ≤15% after proficiency |
| **System Optimization** | Low-Confidence Trigger Rate | Frequency of AI outputting low-confidence answers | Admin Dashboard | Declining month by month after initial deployment |
| **System Optimization** | Trust Health | Frequency of users clicking "verify source" (higher = lower initial trust) | Admin Dashboard | Declining month by month (trust is being built) |

### Prototype-Level Metrics

| Dimension | Design Philosophy | How This Prototype Demonstrates It |
|------|---------------------|----------------|
| **Problem Discovery** | Ability to extract designable problems from real experience | Step 1 problem definition + four formalized questions |
| **User-Centered Design** | Ability to define personas, journeys, and needs | Step 2 three personas + progressive journey + trinity governance |
| **Design Principles** | Clear design philosophy rather than a pile of features | Step 3 five design principles |
| **Technical Implementation** | Ability to implement design in code (not production-grade, but runnable) | Python + Streamlit + LLM API + JSON Schema |
| **Systems Thinking** | Consideration of non-functional constraints (performance/cost/data format) | Step 2 three NFRs + data contract |
| **Iterative Thinking** | Mechanism for backend monitoring and continuous optimization | F7 Admin Dashboard + trust health |

### Metrics Not Pursued by the Prototype

| Not Pursued | Reason |
|--------|------|
| Production-grade stability | This is a prototype, not a product |
| Large-scale user validation | No conditions for large-scale testing |
| Full ML training | Use API calls to simulate; do not train models ourselves |
| Perfect UI design | Streamlit native components suffice; no Figma needed |

---

## 3.5 MVP Scope Definition (Based on Step 2 v2 Priority Matrix)

### MVP Deliverables List

```
AI Trust Layer MVP
├── Front-end Trust Interface (Li Ming's perspective)
│   ├── F1: Source Annotation (progressive expansion)
│   ├── F2: Confidence Indicator + Low-Confidence Alert
│   ├── F3: Jargon Explanation Layer (progressive expansion)
│   └── F4: Verification Suggestions + Action Links
├── Backend Monitoring Dashboard (Wang Fang's perspective)
│   └── F7: Admin Dashboard (basic version)
│       ├── Trust Health
│       ├── Low-Confidence Trigger Rate
│       └── High-Frequency Missing Jargon
├── Data Layer (Engineer Zhang's constraints)
│   ├── DC: JSON Schema Data Contract
│   ├── N1: Latency Control (progressive loading)
│   └── N2: JSON Format Validation
└── Simulated RAG Backend
    ├── Mock Document Set (5–10 simulated project documents)
    ├── LLM API Calls (structured output)
    └── Confidence Calculation (simulated)
```

### MVP Feature Specification Summary

| Feature | Input | Output | Interaction | Data Contract Field |
|------|------|------|------|------------|
| F1 Source Annotation | sources[] | Document name + page number + match score | Click to expand | sources[] |
| F2 Confidence Indicator | confidence_level | Three-tier label (high/medium/low) | Displayed by default | answer.confidence_level |
| F2b Low-Confidence Alert | confidence_level == "low" | Alert banner + action link | Pops up proactively | verification_advice |
| F3 Jargon Explanation | jargon_glossary[] | Jargon + plain language + definition | Hover/click | jargon_glossary[] |
| F4 Verification Suggestion | verification_advice | Verification field + action link | Expand | verification_advice |
| F7 Admin Dashboard | metadata + interaction log | Three monitoring metrics | Switch to backend | metadata |

### Out of MVP Scope (Explicitly Excluded)

| Excluded Item | Reason | Future Work Placement |
|--------|------|-----------------|
| F5 Format Adaptation (full version) | High complexity, not a core trust feature | V2 iteration |
| F6 Interaction Log (full version) | Requires persistent storage; prototype uses in-memory | V2 iteration |
| F8 Trust Health (full version) | Requires long-term data accumulation | V2 iteration |
| F9 Jargon Heatmap | High data-visualization complexity | V2 iteration |
| N3 Cost Optimization (full version) | Requires real traffic data | Operations phase |
| User authentication/permissions | Not needed for prototype | Productionization phase |
| Multi-language support | Prototype is English-only | Internationalization phase |

---

## 3.6 Technical Architecture Overview

### Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                             │
│                  (Streamlit Web Application)                     │
│                                                                  │
│  ┌──────────────┐          ┌──────────────────────┐            │
│  │ Front-end    │          │ Backend Admin         │            │
│  │ Trust UI     │          │ Dashboard             │            │
│  │ (Li Ming's   │          │ (Wang Fang's          │            │
│  │  view)       │          │  perspective)         │            │
│  │              │          │                       │            │
│  │ F1 Source    │          │ F7 Trust Health        │           │
│  │ F2 Conf.     │          │ F7 Low-Conf. Rate      │           │
│  │ F3 Jargon    │          │ F7 Missing Jargon      │           │
│  │ F4 Verif.    │          │                       │            │
│  └──────┬───────┘          └──────────┬───────────┘            │
│         │                             │                         │
│         └──────────┬──────────────────┘                         │
│                    │                                             │
│         ┌──────────▼──────────┐                                 │
│         │ Streamlit Render     │                                 │
│         │ Engine (Python →     │                                 │
│         │ Web UI)              │                                 │
│         └──────────┬──────────┘                                 │
└────────────────────┼────────────────────────────────────────────┘
                     │
                     │ HTTP (localhost)
                     │
┌────────────────────┼────────────────────────────────────────────┐
│                    ▼           Python Backend                    │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │ JSON Schema  │  │  Query         │  │  Interaction Log  │    │
│  │  Validator    │  │  Controller    │  │  (in-memory)      │    │
│  │ (N2 constraint)│  │               │  │                   │    │
│  └──────┬──────┘  └──────┬───────┘  └───────────────────┘    │
│         │                │                                     │
│         │         ┌──────▼───────┐                             │
│         │         │ Confidence     │                            │
│         │         │ Calculation    │                            │
│         │         │ (simulated/LM) │                            │
│         │         └──────┬───────┘                             │
│         │                │                                     │
│         └────────────────┤                                     │
│                          │                                     │
│                   ┌──────▼────────────────────────┐            │
│                   │      LLM API Call Layer        │            │
│                   │  (OpenAI / Anthropic)          │            │
│                   │  structured output /           │            │
│                   │  function calling              │            │
│                   └──────┬────────────────────────┘            │
│                          │                                     │
│                   ┌──────▼────────────────────────┐            │
│                   │      Mock Document Set         │            │
│                   │  (5–10 simulated project       │            │
│                   │   documents)                   │            │
│                   │  Simulated RAG retrieval       │            │
│                   └───────────────────────────────┘            │
│                                                              │
│    N1 constraint: main answer <2s, details async ≤3s          │
└──────────────────────────────────────────────────────────────┘
```

### Technology Selection Decisions

| Layer | Selection | Rationale | Alternative |
|----|------|---------|---------|
| **Web Framework** | Streamlit | Pure Python, no HTML/CSS/JS needed, suitable for prototypes | Gradio (more ML-demo oriented) |
| **LLM API** | OpenAI API | Supports structured output / function calling | Anthropic Claude API |
| **Data Validation** | Pydantic | Python-native JSON Schema validation | jsonschema library |
| **Confidence Calculation** | LLM self-assessment + rule simulation | No real ML needed at prototype stage | Lightweight classification model |
| **Mock Documents** | Local JSON/Markdown | Simulate project document set | Real vector database |
| **Interaction Log** | Python in-memory dict/list | Prototype needs no persistence | SQLite |

### Data Flow: The Complete Path of a Single Query

```
1. Li Ming enters a query
   "What equipment does the XX project require?"
        │
        ▼
2. Streamlit front-end → Python back-end
   query = "What equipment does the XX project require?"
        │
        ▼
3. Mock RAG retrieval
   Retrieve matching documents from the mock document set
   → return 2–3 document snippets
        │
        ▼
4. LLM API call (structured output)
   Prompt: "Answer the user's question based on the following document
            snippets, and return answer/sources/
            jargon_glossary/verification_advice in JSON format"
   → LLM returns structured JSON
        │
        ▼
5. JSON Schema validation (Pydantic)
   Validate whether the returned JSON conforms to the data contract
   → pass → continue; fail → degraded handling
        │
        ▼
6. Confidence calculation
   Based on retrieval match score + LLM self-assessment
   → confidence_level = "high" / "medium" / "low"
        │
        ▼
7. Progressive rendering (Streamlit)
   Level 0: Answer + confidence label + details button
   → if confidence_level == "low" → append alert banner
        │
        ▼
8. User interaction
   Click "Details" → Level 1: expand sources/jargon/verification suggestions
   Click jargon → hover to show plain-language explanation
   Click action link → jump to mock document page
        │
        ▼
9. Interaction log recording (in-memory)
   Record: query_id, whether details viewed, whether jargon clicked,
           whether verification clicked, confidence tier, response time
        │
        ▼
10. Admin Dashboard update
    Wang Fang switches to backend → sees updated three monitoring metrics
```

### Progressive Loading Strategy (N1 Latency Control)

```python
# Pseudocode: progressive loading strategy

# Step 1: Synchronously return the main answer (<2s)
response = llm_api.call(
    prompt=query,
    structured_output=main_answer_schema,  # only require answer + confidence
    timeout=2.0
)
render_main_answer(response.answer, response.confidence_level)

# Step 2: Asynchronously load details (≤3s total)
if user_clicks_details or confidence_level == "low":
    details = llm_api.call(
        prompt=f"Extract jargon and sources for the following answer: {response.answer}",
        structured_output=details_schema,  # sources + jargon + verification
        timeout=1.5
    )
    render_details(details)

# Step 3: Immediately trigger alert on low confidence (without waiting for user click)
if confidence_level == "low":
    render_alert_banner(verification_advice)
```

---

## 3.7 Risks and Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|------|------|---------|
| Python learning slower than expected | Medium | High | Keep prototype code minimal; prioritize Streamlit native components |
| LLM API structured output unstable | Medium | High | Write fallback logic + Pydantic validation degraded handling |
| Confidence calculation cannot be truly implemented | High | Medium | Use rule simulation (match score threshold) + label as "simulated" |
| Interface lacks "design feel" | Medium | Low | Streamlit + custom CSS is sufficient; prototype focus is on workflow, not aesthetics |
| Scope creep | High | High | Strictly follow MVP list; all new features go to Future Work |

---
