# PRD Step 1: Problem Definition & Scenario Reconstruction (Confirmed)

> Working product name: AI Trust Layer
> Phase: Full Product Design Process - Step 1
> Date: 2026-07-23
> Status: ✅ Confirmed (user supplied key information on 2026-07-23)

---

## 1.1 Scenario Reconstruction: What You Experienced at Huaxin

### Background

China Huaxin Post & Telecom Technologies is a rail transit low-voltage (ELV) systems integrator. The company deployed an internally built RAG (Retrieval-Augmented Generation)-based AI bidding assistant to help the sales team:

- Use project documents as the source, and perform project database retrieval via an AI model
- Ultimately handle the quote generation for bidding documents

### System Technical Architecture (Confirmed)

```
Project documents (source) → document preprocessing → vectorized storage → RAG retrieval
                                                                       ↓
User (B/S web client) → enter query → LLM generates answer → output to user
     ↑                                                                  ↓
 Sales staff (non-technical)                                receives AI-generated specs/quotes
```

- **Architecture type**: B/S architecture (Browser/Server); users access via a web page
- **Your role**: Not responsible for front-end UI design or back-end code development; responsible for requirements gathering, user testing, feedback translation, and training delivery
- **Engineering team's focus**: Retrieval capability, model response speed, and data coverage

### The Real Problems You Observed

Based on your recommendation letter (from R&D Director Jiang Jian), your PS description, and this confirmation:

| # | Problem Symptom | Root Cause Analysis |
|---|---------|---------|
| 1 | **The sales team could not use it** | The interface used jargon they did not recognize; input requirements were unclear; the workflow did not match actual habits |
| 2 | **Users did not trust the AI output** | The AI answers carried no source citations, so users did not know where the information came from; they could not tell what was trustworthy and what needed verification |
| 3 | **Risk of "AI hallucination"** | The development team initially proposed an open Wiki database for data ingestion; you foresaw the need to constrain user input → otherwise the AI would generate inaccurate content |
| 4 | **Cognitive overload** | The system output required further processing that users could not complete; a "reference gap" existed between technical capability and users' cognitive level |
| 5 | **AI-phobia** | Non-technical employees had an instinctive resistance to AI systems; a bidding-department employee even complained that "AI would make them lose their jobs" |

### What You Did

- Gathered user requirements
- Acted as communication translator between engineers and non-technical business users
- Executed User Acceptance Testing (UAT)
- Identified the risks of open data ingestion and drove the adoption of strict data verification protocols
- Designed UAT edge-case test scenarios
- Redesigned onboarding training and created a jargon-free user manual
- Significantly reduced "AI-phobia" among non-technical employees

### Key Insight

> **A technically perfect system failed completely on the user side. The problem was not model capability, but that users could not understand, trust, and effectively use the AI's output.**

---

## 1.2 Problem Formalization: From Personal Experience to a General Problem

### Core Problem Statement

**Current RAG-style AI systems exhibit a systematic "trust and comprehension gap" when delivering information to non-technical users:**

1. **Source Opacity**
   - When the AI generates an answer, users cannot see the information source
   - Users cannot tell whether the answer is based on an authoritative document or model inference
   - → Trust cannot be established

2. **Confidence Opacity**
   - The AI presents all answers with the same level of certainty
   - Users cannot distinguish "high-confidence facts" from "low-confidence speculation"
   - → Either trust everything (risk) or trust nothing (waste)

3. **Trust Calibration Gap**
   - The system never tells users "when to trust me, and when to verify on your own"
   - Users lack a framework for judging the reliability of AI output
   - → Trust is binary (all or nothing) rather than calibrated

4. **Cognitive Translation Gap**
   - The AI uses technical jargon that users do not understand
   - The output format does not fit users' work habits
   - → Even when the information is correct, users cannot use it effectively

### Why This Problem Is Worth Solving

| Dimension | Explanation |
|------|------|
| **Universality** | Not limited to the bidding assistant — all RAG systems serving non-technical users have this problem |
| **Urgency** | As AI spreads through enterprises, interaction between non-technical users and AI systems will become a mainstream scenario |
| **Your unique qualification** | You are among the very few who have both personally experienced this problem and possess user-research and communication-translation skills |
| **Academic value** | Directly addresses core HCI topics: explainable AI (XAI), trust calibration, cognitive ergonomics |
| **MSc thesis potential** | "An AI Trust Layer for Enterprise RAG Systems: Designing Transparency for Non-Technical Users" — a perfect MSc thesis title |

---

## 1.3 Confirmed Key Information

### A. Scenario Accuracy (Confirmed)

1. **RAG system interaction**: B/S architecture web client, accessed via browser. Project documents serve as the source; an AI model performs project database retrieval and ultimately handles bidding-document quotes.
2. **Your role boundary**: Not responsible for front-end UI design or back-end code development; responsible for requirements gathering, UAT, feedback translation, and training delivery.
3. **Product positioning**: The portfolio product is **based on your real experience and observations from that project**, but is not a replica of the company system — rather it builds an "AI Trust Layer" interface prototype that addresses the trust and comprehension gap you observed.

### B. Technical Capability Boundary (Confirmed)

| Skill | Current Level | Expected Progress |
|------|---------|---------|
| Python | Studying Cisco Python Essentials 1, beginner stage | Finish Essentials 1 this month, move to Essentials 2 |
| Data cleaning / ML | AI Trainer course, partial understanding | Have conceptual awareness, can understand the process but not proficient |
| API calls / JSON | Not yet studied | Can start after Essentials 2 |
| Front-end development | No experience | Not in plan — prototype will use a Python web framework |

### C. Technical Implementation Strategy

Based on your current technical state, the prototype implementation path:

```
Python back end (requests + LLM API) → Streamlit/Gradio front end (no HTML/CSS/JS needed)
```

- **Streamlit/Gradio**: Python-native web UI frameworks that build interactive web apps with pure Python code, requiring no front-end knowledge
- **LLM API**: Use the OpenAI/Anthropic API to simulate the answer generation of a RAG system
- **Mock data**: Create a small simulated document set to mimic project documents as the RAG data source
- **Core innovation lies in the trust layer**: Not in the RAG engine itself, but in redesigning how AI output is presented

### D. Narrative Consistency (Confirmed)

The product positioning is fully consistent with your PS narrative: your PS tells the story of a "technical translator," and this product turns the "translation" work you did manually at Huaxin into a **product** — from "you translated once for the sales team" to "the system can translate repeatedly."

---

## 1.4 Portfolio Strategy: Why Base It on a Real Project Rather Than a Fictional Scenario

| Dimension | Based on Real Project | Fictional Scenario |
|------|------------|---------|
| Interview tellability | ✅ Every design decision has a real backstory | ❌ Can only discuss design theory |
| Emotional authenticity | ✅ You experienced these pain points firsthand | ❌ Lacks real feeling |
| Technical feasibility | ✅ You know how the system works | ❌ May design something unrealistic |
| IP risk | ⚠️ Needs abstraction; do not replicate the specific system | ✅ No risk |
| MSc thesis continuity | ✅ Can directly become a thesis topic | ❌ Need to find a new direction |

**Conclusion**: Based on real project experience, build an abstracted trust-layer prototype. Do not replicate the company system; reuse your genuine understanding of the problem.
