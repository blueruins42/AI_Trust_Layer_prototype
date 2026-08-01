
- Working prototype name: AI Trust Layer
- Phase: Full Product Design Process - Step 4
- Date: 2026-07-28
- Upstream inputs: Step 1 Problem Definition, Step 2 v2 User Personas + Data Contract + NFR, Step 3 Product Vision + MVP Scope

---

## 4.0 Document Structure

This specification defines the following for each function in the MVP:

- **User Story**: As a / I want to / So that
- **Input Specification**: What data the function requires
- **Output Specification**: What the function presents to the user
- **Interaction Flow**: Detailed state transitions and user operation steps
- **Exception Handling**: Boundary scenarios and degradation strategies
- **Acceptance Criteria**: Testable pass conditions (Given/When/Then)
- **Data Contract Mapping**: Which JSON Schema fields it corresponds to
- **Streamlit Component Mapping**: Which Streamlit native components implement it

---

## 4.1 Global UI State Machine

All feature interactions run within a unified state machine. We first define the global states, then expand each feature individually.

### State Definitions

```
                         ┌──────────┐
                         │  IDLE    │ ← Initial state, shows search box + guidance prompt
                         └────┬─────┘
                              │ User enters a query and submits
                              ▼
                    ┌─────────────────┐
                    │  LOADING        │ ← Shows loading animation
                    │  (progressive loading) │
                    └────────┬────────┘
                             │ Main answer returned (<2s)
                             ▼
               ┌─────────────────────────┐
               │  ANSWER_DISPLAYED        │ ← Level 0: answer + confidence label + details button
               │  (default view)          │
               └──┬──────┬──────┬─────────┘
                  │      │      │
     Click "Details" │    │      │ Click "Collapse"
                  ▼      │      ▼
    ┌──────────────┐    │    ┌──────────────┐
    │  EXPANDED    │    │    │  (back to default) │
    │  Level 1     │    │    └──────────────┘
    │  (details expanded) │  │
    └──────────────┘    │
                        │ confidence_level == "low"
                        ▼
               ┌─────────────────────────┐
               │  ALERT_DISPLAYED         │ ← Alert banner (pops up proactively, not waiting for a click)
               │  (low-confidence exception) │
               └────────┬────────────────┘
                        │ User reads and clicks action link
                        ▼
               ┌─────────────────────────┐
               │  DOCUMENT_VIEW           │ ← Jumps to Mock document page
               │  (document view)         │
               └─────────────────────────┘
```

### State Transition Rules

| Current State | Trigger Event | Target State | Notes |
|---------|---------|---------|------|
| IDLE | User submits query | LOADING | Clear previous results |
| LOADING | Main answer returned successfully | ANSWER_DISPLAYED | Render Level 0 |
| LOADING | Main answer returned failure | IDLE + error message | Degradation handling |
| LOADING | Timeout (>3s) | IDLE + timeout message | Degradation handling |
| ANSWER_DISPLAYED | User clicks "Details" | EXPANDED | Render Level 1 |
| ANSWER_DISPLAYED | confidence_level == "low" | ANSWER_DISPLAYED + ALERT | Alert overlays the default view |
| EXPANDED | User clicks "Collapse" | ANSWER_DISPLAYED | Back to Level 0 |
| ALERT_DISPLAYED | User clicks action link | DOCUMENT_VIEW | Jump to document |
| Any state | User submits new query | LOADING | Clear current results |
| Any state | User clicks "Switch to Admin" | ADMIN_DASHBOARD | Wang Fang's perspective |

> **⚠️ Streamlit Implementation Note**: The `ANSWER_DISPLAYED ↔ EXPANDED` expand/collapse transitions in the table above **do not require manual state management**. Streamlit's `st.expander` is a persistent-state control; its expand/collapse state is automatically preserved across script reruns. Using `st.expander` is sufficient — **it is strictly forbidden** to use `st.button` to control expand/collapse (`st.button` is a transient trigger that only returns True on the rerun of the click, and immediately returns False on the next rerun, which would cause the details area to disappear when the user operates internal buttons). See Section 4.8 for implementation details.

---

## 4.2 F1: Source Citation

### User Story

> **As** Li Ming (tender specialist),
> **I want** to know which document and which page a piece of AI-generated information comes from,
> **So that** I can verify its accuracy and cite the original source in the tender document.

### Input Specification

| Field | Source | Type | Description |
|------|------|------|------|
| `sources[]` | LLM API return | array | List of source documents, ≤5 entries |
| `sources[].document_name` | LLM API return | string | Document name |
| `sources[].page_number` | LLM API return | int | Page number |
| `sources[].match_score` | LLM API return | float | 0.0-1.0 retrieval match score |
| `sources[].excerpt` | LLM API return | string (optional) | Original excerpt |

### Output Specification

**Level 0 (default view)**: Source information is not shown; only a collapsed "📄 Details" expander hints at the presence of sources.

**Level 1 (expanded view)**:

```
┌─ Sources (3 matching documents) ────────────────────────────┐
│                                                    │
│  📄 XX Project Technical Specification v3.2 · Page 15        │
│     Match: 92% · [View Excerpt ▾]                            │
│                                                    │
│  📄 XX Project Signaling System Design Diagram · Page 8     │
│     Match: 78% · [View Excerpt ▾]                            │
│                                                    │
│  📄 Rail Transit Equipment List · Page 22                    │
│     Match: 65% · [View Excerpt ▾]                            │
│                                                    │
└────────────────────────────────────────────────────┘
```

- Sources are sorted in descending order by `match_score`
- Each source shows: document name + page number + match score percentage
- "View Excerpt" expands the `excerpt` original text snippet (if present) when clicked

### Interaction Flow

1. User sees the source list in the EXPANDED state
2. The list is sorted in descending order by match_score
3. User clicks "View Excerpt" → expands the original text snippet (inline, no new window)
4. User clicks the document name → transitions to DOCUMENT_VIEW state, displaying that page's content
5. User clicks "Collapse" → returns to ANSWER_DISPLAYED state

### Exception Handling

| Exception Scenario | Handling Method |
|---------|---------|
| `sources[]` is an empty array | Show "This answer does not cite any specific document" + do not show the source block |
| `sources[].excerpt` is missing | Do not show the "View Excerpt" button |
| `sources[]` exceeds 5 entries | Show only the first 5 entries (sorted descending by match_score) |
| `page_number` is 0 or negative | Show "Page number not annotated" |

### Acceptance Criteria

```gherkin
Given AI returned an answer containing 3 sources
When the user clicks "Details" to expand
Then the source list is displayed in descending order by match_score showing 3 sources
And each source shows the document name, page number, and match score percentage
And the source with the highest match score is listed first

Given AI returned an answer with no sources (sources = [])
When the user clicks "Details" to expand
Then the source block shows "This answer does not cite any specific document"
And the source list is not displayed

Given the source list contains one source with an excerpt
When the user clicks "View Excerpt" for that source
Then the original text snippet expands inline below the source entry
```

### Streamlit Component Mapping

| UI Element | Streamlit Component |
|---------|---------------|
| Source block container | `st.expander` (expanded=True) |
| Source list | `st.markdown` + loop rendering |
| Excerpt expansion | `st.expander` (nested, expanded=False) |
| Document name navigation | `st.button` + `st.session_state` state switch |

---

## 4.3 F2: Confidence Indicator + Low-Confidence Alert

### User Story

> **As** Li Ming (tender specialist),
> **I want** to tell at a glance how trustworthy this AI answer is,
> **So that** I know whether to use it directly or to verify it manually.

### Sub-function Breakdown

F2 contains two sub-functions:
- **F2a: Confidence Indicator** — three-tier label, displayed by default (Level 0)
- **F2b: Low-Confidence Alert** — alert banner that pops up proactively on low confidence

### F2a: Confidence Indicator

#### Input Specification

| Field | Type | Description |
|------|------|------|
| `answer.confidence_score` | float | 0.0-1.0 raw score |
| `answer.confidence_level` | enum | "high" / "medium" / "low" |
| `answer.is_inferred` | boolean | Whether it is AI-inferred |

#### Output Specification (three-tier differentiation)

| Tier | Score Range | Visual Representation | Label Text | Additional Behavior |
|------|---------|---------|---------|---------|
| High | ≥ 0.75 | 🟢 Green label | "High confidence" | None |
| Medium | 0.50-0.74 | 🟡 Yellow label | "Partial match · verification recommended" | Source expander expanded + jargon expander collapsed |
| Low | < 0.50 | 🔴 Red label + alert banner | "Low confidence · manual verification required" | Triggers F2b alert |

When `is_inferred == true`, append a small "(AI-inferred)" marker after the label.

#### Interaction Flow

1. After the main answer is returned, the system reads `confidence_level`
2. Renders the corresponding colored label (green/yellow/red)
3. If `confidence_level == "medium"` → set source expander `expanded=True`, jargon expander `expanded=False` (physically achieving "sources visible, jargon expand on demand")
4. If `confidence_level == "low"` → render the alert banner above the answer (F2b)
5. The label is always displayed in the Level 0 default view (no user click required)

### F2b: Low-Confidence Alert

#### Input Specification

| Field | Type | Description |
|------|------|------|
| `answer.confidence_level` | enum | Trigger condition: == "low" |
| `verification_advice.needs_verification` | boolean | Whether verification is needed |
| `verification_advice.action_link` | object | Action link information |

#### Output Specification

```
┌─ ⚠️ Warning ─────────────────────────────────────────┐
│                                                    │
│  No fully matching specification was found in the database.     │
│  This answer is for reference only; please click below to manually  │
│  verify against the original document.                    │
│                                                    │
│  [📄 View closest document, Page 22 →]                      │
│                                                    │
└────────────────────────────────────────────────────┘
```

- Alert banner color: light red background (#ffe0e0) + red border
- The alert cannot be closed/ignored — it must remain displayed above the answer
- The action link text comes from `verification_advice.action_link.text`
- Clicking the action link jumps to DOCUMENT_VIEW

#### Interaction Flow

1. Main answer returned, `confidence_level == "low"`
2. Render the alert banner above the answer text
3. User reads the alert content
4. User clicks the action link → jumps to DOCUMENT_VIEW
5. The alert banner persists, and does not disappear even if the user expands/collapses the details

#### Exception Handling

| Exception Scenario | Handling Method |
|---------|---------|
| `confidence_level == "low"` but `verification_advice` is missing | Show a generic alert: "This answer has low confidence; manual verification is recommended" |
| `action_link` is missing | Alert shows no link, only the warning text |
| `confidence_score` and `confidence_level` are inconsistent | Use `confidence_level` as the source of truth (the LLM-returned enum value takes priority) |

### Acceptance Criteria

```gherkin
Given AI returned confidence_level of "high"
When the main answer finishes rendering
Then display the green "High confidence" label
And do not display the alert banner
And the details block is collapsed by default

Given AI returned confidence_level of "medium"
When the main answer finishes rendering
Then display the yellow "Partial match · verification recommended" label
And do not display the alert banner
And the source expander is expanded by default (expanded=True)
And the jargon expander is collapsed by default (expanded=False)

Given AI returned confidence_level of "low"
When the main answer finishes rendering
Then display the red "Low confidence · manual verification required" label
And display the red alert banner above the answer
And the alert banner contains an action link
And the alert banner cannot be closed

Given AI returned is_inferred of true
When the confidence label renders
Then a small "(AI-inferred)" marker is shown after the label
```

### Streamlit Component Mapping

| UI Element | Streamlit Component |
|---------|---------------|
| High-confidence label | `st.success("🟢 High confidence")` |
| Medium-confidence label | `st.warning("🟡 Partial match · verification recommended")` |
| Low-confidence label | `st.error("🔴 Low confidence · manual verification required")` |
| AI-inferred marker | `st.caption("(AI-inferred)")` |
| Alert banner | `st.error()` with custom markdown |
| Action link | `st.button()` + `st.session_state` navigation (one-time action, not expand/collapse) |
| Medium confidence · source expanded | `st.expander("📄 Sources", expanded=True)` — separate from jargon |
| Medium confidence · jargon collapsed | `st.expander("ℹ️ Jargon Explanation", expanded=False)` — independent control |

> **⚠️ Bug Fix Note**: The original draft said "details half-expanded by default," but Streamlit's `st.expander` is a binary control (`expanded=True/False`) with no "half-expanded" state. Corrected to the **dual-expander strategy**: on medium confidence, source expander `expanded=True` + jargon expander `expanded=False`, physically achieving "sources visible, jargon expand on demand."

---

## 4.4 F3: Jargon Glossary

### User Story

> **As** Li Ming (tender specialist),
> **I want** unfamiliar technical jargon to be automatically translated into plain language,
> **So that** I can understand the AI answer without having to ask an engineer.

### Input Specification

| Field | Type | Description |
|------|------|------|
| `jargon_glossary[]` | array | Jargon list, ≤10 entries |
| `jargon_glossary[].term` | string | Technical term |
| `jargon_glossary[].definition` | string | Formal definition |
| `jargon_glossary[].plain_language` | string | Plain-language explanation |

### Output Specification

**Term markers in the answer text**:

When `jargon_glossary[].term` appears in the AI answer text, it is automatically marked as an interactive term link (underline + different color).

**Jargon block in the Level 1 expanded view**:

```
┌─ Jargon Explanation ───────────────────────────────────────┐
│                                                    │
│  「switch machine」                                      │
│  💬 The switch that moves trains onto a different track    │
│  📖 Mechanical equipment that controls railway point switching  [Expand Definition] │
│                                                    │
│  「low-voltage integration」                              │
│  💬 Bundling communication, signaling, monitoring and other low-voltage systems together │
│  📖 Integrated engineering of low-voltage electrical systems  [Expand Definition] │
│                                                    │
└────────────────────────────────────────────────────┘
```

- **Display by default** `plain_language` (plain words), marked with 💬
- **Expand on demand** `definition` (formal definition), marked with 📖, requires clicking "Expand Definition"
- Follows Design Principle 3: plain language first

### Interaction Flow

1. User sees the jargon explanation block in the EXPANDED state
2. Each term displays `plain_language` by default
3. User clicks "Expand Definition" → displays `definition`
4. User clicks "Collapse Definition" → returns to showing only `plain_language`
5. **Interaction log**: records which terms the user viewed (for use by F7 Admin Dashboard)

### Exception Handling

| Exception Scenario | Handling Method |
|---------|---------|
| `jargon_glossary[]` is empty | Do not display the jargon block |
| `plain_language` is missing | Show only `definition` |
| `definition` is missing | Do not show the "Expand Definition" button |
| `term` does not appear in the answer text | Still shown in the jargon block, but no text marking |
| More than 10 terms | Show only the first 10 |

### Acceptance Criteria

```gherkin
Given the AI answer contains the term "switch machine" and it exists in jargon_glossary
When the user expands details (Level 1)
Then the jargon block shows "switch machine"
And displays by default the plain language "The switch that moves trains onto a different track"
And the "Expand Definition" button is clickable

Given the user clicks "Expand Definition"
Then display the formal definition "Mechanical equipment that controls railway point switching"
And the button text changes to "Collapse Definition"

Given jargon_glossary is an empty array
When the user expands details
Then the jargon explanation block is not displayed

Given the user viewed the explanation of the term "switch machine"
Then the interaction log records this viewing behavior
And F7 Admin Dashboard's high-frequency missing-jargon counter +1
```

### Streamlit Component Mapping

| UI Element | Streamlit Component |
|---------|---------------|
| Jargon block container | `st.expander("Jargon Explanation", expanded=True)` |
| Single term | `st.markdown` + `st.columns` layout |
| Plain language | `st.markdown("💬 {plain_language}")` |
| Expand definition | `st.expander("📖 Formal Definition", expanded=False)` |
| Term view log | `st.session_state["jargon_views"]` counter |

---

## 4.5 F4: Verification Advice + Action Link

### User Story

> **As** Li Ming (tender specialist),
> **I want** the system to clearly tell me which content needs manual verification and how to verify it,
> **So that** I won't make mistakes by blindly trusting the AI.

### Input Specification

| Field | Type | Description |
|------|------|------|
| `verification_advice.needs_verification` | boolean | Whether verification is needed |
| `verification_advice.fields_to_check[]` | array | Specific fields to verify |
| `verification_advice.action_link.text` | string | Link display text |
| `verification_advice.action_link.document` | string | Target document name |
| `verification_advice.action_link.page` | int | Target page number |

### Output Specification

**Verification advice block in the Level 1 expanded view**:

```
┌─ ⚠️ Verification Advice ────────────────────────────────────┐
│                                                    │
│  The following content is recommended for manual verification:       │
│                                                    │
│  • Equipment quantities require cross-validation against drawings  │
│  • Cable specifications require checking against the latest national standard │
│                                                    │
│  [📄 View drawing, Page 8 →]                               │
│                                                    │
└────────────────────────────────────────────────────┘
```

- Shown only when `needs_verification == true`
- `fields_to_check[]` is presented as an unordered list
- The action link is presented as a button; clicking jumps to DOCUMENT_VIEW
- If `confidence_level == "low"`, the verification advice is already shown in the alert banner, so it is not repeated here

### Interaction Flow

1. User sees the verification advice block in the EXPANDED state (if present)
2. User reads the list of fields to verify
3. User clicks the action link → jumps to DOCUMENT_VIEW
4. **Interaction log**: records whether the user clicked the verification advice (for F7 trust-health calculation)

### Exception Handling

| Exception Scenario | Handling Method |
|---------|---------|
| `needs_verification == false` | Do not display the verification advice block |
| `fields_to_check[]` is empty | Do not display the list, only show the action link (if any) |
| `action_link` is missing | Show only the verification field list, no link |
| `confidence_level == "low"` | The alert banner already contains verification info; show "See alert above" here |

### Acceptance Criteria

```gherkin
Given verification_advice.needs_verification is true
And fields_to_check contains 2 fields
When the user expands details
Then display the verification advice block
And display the 2 fields to verify
And display the action link button

Given verification_advice.needs_verification is false
When the user expands details
Then do not display the verification advice block

Given confidence_level is "low"
When the user expands details
Then the verification advice block shows "See alert above"
And the action link is not repeated

Given the user clicked the action link
Then jump to the DOCUMENT_VIEW state
And the interaction log records a "verification click" event
And F7 Admin Dashboard's trust-health calculation is updated
```

### Streamlit Component Mapping

| UI Element | Streamlit Component |
|---------|---------------|
| Verification advice block | `st.expander("⚠️ Verification Advice", expanded=True)` |
| Field list | `st.markdown` + unordered list |
| Action link | `st.button("📄 {action_link.text}")` |
| Verification click log | `st.session_state["verification_clicks"]` counter |

---

## 4.6 F7: Admin Dashboard (Basic Version)

### User Story

> **As** Wang Fang (AI product coordinator),
> **I want** to see the key metrics of how the system is running,
> **So that** I can identify data coverage gaps and user trust trends, driving continuous system optimization.

### Input Specification

| Data Source | Field | Description |
|---------|------|------|
| Interaction log | Total query count | Number of queries in the current session |
| Interaction log | Verification click count | Number of times the user clicked "verify source / action link" |
| Interaction log | Low-confidence trigger count | Number of queries where confidence_level == "low" |
| Interaction log | Jargon view records | Number of times each term was viewed |
| metadata | response_time_ms | Response time per query |

### Output Specification

**Admin Dashboard interface**:

```
┌─ Admin Dashboard · System Monitoring ──────  [Switch to Frontend] ─┐
│                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│  │ Trust Health │ │ Low-Conf Rate │ │ Total Qs │ │
│  │              │ │              │ │          │ │
│  │    73%       │ │    3/10      │ │   10     │ │
│  │ (verif. click rate) │ │   (30%)      │ │          │ │
│  │              │ │              │ │          │ │
│  │ lower=better trust │ │ higher=low coverage │ │          │ │
│  └──────────────┘ └──────────────┘ └──────────┘ │
│                                                  │
│  ┌─ Top 5 Most-Viewed Jargon ────────────────────────┐ │
│  │  1. low-voltage integration  · viewed 4 times      │ │
│  │  2. switch machine            · viewed 3 times      │ │
│  │  3. RAG                      · viewed 2 times      │ │
│  │  4. vector retrieval          · viewed 1 time       │ │
│  │  5. hallucination             · viewed 1 time       │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  ┌─ Recent Query Records ──────────────────────────────┐ │
│  │  #10  XX Project equipment?  High  1.8s  Unverified │ │
│  │  #9   YY Line signal plan?  Low  2.3s  Verified ✓  │ │
│  │  #8   ZDJ-200 params?      Med  1.5s  Verified ✓  │ │
│  │  ...                                        │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### Definitions of the Three Monitoring Metrics

| Metric | Calculation | Meaning | Optimization Direction |
|------|---------|------|---------|
| **Trust Health** | Verification click count / total query count × 100% | Higher ratio = users trust AI output less | Decrease over time (trust is being built) |
| **Low-Confidence Trigger Rate** | Low-confidence query count / total query count × 100% | Higher ratio = RAG database coverage insufficient | Decrease over time (data is being completed) |
| **High-Frequency Missing Jargon** | Top 5 sorted by jargon view count descending | Higher rank = jargon users understand least | After adding to the preset glossary, rank drops |

### Interaction Flow

1. Wang Fang clicks "Switch to Admin" button → enters Admin Dashboard
2. Interface shows all statistics for the current session
3. Wang Fang views the three monitoring metrics
4. Wang Fang views high-frequency jargon → identifies jargon to add to the glossary
5. Wang Fang views recent query records → understands user usage patterns
6. Wang Fang clicks "Switch to Frontend" → returns to Li Ming's perspective

### Exception Handling

| Exception Scenario | Handling Method |
|---------|---------|
| No query records in current session | Show "No data yet, please query in the frontend first" |
| Jargon view records are empty | High-frequency jargon area shows "No jargon view records yet" |
| Verification click count is 0 | Trust Health shows "0% (no verification behavior yet)" |

### Acceptance Criteria

```gherkin
Given the current session has performed 10 queries, 3 of which triggered verification clicks
When Wang Fang switches to Admin Dashboard
Then Trust Health shows "30%"
And total query count shows "10"

Given the current session has 5 low-confidence queries
When Wang Fang views Admin Dashboard
Then Low-Confidence Trigger Rate shows "50%"

Given the user viewed the term "switch machine" 3 times in the frontend
When Wang Fang views Admin Dashboard's high-frequency jargon
Then "switch machine" ranks Top 1
And the view count "3 times" is displayed

Given the current session has no queries at all
When Wang Fang switches to Admin Dashboard
Then display "No data yet, please query in the frontend first"
```

### Streamlit Component Mapping

| UI Element | Streamlit Component |
|---------|---------------|
| Three metric cards | `st.columns(3)` + `st.metric` |
| High-frequency jargon list | `st.dataframe` or `st.table` |
| Recent query records | `st.dataframe` |
| Switch frontend/backend | `st.button` + `st.session_state["view_mode"]` |
| Interaction log storage | `st.session_state["interaction_log"]` (list of dicts) |

---

## 4.7 DC: Data Contract Implementation Specification

### User Story

> **As** Engineer Zhang (backend engineer),
> **I want** the AI output to strictly follow the JSON Schema format,
> **So that** the frontend can render the interface deterministically, without needing NLP parsing.

### Pydantic Model Definitions

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Answer(BaseModel):
    text: str = Field(..., max_length=2000, description="AI-generated answer text")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence tier")
    is_inferred: bool = Field(..., description="Whether AI-inferred")

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
    documents_searched: int = Field(..., ge=0, description="Total documents retrieved")
    documents_matched: int = Field(..., ge=0, description="Number of matched documents")

class TrustLayerResponse(BaseModel):
    """Complete data contract for the AI Trust Layer"""
    answer: Answer
    sources: List[Source] = Field(default=[], max_length=5)
    jargon_glossary: List[JargonTerm] = Field(default=[], max_length=10)
    verification_advice: Optional[VerificationAdvice] = None
    metadata: QueryMetadata
```

### Validation Logic

```python
def validate_response(raw_json: dict) -> TrustLayerResponse | None:
    """
    Validate whether the JSON returned by the LLM conforms to the data contract.
    Pass → return TrustLayerResponse object
    Fail → return None and log the error
    """
    try:
        response = TrustLayerResponse(**raw_json)
        return response
    except ValidationError as e:
        # Degradation handling: return a minimally usable response
        log_validation_error(e)
        return create_fallback_response(raw_json)

def create_fallback_response(raw_json: dict) -> TrustLayerResponse:
    """
    Degradation handling: when JSON validation fails, construct a minimally usable response.
    Preserve fields that can be parsed; fill missing fields with default values.
    """
    return TrustLayerResponse(
        answer=Answer(
            text=raw_json.get("answer", {}).get("text", "Sorry, answer parsing failed. Please ask again."),
            confidence_score=0.0,
            confidence_level=ConfidenceLevel.LOW,
            is_inferred=True
        ),
        sources=[],
        jargon_glossary=[],
        verification_advice=VerificationAdvice(
            needs_verification=True,
            fields_to_check=["Abnormal answer parsing; manual verification of all content recommended"],
            action_link=None
        ),
        metadata=QueryMetadata(
            query_id="fallback",
            timestamp=datetime.now().isoformat(),
            response_time_ms=0,
            model_used="fallback",
            documents_searched=0,
            documents_matched=0
        )
    )
```

### LLM API Prompt Template

```
SYSTEM PROMPT:
You are the answer generator for an enterprise RAG (Retrieval-Augmented Generation) system. Answer the user's question based on the retrieved document excerpts below.
You must return the answer in JSON format, strictly following this structure:

{
  "answer": {
    "text": "Answer text (≤2000 chars)",
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

Confidence determination rules:
- high (≥0.75): Answer comes directly from document citations, no inference needed
- medium (0.50-0.74): Answer partly from documents, partly requires inference
- low (<0.50): No direct match found in documents, answer mainly based on inference

plain_language must use everyday plain words so non-technical staff can understand instantly.

USER PROMPT:
Retrieved document excerpts:
{retrieved_documents}

User question: {user_query}
```

### Acceptance Criteria

```gherkin
Given LLM returned a complete JSON conforming to the JSON Schema
When Pydantic validation executes
Then return a valid TrustLayerResponse object
And all required fields have values

Given LLM returned JSON missing answer.confidence_level
When Pydantic validation executes
Then a ValidationError is raised
And the degradation handler is invoked
And a fallback response is returned (confidence_level = "low")

Given LLM returned a sources array with 7 entries
When Pydantic validation executes
Then validation passes but sources is truncated to 5 entries
And sorted in descending order by match_score
```

---

## 4.8 N1: Latency Control — Progressive Loading Implementation Specification

### Constraint Specification

| Stage | Time Limit | Content | Implementation |
|------|---------|------|---------|
| Stage 1 | ≤ 2.0s | Main answer + confidence | Synchronous LLM API call |
| Stage 2 | ≤ 1.0s (total ≤3s) | Sources + jargon + verification advice | Async call or single request return |
| Timeout | > 3.0s | Degradation prompt | Show "Response timeout, please retry" |

### Implementation Strategy

**Option A (recommended): Single full-payload request**

The LLM API returns the complete JSON (with all fields) in one call; the frontend renders Level 0 first, and Level 1 after the user clicks.

Advantage: only one API call, lower cost; disadvantage: first response may approach 2s.

**Option B (alternative): Two progressive requests**

- First request asks only for `answer` + `confidence` (fast return)
- After the user clicks "Details", a second request fetches `sources` + `jargon` + `verification`

Advantage: faster first response; disadvantage: two API calls, higher cost and a delay on the second.

**The prototype adopts Option A**, because:
1. Simpler code (suitable for Python beginners)
2. Lower cost (one API call)
3. OpenAI structured output can return the complete JSON in one go
4. If the first response >2s, just show a loading animation

### Progressive Rendering Logic

```python
# Pseudocode

def handle_query(user_query: str):
    # Stage 1: show loading animation
    with st.spinner("Retrieving documents and generating answer..."):
        # Call LLM API to get the complete JSON
        raw_response = call_llm_api(user_query)
        response = validate_response(raw_response)

    # Stage 2: render Level 0 (default view)
    render_confidence_label(response.answer.confidence_level)
    st.markdown(response.answer.text)

    # If low confidence, render the alert banner
    if response.answer.confidence_level == "low":
        render_alert_banner(response.verification_advice)

    # Stage 3: details block (use st.expander to preserve state, not st.button)
    # ⚠️ Streamlit mechanism note:
    # st.button is a transient trigger; it returns True only on the rerun of the click,
    # and immediately False on the next rerun.
    # If you use st.button to control expand/collapse, any click on an internal sub-button
    # will cause the entire details area to disappear.
    # st.expander is a persistent-state control; its expand/collapse state is automatically
    # preserved across script reruns.
    with st.expander("📄 Details", expanded=(response.answer.confidence_level == "medium")):
        # ↑ Expanded by default on medium confidence (expanded=True),
        #   collapsed by default on high/low confidence (expanded=False)
        render_sources(response.sources)
        # Jargon uses an independent expander, always collapsed by default
        # (following progressive disclosure principle)
        with st.expander("ℹ️ Jargon Explanation", expanded=False):
            render_jargon_glossary(response.jargon_glossary)
        render_verification_advice(response.verification_advice)

    # Stage 4: record interaction log
    log_interaction(response)
```

### Acceptance Criteria

```gherkin
Given the user submits a query
When the LLM API returns within 2 seconds
Then show a loading animation first
Then after loading completes, render Level 0 (answer + label + details expander)
And total response time ≤ 3 seconds

Given the user expands the "📄 Details" expander at Level 0
Then immediately render Level 1 (sources + jargon + verification advice)
And no additional API call is needed (data is already in memory)
And when the user clicks sub-actions like "View Excerpt" inside the details,
    the details expander stays expanded (st.expander state persists)

Given confidence_level == "medium"
When the main answer finishes rendering
Then the "📄 Details" expander is expanded by default (expanded=True)
And the "ℹ️ Jargon Explanation" sub-expander is collapsed by default (expanded=False)

Given the LLM API does not return after more than 3 seconds
Then show the "Response timeout, please retry" prompt
And do not render any answer content
```

---

## 4.9 N2: JSON Format Validation Implementation Specification

### Constraint Specification

| Constraint | Spec Value |
|------|--------|
| `answer.text` max length | 2000 characters |
| `sources[]` max count | 5 entries |
| `jargon_glossary[]` max count | 10 entries |
| `confidence_score` range | 0.0 - 1.0 |
| `confidence_level` enum values | "high" / "medium" / "low" |
| `page_number` minimum | 0 |
| All required fields | Not allowed to be null/undefined |

### Validation Flow

```
LLM API returns raw JSON
        │
        ▼
   Pydantic validation
        │
    ┌───┴───┐
    │       │
  Pass     Fail
    │       │
    ▼       ▼
  Normal   Degradation
  Render    (fallback)
```

### OpenAI API Structured Output Configuration

```python
# Use the OpenAI API's response_format parameter to ensure JSON output

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "trust_layer_response",
            "schema": TRUST_LAYER_JSON_SCHEMA  # Corresponds to the Pydantic model
        }
    }
)
```

### Acceptance Criteria

```gherkin
Given LLM returned answer.text exceeding 2000 characters
When Pydantic validation executes
Then validation fails, triggering degradation handling

Given LLM returned confidence_score of 1.5
When Pydantic validation executes
Then validation fails (out of 0.0-1.0 range)

Given LLM returned sources containing 6 entries
When Pydantic validation executes
Then validation passes, but sources is truncated to the first 5 entries

Given degradation handling is triggered
Then the user sees the fallback answer: "Sorry, answer parsing failed. Please ask again."
And confidence_level is set to "low"
And verification_advice.needs_verification is set to true
```

---

## 4.10 Mock Document Set Specification

### Document Set Structure

The prototype needs 5-10 mock project documents as the RAG data source. Documents are stored locally in Markdown format.

```
mock_documents/
├── proj_XX_tech_spec_v3.2.md      # XX Project Technical Specification
├── proj_XX_signal_design.md        # XX Project Signaling System Design Diagram Notes
├── equipment_catalog_2024.md       # Rail Transit Equipment List
├── national_standard_GB_T.md       # National Standard Reference Document
├── proj_YY_line_overview.md        # YY Line Project Overview
├── proj_YY_signal_plan.md          # YY Line Signaling System Plan
├── tender_template_standard.md     # Standard Tender Template
├── zdj200_manual.md                # ZDJ-200 Switch Machine Technical Manual
├── cable_spec_railway.md           # Rail Transit Cable Specifications
└── pricing_guide_2024.md           # 2024 Pricing Guide
```

### Document Content Structure

Each document contains:

```markdown
# [Document Title]

**Document Number**: DOC-XXX
**Version**: vX.X
**Page Marker**: Page X (for source citation)

---

## [Section Title]

[Content...]

> Page marker: page=X
```

### Mock RAG Retrieval Implementation

```python
# Pseudocode: simplified Mock RAG retrieval

def mock_rag_retrieve(query: str, top_k: int = 3) -> list[dict]:
    """
    Simulate RAG retrieval: retrieve the most relevant document excerpts
    from the Mock document set. The prototype stage uses simple keyword
    matching + simulated match scores.
    """
    documents = load_mock_documents()
    scored_docs = []

    for doc in documents:
        score = calculate_match_score(query, doc)  # keyword matching
        if score > 0:
            scored_docs.append({
                "document_name": doc["name"],
                "page_number": doc["page"],
                "match_score": score,
                "excerpt": doc["excerpt"]
            })

    # Sort by match_score descending, take top_k
    scored_docs.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_docs[:top_k]
```

---

## 4.11 Interaction Log Specification

### Log Data Structure

```python
@dataclass
class InteractionLogEntry:
    query_id: str              # Unique query ID
    timestamp: str             # ISO 8601 timestamp
    user_query: str            # User query text
    confidence_level: str      # Confidence tier
    response_time_ms: int      # Response time
    viewed_details: bool       # Whether details were viewed
    viewed_jargon: list[str]   # Which jargon terms were viewed
    clicked_verification: bool # Whether verification advice was clicked
    documents_searched: int    # Number of documents retrieved
    documents_matched: int     # Number of matched documents
```

### Log Storage

The prototype stage uses `st.session_state["interaction_log"]` (Python in-memory list) for storage; not persisted.

### Log-Driven Admin Dashboard Metric Calculation

```python
def calculate_admin_metrics(log: list[InteractionLogEntry]) -> dict:
    total_queries = len(log)
    if total_queries == 0:
        return {"empty": True}

    verification_clicks = sum(1 for e in log if e.clicked_verification)
    low_conf_count = sum(1 for e in log if e.confidence_level == "low")

    # Jargon view statistics
    jargon_counter = Counter()
    for entry in log:
        for term in entry.viewed_jargon:
            jargon_counter[term] += 1

    return {
        "total_queries": total_queries,
        "trust_health": verification_clicks / total_queries * 100,  # verification click rate
        "low_conf_rate": low_conf_count / total_queries * 100,      # low-confidence trigger rate
        "top_jargon": jargon_counter.most_common(5),                # Top 5 jargon
        "recent_queries": log[-10:]                                  # Last 10 queries
    }
```

---

## 4.12 Function-Component-Data Mapping Summary

| Function | User Story | Data Contract Field | Streamlit Component | Interaction Log |
|------|---------|------------|---------------|------------|
| F1 Source Citation | Know where info comes from | sources[] | st.expander(expanded by confidence) + st.markdown | viewed_details |
| F2a Confidence Label | See trustworthiness at a glance | answer.confidence_level | st.success/warning/error | — |
| F2b Low-Confidence Alert | Proactive alert on low confidence | confidence_level=="low" + verification_advice | st.error (banner) | — |
| F3 Jargon Explanation | Understand technical jargon | jargon_glossary[] | st.expander(expanded=False) + st.expander(nested definition) | viewed_jargon[] |
| F4 Verification Advice | Know what to verify | verification_advice | st.expander + st.button(navigation action) | clicked_verification |
| F7 Admin Dashboard | Monitor system operation | metadata + interaction_log | st.metric + st.dataframe | — |
| DC Data Contract | Frontend-backend format agreement | All fields | Pydantic BaseModel | — |
| N1 Latency Control | Response ≤3s | — | st.spinner | response_time_ms |
| N2 JSON Validation | Format determinism | All fields | Pydantic validation | — |

