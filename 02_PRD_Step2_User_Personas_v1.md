
- Working prototype name: AI Trust Layer
- Phase: Full Product Design Process — Step 2
- Date: 2026-07-23

---

## 2.1 User Role Definitions (Personas)

### Persona 1 (Primary User): Li Ming — Bidding Specialist

```
┌─────────────────────────────────────────────────┐
│  Li Ming (Li Ming)                               │
│  Bidding Specialist | 38 years old | 10 years in rail transit industry │
├─────────────────────────────────────────────────┤
│                                                 │
│  Background:                                     │
│  • Graduated from a vocational college; worked his way up from the construction front line to the bidding desk │
│  • Familiar with equipment models, quotation workflows, and tender document formats │
│  • No programming background; does not understand terms such as "vectorization," "RAG," or "LLM" │
│  • Daily tools: Excel, Word, enterprise WeChat   │
│                                                 │
│  Work scenario:                                  │
│  • Receives tender documents → needs to quickly match equipment specs → generate a quotation │
│  • Previously relied on digging through historical files and calling the technical department │
│  • Now the company has deployed an AI bidding assistant and expects him to use it │
│                                                 │
│  Pain points:                                    │
│  • "I don't know whether the AI's answer is correct" │
│  • "It tells me to use a certain equipment model, but doesn't say why" │
│  • "Some words I don't understand, and I'm embarrassed to ask" │
│  • "If the quotation is wrong, is it my fault or the AI's fault?" │
│  • "I'd rather dig through the files myself; at least if something goes wrong I know why" │
│                                                 │
│  Core needs:                                     │
│  ① Know what the AI's answer is based on (source traceability) │
│  ② Know which information can be used directly and which needs verification │
│  ③ Have somewhere or someone to explain terms he doesn't understand │
│  ④ Be able to explain accountability if something goes wrong │
│                                                 │
│  Represents the group of Huaxin colleagues who "dare not use AI" │
└─────────────────────────────────────────────────┘
```

### Persona 2 (Secondary User): Wang Fang — AI Product Coordinator

```
┌─────────────────────────────────────────────────┐
│  Wang Fang (Wang Fang)                           │
│  AI Product Coordinator | 35 years old | Cross-functional bridge role │
├─────────────────────────────────────────────────┤
│                                                 │
│  Background:                                     │
│  • Non-technical background (journalism/marketing), but works in the technical team │
│  • Responsible for gathering user requirements, executing UAT, and writing training materials │
│  • Translates between engineers and business users │
│                                                 │
│  Work scenario:                                  │
│  • Receives feedback from the sales team → translates it into requirements engineers can act on │
│  • Designs UAT test cases → verifies whether the system is actually usable │
│  • Writes training manuals → teaches the sales team how to use the AI │
│                                                 │
│  Pain points:                                    │
│  • "The translation work I do manually — can it be systematized?" │
│  • "Every time I collect feedback it's one-off, with no accumulation" │
│  • "The trust mechanism I designed only exists in training, not in the product" │
│                                                 │
│  Core needs:                                     │
│  ① Productize the manual translation work        │
│  ② Collect data on user-AI interactions for continuous improvement │
│  ③ Have a framework to evaluate whether users really trust the AI │
│                                                 │
│  ← This role is you                              │
└─────────────────────────────────────────────────┘
```

### Anti-Persona (Non-Target User): Zhang Gong — Backend Engineer

```
┌─────────────────────────────────────────────────┐
│  Zhang Gong (Zhang Gong)                         │
│  Backend Engineer | 28 years old | Responsible for RAG system development │
├─────────────────────────────────────────────────┤
│  • Cares about retrieval accuracy, response speed, and system stability │
│  • Thinks UI is the frontend team's job and user training is the coordinator's job │
│  • Doesn't understand why users "can't use it" — the system returns results normally, doesn't it? │
│                                                 │
│  ❌ The trust layer is not designed for Zhang Gong │
│  But Zhang Gong needs to provide: RAG output metadata (source, confidence, etc.) │
└─────────────────────────────────────────────────┘
```

---

## 2.2 User Journey: Li Ming's Bidding Day

### Current State (No Trust Layer) — A Friction-Filled Journey

```
Stage 1: Receive the task
  Li Ming receives the tender document and must submit a quotation proposal within 2 days
  Mindset: Nervous but proficient (this is his daily work)
  ↓

Stage 2: Open the AI assistant
  Logs in to the system and sees a search box / chat dialog
  Mindset: Hesitant (last time it felt off)
  ❌ Friction point: Interface terms are unfamiliar; doesn't know what input format to use
  ↓

Stage 3: Enter query
  Tries entering: "What equipment does the XX project require?"
  The system returns a long technical description
  Mindset: Confused
  ❌ Friction point 1: Doesn't know where this information came from
  ❌ Friction point 2: Some terms are incomprehensible
  ❌ Friction point 3: Doesn't know whether it can be used directly or needs verification
  ↓

Stage 4: The decision moment ← This is the most critical breaking point
  Option A: Use the AI's answer directly → Risk: if it's wrong, he takes the blame
  Option B: Ignore the AI and dig through files himself → Wastes time; the AI deployment is wasted
  Option C: Call the technical department → Annoys them and makes him look incompetent
  Mindset: Anxious, distrustful
  ❌ Most Li Mings choose B or C → The AI system becomes useless
  ↓

Stage 5: Generate the quotation
  Eventually completes the quotation in the way he is familiar with
  The AI system generated no value along this path
  Mindset: Relieved, but still doesn't want to use AI next time
```

### Target State (With Trust Layer) — A Smooth Journey

```
Stage 1: Receive the task
  (Same as above)
  ↓

Stage 2: Open the AI assistant (Trust-Layer-enhanced interface)
  Sees a search box + brief guidance: "Enter the project number or equipment type, and I'll help you look it up"
  ✅ Improvement: Guidance in plain language, no technical jargon
  ↓

Stage 3: Enter query
  Enters: "What equipment does the XX project require?"
  The AI returns the answer, and the trust layer adds around it:
  ┌──────────────────────────────────────────┐
  │ 📄 Source: XX Project Technical Specification v3.2 (page 15) │
  │ 📊 Confidence: High (based on 3 matching documents) │
  │ ℹ️ Jargon explanation: "low voltage integration" = overall contracting of low-voltage electrical systems │
  │ ⚠️ Verification advice: Equipment quantity requires cross-verification against drawings │
  │ 📋 Actionable format: Quotation template generated (click to download) │
  └──────────────────────────────────────────┘
  ✅ Improvement 1: See the source → trust is established
  ✅ Improvement 2: Confidence indicator → know what can be used directly
  ✅ Improvement 3: Jargon translation → understandable
  ✅ Improvement 4: Verification advice → know the boundaries
  ✅ Improvement 5: Actionable format → ready to use
  ↓

Stage 4: The decision moment
  Option A: Use the high-confidence parts directly + verify the low-confidence parts
  Mindset: Confident, in control
  ✅ Li Ming chooses A → The AI system truly creates value
  ↓

Stage 5: Generate the quotation
  Based on the AI answer + trust-layer guidance, completes the quotation efficiently
  Mindset: Will use this tool again next time
```

---

## 2.3 Core Requirements Refinement (User Needs → Product Requirements)

### From User Pain Points to Product Features

| User pain point (from Persona) | User need | Product feature | Priority |
|-------------------------------|-----------|-----------------|----------|
| "Don't know if the AI answer is correct" | Source traceability | **F1: Source annotation** — every AI answer annotated with its source document | P0 |
| "Don't know which parts can be used directly" | Confidence visualization | **F2: Confidence indicator** — visual signal distinguishing high / medium / low confidence | P0 |
| "Can't understand the jargon" | Cognitive translation | **F3: Jargon explanation layer** — technical terms explained on hover or inline | P1 |
| "Don't know when to verify" | Trust calibration guidance | **F4: Verification advice** — flag content requiring manual verification | P1 |
| "AI output can't be used directly" | Actionable format | **F5: Format adaptation** — output converted to the user's working format (table / template) | P2 |
| "Who is responsible if something goes wrong" | Accountability | **F6: Interaction log** — records the history of user-AI interactions | P2 |

### Priority Explanation

- **P0 (Must-have)**: Source annotation + Confidence indicator — these are the core of the trust layer; without them it is not a "trust layer"
- **P1 (Should-have)**: Jargon explanation + Verification advice — this is the core of cognitive translation and distinguishes the product from an ordinary RAG system
- **P2 (Nice-to-have)**: Format adaptation + Interaction log — enhance the experience; can be shown as "future work" in the portfolio prototype

---

## 2.4 Competitor & Existing Solution Analysis

### Current Market Solutions

| Product / Solution | Source Transparency | Confidence Display | Jargon Translation | Trust Calibration | Targeted at Non-Technical Users |
|--------------------|---------------------|--------------------|--------------------|-------------------|---------------------------------|
| ChatGPT (standard mode) | ❌ None | ❌ None | ❌ None | ❌ None | Partial |
| ChatGPT (search mode) | ✅ Citations | ❌ None | ❌ None | ❌ None | Partial |
| Perplexity AI | ✅ Citations | ⚠️ Simple | ❌ None | ❌ None | ❌ Tech-biased |
| Microsoft Copilot | ⚠️ Partial | ❌ None | ❌ None | ❌ None | Partial |
| Typical enterprise RAG systems | ❌ Usually none | ❌ None | ❌ None | ❌ None | ❌ Usually technical users |
| **AI Trust Layer (your product)** | **✅ Document-level** | **✅ Visualized** | **✅ Inline** | **✅ Proactive guidance** | **✅ Core target** |

### Competitive Advantage Analysis

**The fundamental difference between prototype and existing solutions:**

1. **Common blind spot of existing solutions**: They all optimize "AI answer quality," not "users' understanding of and trust in AI answers"
2. **The prototype's entry point**: Without changing the AI backend, add a trust layer at the output end — lightweight, attachable, and portable
3. **The unique moat**: I have real observation experience of non-technical users — most AI transparency research is done by technical teams and lacks a user perspective

### Academic Positioning

| Research Field | How Your Product Maps |
|----------------|-----------------------|
| Explainable AI (XAI) | Not explaining model internals, but explaining output source and reliability |
| Trust Calibration | Not increasing or decreasing trust, but calibrating trust to a reasonable level |
| Human-AI Collaboration | Not replacing human judgment, but augmenting human judgment |
| Cognitive Load Theory | Reducing cognitive overload for non-technical users through layered information presentation |
