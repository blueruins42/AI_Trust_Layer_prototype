
- Working prototype name: AI Trust Layer
- Phase: Full Product Design Process — Step 2
- Date: 2026-07-23 | Revised: 2026-07-24

---

## Revision Summary (v1 → v2 Changelog)

| # | Blind Spot | Severity | Revision |
|---|-----------|----------|----------|
| 1 | Violated the progressive disclosure principle | P0 | Rewrote the target-state user journey; default view shows only the answer + confidence label, with details expanded on demand |
| 2 | Lacked low-confidence edge-case handling | P0 | Added a low-confidence alert mechanism; defined differentiated presentation strategies for the three confidence tiers |
| 3 | Data contract undefined | P1 | Added JSON Schema defining four fields: answer / sources / confidence_score / jargon_glossary |
| 4 | Secondary user had no operating interface | P1 | Added F7 Admin/Audit Dashboard, activating Wang Fang's "model supervision and system iteration" role |
| 5 | Non-target user did not drive the boundaries | P1 | Added three NFRs: latency ceiling, data contract, compute cost control |

---

## 2.1 User Role Definitions (Personas)

> *Same as v1: Three roles: Li Ming — primary user; Wang Fang — secondary user; Engineer Zhang — non-target user)*

### The Triad of Governance

The problem with v1 was that only Li Ming drove the product functionality. After the v2 correction, each of the three roles drives one product dimension:

```
[Primary user: Li Ming] ──drives──> 【Frontend UX & Trust Interface】 (Frontend / Trust Layer)
                             ▲
                             │
[Secondary user: Wang Fang] ──drives──> 【Admin Dashboard & Data Loop】 (Admin Dashboard / Audit)
                             ▲
                             │
[Anti-user: Engineer Zhang] ──drives──> 【Technical Boundaries & System Performance】 (Backend NFRs / Constraints)
```

| Li Ming only                 | Li Ming + Wang Fang + Engineer Zhang                                                                                                                 |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| A one-way presentation layer | - An industrial-grade product that accounts for the business loop, data iteration, and engineering feasibility      - A Human-AI Co-evolution System |

---

## 2.2 User Journey: Li Ming's Bidding Day

### Current State (No Trust Layer) — A Friction-Filled Journey

> *(Same as v1, not repeated)*

### Target State (With Trust Layer) — Revised: Progressive Disclosure

#### Blind Spot 1 Fix: Why You Can't Display All Trust Widgets at Once

The v1 target state pasted five dimensions (source + confidence + jargon explanation + verification advice + actionable format) around the AI answer simultaneously. This violated the **Progressive Disclosure** principle.

Li Ming is a 38-year-old non-technical bidding specialist. Bombarding him with trust widgets across five dimensions at once on a single interface not only fails to reduce cognitive load, but creates a new **Information Overload**.

**Guiding principles**:
- **Default state**: Only show the AI answer + a concise confidence label (high / medium / low)
- **Interactive expansion**: Details (specific sources, jargon explanation, verification advice) expand only when the user hovers or clicks
- **Exception state**: When confidence is low, proactively pop up an alert (see 2.2b)

#### Revised Target-State Journey

```
Stage 1: Receive the task
  Li Ming receives the bidding document and must submit a quotation proposal within 2 days
  Mindset: Nervous but proficient
  ↓

Stage 2: Open the AI assistant (Trust-Layer-enhanced interface)
  Sees a search box + brief guidance: "Enter the project number or equipment type, and I'll help you look it up"
  ✅ Improvement: Guidance in plain language, no technical jargon
  ↓

Stage 3: Enter query — Default view (Progressive Disclosure Level 0)
  Input: "What equipment does the XX project require?"
  AI returns the answer; the trust layer shows by default only:

  ┌──────────────────────────────────────────────────┐
  │                                                    │
  │  [High confidence]  This project requires 12 units │
  │  of ZDJ-200 switch machines, each with mounting    │
  │  brackets and accompanying cables...               │
  │                                                    │
  │  📊 High  ℹ️ Details  ← clickable to expand, hidden │
  │  by default                                         │
  └──────────────────────────────────────────────────┘

  ✅ Improvement 1: Minimal default view — only the answer + a three-tier label
  ✅ Improvement 2: The "Details" button hints at more information, but does not force Li Ming to read it
  ✅ Improvement 3: Cognitive load minimized — Li Ming reads the answer itself first, then decides whether to dig deeper

  ↓

Stage 3b: Expand on demand (Progressive Disclosure Level 1)

  After Li Ming clicks "Details" or hovers over the confidence label, it expands:

  ┌──────────────────────────────────────────────────┐
  │                                                    │
  │  [High confidence]  This project requires 12 units │
  │  of ZDJ-200 switch machines...                     │
  │                                                    │
  │  ┌─ Expanded ────────────────────────────────────┐ │
  │  │ 📄 Source: XX Project Technical Specification  │ │
  │  │   v3.2 (page 15)                               │ │
  │  │    Matching documents: 3 | Retrieval coverage: │ │
  │  │    87%                                          │ │
  │  │                                                │ │
  │  │ ℹ️ Jargon: "switch machine" = device that      │ │
  │  │    controls railway point switching            │ │
  │  │    "low voltage integration" = overall    │ │
  │  │    contracting of low-voltage electrical systems│ │
  │  │                                                │ │
  │  │ ⚠️ Verification advised: Equipment quantity     │ │
  │  │    requires cross-verification against drawings│ │
  │  └────────────────────────────────────────────────┘ │
  │                                                    │
  │  📊 High  ℹ️ Details  ▲ Collapse                    │
  └──────────────────────────────────────────────────┘

  ✅ Improvement 4: Li Ming actively chooses to view details → higher willingness to accept information
  ✅ Improvement 5: Sources, jargon, and verification advice are presented on demand, not disturbing the default workflow
  ✅ Improvement 6: The "Collapse" button gives Li Ming a sense of control — the information is his tool, not a burden

  ↓

Stage 4: The decision moment
  Option A: Use the high-confidence parts directly + click details to verify the advised parts
  Mindset: Confident, in control
  ✅ Li Ming chooses A → the AI system truly creates value
  ↓

Stage 5: Generate the quotation
  Based on the AI answer + trust-layer guidance, completes the quotation efficiently
  Mindset: Will use this tool again next time
```

### 2.2b Edge Case: Low-Confidence Alert Mechanism (Blind Spot 2 Fix)

#### Problem Diagnosis

The v1 user journey only showed the perfect scenario where the AI gives "high confidence." But the core of design rationale is solving **"uncertainty."** If the confidence of the data retrieved by the AI is extremely low (say only 30%), how should the system present it to Li Ming?

#### Three-Tier Differentiated Confidence Presentation Strategy

| Confidence tier | Score range | Visual treatment | Interaction behavior | User guidance text |
|-----------------|-------------|------------------|----------------------|--------------------|
| **High** | ≥ 75% | Green label, no extra prompt | Details expandable to view sources | None (trust by default) |
| **Medium** | 50%-74% | Yellow label, slight prompt | Details half-expanded by default, showing verification advice | "This information is partially matched; please verify the source" |
| **Low** | < 50% | Red label + alert banner | Alert banner is non-ignorable and must be read | See full guidance text below |

#### Low-Confidence Scenario User Journey

```
Stage 3: Enter query — Low-confidence exception state

  Li Ming inputs: "What localized solution is used for the signaling system on the YY line project?"
  After retrieval, the AI finds no fully matching document in the database...

  ┌──────────────────────────────────────────────────┐
  │ ⚠️ Warning                                        │
  │                                                    │
  │ No fully matching specification was found in the   │
  │ database. This answer is for reference only;       │
  │ please be sure to click below to manually verify   │
  │ against the source document.                       │
  │                                                    │
  │ [View closest document, page 22 →]                 │
  └──────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────┐
  │                                                    │
  │  [Low confidence]  Based on existing materials, the│
  │  YY line may adopt...                              │
  │  (the following content is AI inference, not a     │
  │  direct quotation from the document)               │
  │                                                    │
  │  📊 Low  ⚠️ Verification needed  ℹ️ Details        │
  └──────────────────────────────────────────────────┘

  ✅ Not a cold, hard score, but plain-language guidance
  ✅ Clearly tells Li Ming "why confidence is low" (no full match found)
  ✅ Directly gives an action suggestion (click to view source document page 22)
  ✅ The four words "for reference only" = the core of trust calibration — neither "don't use it" nor "use it with confidence"
```

#### Why This Is True Trust Calibration

| Wrong approach | Correct approach (this product) |
|----------------|----------------------------------|
| Show "Confidence: 30%" and let the user judge | Show "No full match found; please verify manually" |
| Low and high confidence use the same presentation | Low confidence triggers an alert banner, visually distinct |
| Only tells the user "uncertain," not "what to do" | Also gives an action suggestion (view source document page X) |
| Trust is binary (trust all / trust none) | Trust is calibrated (high = usable, medium = use after checking, low = reference only) |

---

## 2.3 Core Requirements Refinement (Revised)

### From User Pain Points to Product Features — Complete Feature Matrix

#### Features Driven by Li Ming (Frontend Trust Interface)

| ID | User pain point | User need | Product feature | Priority | v2 revision |
|----|-----------------|-----------|-----------------|----------|-------------|
| F1 | "Don't know if the AI answer is correct" | Source traceability | **Source annotation** — each AI answer annotated with its source document | P0 | Changed to expand-on-demand (progressive disclosure) |
| F2 | "Don't know which parts can be used directly" | Confidence visualization | **Confidence indicator** — three-tier label (high/medium/low) + low-confidence alert | P0 | Added low-confidence alert mechanism |
| F3 | "Can't understand the jargon" | Cognitive translation | **Jargon explanation layer** — technical term hover explanation / inline translation | P1 | Changed to expand-on-demand (progressive disclosure) |
| F4 | "Don't know when to verify" | Trust calibration guidance | **Verification advice** — flag content requiring manual verification + action suggestion | P1 | Added "action suggestion" (not just flagging, but telling the user what to do) |
| F5 | "AI output can't be used directly" | Actionable format | **Format adaptation** — output converted to the user's working format (table/template) | P2 | No change |
| F6 | "Who is responsible if something goes wrong" | Accountability | **Interaction log** — records the history of user-AI interactions | P2 | No change |

#### Features Driven by Wang Fang (Backend Data Loop) — Added in v2

| ID | User pain point | User need | Product feature | Priority |
|----|-----------------|-----------|-----------------|----------|
| F7 | "Translation work done manually cannot be systematized" | Model supervision and system iteration | **Admin/Audit Dashboard** — administrator backend data dashboard | P1 |
| F8 | "Feedback collection is one-off, with no accumulation" | Data-driven continuous improvement | **Trust health monitoring** — counts how often users click "verify source," measuring initial trust | P2 |
| F9 | "The trust mechanism only exists in training, not in the product" | High-frequency issue identification | **Jargon heatmap** — counts the technical terms users hover to view most, driving glossary updates | P2 |

##### F7 Admin/Audit Dashboard Feature Detail

```
┌─────────────────────────────────────────────────────────┐
│  Admin View (admin only)                       [Front]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Today's Overview                                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Trust Health │ │ Low-Conf Rate│ │ Top Jargon   │    │
│  │              │ │              │ │              │    │
│  │    73%       │ │    12 times  │ │  1. low-volt.│    │
│  │  (verify     │ │ (triggered   │ │     integrat.│    │
│  │   click rate)│ │  today)      │ │  2. switch   │    │
│  │              │ │              │ │     machine  │    │
│  │              │ │              │ │  3. RAG      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                         │
│  Trust Health = frequency of users clicking "verify     │
│  source"                                                │
│  Higher click rate → lower initial trust → need to      │
│  optimize source annotation method                      │
│                                                         │
│  Low-Conf Rate → counts how often AI output is          │
│  low-confidence                                         │
│  High trigger rate → insufficient RAG database coverage │
│  → documents need to be supplemented                     │
│                                                         │
│  Top Jargon → terms users most often view explanations  │
│  for                                                     │
│  → update directly into the preset glossary next time,  │
│  reducing user query count                              │
└─────────────────────────────────────────────────────────┘
```

**The significance of this feature**: The product is upgraded from a simple "conversation trust interface" into a complete "human-AI co-evolution system." Wang Fang is no longer a coordinator manually collecting feedback, but a product manager who drives continuous system optimization through the data dashboard.

#### Non-Functional Requirements Driven by Engineer Zhang (Technical Boundaries) — Added in v2

See Section 2.7 below.

---

## 2.4 Competitor & Existing Solution Analysis

> *(Same as v1, not repeated. Core conclusion: existing solutions all optimize "AI answer quality"; no one systematically solves "users' understanding of and trust in AI answers.")*

---

## 2.5 Data Contract — Added in v2 (Blind Spot 3 Fix)

### Problem Diagnosis

The Python tech stack is Streamlit + LLM API. But how does Streamlit know "which sentence is jargon" or "what the confidence is"? v1 wrote a bunch of advanced features but never defined the output format of the backend API.

### JSON Data Contract Definition

The output of the trust-layer backend API must be the following structured JSON data:

```json
{
  "answer": {
    "text": "This project requires 12 ZDJ-200 point machines, each including mounting brackets and accompanying cables.",
    "confidence_score": 0.87,
    "confidence_level": "high",
    "is_inferred": false
  },
  "sources": [
    {
      "document_name": "XX Project Signalling Technical Specification v3.2",
      "page_number": 15,
      "match_score": 0.92,
      "excerpt": "The project signalling system adopts ZDJ-200 electric point machines..."
    },
    {
      "document_name": "XX Project Signalling System Design Drawing",
      "page_number": 8,
      "match_score": 0.78,
      "excerpt": "Point machine layout drawing: 12 turnouts..."
    }
  ],
  "jargon_glossary": [
    {
      "term": "point machine",
      "definition": "Electro-mechanical equipment used to operate railway points (turnouts)",
      "plain_language": "The switch that lets trains change from one track to another"
    },
    {
      "term": "railway signalling and telecommunications (S&T) systems integration",
      "definition": "Integrated engineering of railway low-current systems, including signalling, telecommunications, CCTV, and supervision systems",
      "plain_language": "Bundling communication, signalling, monitoring, and other low-voltage railway systems into one integrated package"
    }
  ],
  "verification_advice": {
    "needs_verification": true,
    "fields_to_check": ["Equipment quantity must be cross-verified against the design drawings"],
    "action_link": {
      "text": "Go to drawing page 8",
      "document": "XX Project Signalling System Design Drawing",
      "page": 8
    }
  },
  "metadata": {
    "query_id": "q_20260724_001",
    "timestamp": "2026-07-24T10:30:00Z",
    "response_time_ms": 1850,
    "model_used": "gpt-4-turbo",
    "documents_searched": 47,
    "documents_matched": 3
  }
}
```

### Field Description

| Field | Type | Required | Description | Driving product feature |
|-------|------|----------|-------------|-------------------------|
| `answer.text` | string | ✅ | AI-generated answer text | F1, F2 display body |
| `answer.confidence_score` | float | ✅ | 0.0-1.0 confidence score | F2 confidence indicator |
| `answer.confidence_level` | enum | ✅ | "high" / "medium" / "low" | F2 three-tier label + low-confidence alert |
| `answer.is_inferred` | boolean | ✅ | Whether it is AI inference (not a direct document quotation) | F2 distinguishes "quotation" from "inference" |
| `sources[]` | array | ✅ | List of source documents | F1 source annotation |
| `sources[].document_name` | string | ✅ | Document name | F1 display |
| `sources[].page_number` | int | ✅ | Page number | F1 click-to-jump |
| `sources[].match_score` | float | ✅ | Retrieval match score | F1 source ordering |
| `sources[].excerpt` | string | ❌ | Original excerpt | F1 hover preview |
| `jargon_glossary[]` | array | ❌ | List of jargon explanations | F3 jargon explanation layer |
| `jargon_glossary[].term` | string | ❌ | Technical term | F3 mark explainable word |
| `jargon_glossary[].definition` | string | ❌ | Formal definition | F3 displayed on expand |
| `jargon_glossary[].plain_language` | string | ❌ | Plain-language explanation | F3 displayed by default (Li Ming-friendly) |
| `verification_advice` | object | ❌ | Verification advice | F4 verification advice |
| `verification_advice.needs_verification` | boolean | ❌ | Whether manual verification is needed | F4 whether to show advice |
| `verification_advice.fields_to_check[]` | array | ❌ | Specific fields to verify | F4 verification content |
| `verification_advice.action_link` | object | ❌ | Action suggestion link | F4 one-click jump |
| `metadata` | object | ✅ | Query metadata | F7 Admin Dashboard |

### Why This Data Contract Is Key

1. **Frontend parseable**: Streamlit directly `json.loads()` and renders by field — no NLP parsing needed
2. **Backend extensible**: Future fields (e.g., `alternative_answers`) can be added without breaking the frontend
3. **Testable**: During UAT, can check whether the JSON contains all required fields

---

## 2.6 Non-Functional Requirements (NFR) — Added in v2 (Driven by Engineer Zhang)

### Problem Diagnosis

Once Engineer Zhang was labeled a "non-target user," he was never dealt with again. But the real role of the non-target user (Anti-Persona) in a PRD is to **"draw the system's physical boundaries (System Boundaries)"** — preventing the product manager from proposing fantasy features that "sound beautiful but the engineer simply cannot build" (Scope Creep).

Engineer Zhang is the technical constraint wall.

### NFR-1: Response Latency Limit

| Dimension                      | Specification                                                                                                                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Constraint**                 | Total system response time ≤ 3 seconds (from user submitting query to trust-layer interface render complete)                                                                   |
| **Engineer Zhang's objection** | "You want to both generate the answer, compute confidence, AND extract jargon! If you use too complex a model, the API response takes 15 seconds and the server will explode!" |
| **Technical solution**         | If LLM jargon extraction is too slow, use async loading or a preset local dictionary                                                                                           |
| **Implementation strategy**    | Main answer returned synchronously (<2s); jargon explanation / source details loaded asynchronously (deferrable to after 3s)                                                   |
| **Portfolio impact**           | Prototype demo must show "progressive loading" — answer first, details later                                                                                                   |

### NFR-2: Data Contract

| Dimension                      | Specification                                                                                   |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| **Constraint**                 | API return must be the structured JSON defined in Section 2.5 above, with limited field lengths |
| **Engineer Zhang's objection** | "Don't talk to me about feelings! Tell me exactly what JSON format the backend should pass!"    |
| **Technical solution**         | LLM output uses structured output / function calling to ensure JSON format                      |
| **Field limits**               | `answer.text` ≤ 2000 chars; `sources[]` ≤ 5 entries; `jargon_glossary[]` ≤ 10 entries           |
| **Portfolio impact**           | Prototype code must include JSON schema validation logic                                        |

### NFR-3: Compute & Cost Control

| Dimension                      | Specification                                                                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **Constraint**                 | Limit each user's daily query count + frontend offline caching                                                                   |
| **Engineer Zhang's objection** | "If every query calls GPT-4 three times for prompt validation, the company's API bill will crash!"                               |
| **Technical solution**         | Cache identical queries for 1 hour; use a lightweight model (e.g., GPT-3.5) for confidence calculation instead of the main model |
| **Portfolio impact**           | Prototype shows cache hit-rate metric; does not show full cost optimization (as future work)                                     |

### NFR Summary Table

| NFR | Constraint | Implementation strategy | Shown in Portfolio |
|-----|------------|-------------------------|--------------------|
| Latency | ≤ 3 seconds | Main answer sync, details async | ✅ Progressive loading |
| Data format | JSON Schema | Structured output | ✅ JSON validation logic |
| Cost | Daily query cap + cache | Lightweight model + 1h cache | ⚠️ Cache hit rate |

---

## 2.7 Revised Requirement Priority Overview

### Complete Feature Priority Matrix (v2)

| Priority | Feature ID | Feature name | Driving role | v1/v2 status |
|----------|------------|--------------|--------------|--------------|
| **P0** | F1 | Source annotation (progressive expand) | Li Ming | v1→v2 revised to expand-on-demand |
| **P0** | F2 | Confidence indicator + low-confidence alert | Li Ming | v1→v2 added alert mechanism |
| **P1** | F3 | Jargon explanation layer (progressive expand) | Li Ming | v1→v2 revised to expand-on-demand |
| **P1** | F4 | Verification advice + action advice | Li Ming | v1→v2 added action link |
| **P1** | F7 | Admin/Audit Dashboard | Wang Fang | v2 added |
| **P1** | DC | Data contract (JSON Schema) | Engineer Zhang | v2 added |
| **P2** | F5 | Format adaptation | Li Ming | No change |
| **P2** | F6 | Interaction log | Li Ming | No change |
| **P2** | F8 | Trust health monitoring | Wang Fang | v2 added |
| **P2** | F9 | Jargon heatmap | Wang Fang | v2 added |
| **NFR** | N1-N3 | Latency / format / cost constraints | Engineer Zhang | v2 added |

### Portfolio Prototype Scope Definition (MVP)

| In prototype | Not in prototype (future work) |
|--------------|-------------------------------|
| F1 Source annotation (progressive expand) | F5 Format adaptation (full version) |
| F2 Confidence indicator + low-confidence alert | F6 Interaction log (full version) |
| F3 Jargon explanation layer (progressive expand) | F9 Jargon heatmap |
| F4 Verification advice + action advice | N3 Cost optimization (full version) |
| F7 Admin Dashboard (basic version) | |
| DC Data contract (JSON Schema) | |
| N1 Latency control (progressive loading) | |
| N2 JSON format validation | |


