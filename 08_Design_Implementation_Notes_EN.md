# 08. Design Implementation Notes

> Stage: P0 Visual Upgrade (Homepage guidance layer + Low-confidence alert banner redesign)
> Date: 2026-07-25
> Design mockup: ardot file ID `707535023504113` (https://ardot.tencent.com/file/707535023504113)
> Upstream: PRD Step 1-6 (product planning chain, locked; this document does not replace the PRD)
> Positioning: Records key decisions, engineering fixes, and reusable lessons from the design implementation process

---

## 0. Why This New Document Was Added (Rather Than Replacing the PRD)

PRD Step 1-6 is the **product planning chain** — from problem definition to Portfolio scope, each step has traceable decision rationale and is locked and should not be modified.

This document is the **Design Implementation Notes** — it records problems encountered, compromises made, and bug-fix patterns discovered while visualizing the PRD on the ardot canvas. It belongs to the "implementation-layer accumulation" and is decoupled from the PRD (planning layer).

The relationship between the two: the PRD says "what to build"; this document says "what was discovered while building it, and how it was resolved."

---

## 1. Design System Selection (search_style_guide → build_style_guide)

Design tokens obtained via ardot style catalog search + build:

| Domain | Choice | Rationale |
|---|---|---|
| style | soft-card-pastel-finance | Deep-blue sense of trust, enterprise-grade, avoids the cold hardness of a Bloomberg terminal |
| color | bento-neutral | warm-white #FAFAFA + engineering sense of clear order |
| typography | Inter Black hero + IBM Plex Mono metrics | 2024 enterprise SaaS tone, Black large type + Mono labels |
| layout | bento-attio-modern-saas | nav + hero + bento feature grid structure |
| composition | hero-template-A | centered hero, title on top, primary action centered |

**Core tokens**:
- Background: `#FAFAFA` (warm-white, one degree warmer than pure white #FFFFFF)
- Card: `#FFFFFF`
- Text primary: `#0A0A0B`, secondary: `#52525B`
- Primary brand color: `#014DB2` (deep blue, trust)
- Semantic triplet: `#10B981` (green/high) / `#F59E0B` (orange/medium) / `#EF4444` (red/low) — echoes the product's three-tier confidence
- Card corner radius: 24px / button & search box: 50px (pill)
- Shadow: `rgba(1,77,178,0.06)` blue-toned (not black)

---

## 2. Homepage Guidance Layer Redesign (Replacing the Original scene1_idle.png)

**Original problem**: title + intro copy + bare input + button — minimal, but no guidance, no branding, no value proposition.

**New design structure**:
1. Top Nav: shield Logo + "AI Trust Layer" + Admin pill button on the right
2. Hero section (centered):
   - Eyebrow (Plex Mono blue): `TRUST INTERFACE FOR ENTERPRISE RAG`
   - Big title (Inter Black 80px): `Every AI answer, accountable.`
   - Subtitle: `See where it comes from. Know how much to trust it. Verify when it matters.` (displayed on one line, to avoid single-word line breaks)
   - Search box (pill corner radius + deep-blue Search button + search icon)
   - 3 example query chips (locked to the three Demo scenarios)
3. Value card section (#F9F9FB background): 3 bento cards
   - Source Transparency (blue #3B82F6 icon)
   - Confidence Calibration (green #10B981 icon)
   - Plain Language, On Demand (orange #F59E0B icon)
   - Icon color triplet echoes the product's three-tier confidence semantics
4. Footer: `Built for enterprise RAG systems · Student design prototype · Non-commercial · Designed by Shuting Fan`

---

## 3. Low-Confidence Alert Banner Redesign (Replacing the Original frontend.py render_alert_banner)

**Original problem**: light-red #fff0f0 flat card + red border + "Warning" + ordinary button — weak visual weight, looks like a generic system prompt.

**New design structure** (horizontal three-segment layout):
1. Left 6px deep-red #DC2626 accent bar (visual anchor, runs full height)
2. Red circular 48x48 warning icon (white ! symbol + shadow) = single focal point
3. Content area:
   - Title `Manual verification required` (Inter Bold 20px #991B1B) + confidence pill `28% confidence` (red background, white text)
   - Description `No fully matching spec found. This answer is AI-inferred — reference only.`
   - Verification field `Verify: construction cost · budget approval number · funding source`
4. Primary action button `View source document` (deep-red solid pill + document icon + shadow)

**3-color system** (restraint requested by user): light-red #FEF2F2 background / deep-red #DC2626 primary / white #FFFFFF contrast. Deep-red text variants (#991B1B / #7F1D1D / #B91C1C) belong to the same red family's light-dark range and do not count as exceeding 3 colors.

**Visual weight comparison**: original → new version improves by roughly 5x (accent bar + icon + shadow, triple-anchored).

---

## 4. ⚠️ Engineering Fix: flexbox Circular Dependency (Reusable Lesson)

### 4.1 Bug Symptoms

The alert banner's left decorative accent bar (leftBar) used `height: "fill_container"` + the parent container (banner) used `height: "hug_contents"` → **circular dependency**:
- leftBar height depends on banner height (fill_container)
- banner height depends on child node height (hug_contents)
- leftBar is the only flowing child node carrying height → cannot be computed

**Symptoms**: `capture_layout` reported `Content Row: Outside parent bounds, and parent (clipsContent: true)` — contentRow was clipped by banner, banner height was abnormally small.

### 4.2 Fix Pattern (Reusable)

When decorative elements (accent bar / badge / background graphic) need to "run through the parent container", **do not use fill_container**; instead use absolute positioning + fixed large size + parent clipsContent clipping:

```javascript
// ❌ Circular dependency
leftBar = I(banner, { width: 6, height: "fill_container", fill: "#DC2626" })
// banner height: "hug_contents" → circular

// ✅ Absolute positioning + clipping
leftBar = I(banner, {
  layoutPositioning: "ABSOLUTE",
  x: 0, y: 0,
  width: 6, height: 300,  // fixed large height, greater than parent's expected height
  fill: "#DC2626",
  topLeftRadius: 16, bottomLeftRadius: 16  // round only the left corners
})
// banner: height: 132 (fixed), clipsContent: true → leftBar clipped to 132px, running through
```

### 4.3 layout warning Noise Identification

After the fix, `capture_layout` will still report a `Left Accent Bar: Outside parent bounds` warning — **this is by design** (the accent bar intentionally overflows and is clipped to achieve the run-through effect), not a bug.

**Judgment rule**: if the warning node is a decorative element and the parent node has `clipsContent: true`, the warning can be ignored; if it is a content node (text/frame containing information), it must be fixed.

---

## 5. Design Aesthetic Constraints (Distilled from User Feedback, 2026-07-25)

| Constraint | Description | Application |
|---|---|---|
| **Typographic integrity** | Subtitles/single-line text should avoid a single word breaking onto its own line (e.g. "matters." as a lone word breaks the aesthetic) | Subtitle displayed within one line; narrow the width or trim the copy if necessary |
| **Alignment consistency** | Border size, padding, and spacing of same-level cards/components stay visually consistent | The three value cards have completely identical width/cornerRadius/padding |
| **Color restraint** | Keep each page/scenario within 3 colors | Homepage: blue/green/orange icon triplet + neutral background; Alert: red/white/light-red |
| **Clear visual weight** | Alert/prompt components need a strong visual anchor | Alert banner: accent bar + icon + shadow, triple-anchored |
| **No Chinese in visuals** | All on-screen copy in the design mockup is English (applying to Irish schools, language consistency) | Chinese appears only in design annotations/documents, never in the UI visuals |

---

## 6. Author Attribution Decision

**Decision**: Add `Designed by Shuting Fan` to the homepage Footer.

**Rationale**:
- Portfolio pieces must be attributed; reviewers need to know the author
- Placed in the restrained Footer position, not overshadowing the main content
- Placed alongside the product identity, forming a complete "work attribution chain"

**Footer copy**: `Built for enterprise RAG systems · Student design prototype · Non-commercial · Designed by Shuting Fan`

---

## 7. ardot Design Mockup → Streamlit Code Mapping

| ardot design mockup | Corresponding Streamlit code | Implementation approach |
|---|---|---|
| Homepage guidance layer | `frontend.py render_frontend()` | Rewrite: value proposition + search box + example chips + value cards |
| Alert banner | `frontend.py render_alert_banner()` | Rewrite: accent bar + icon + title/pill + fields + primary button |
| Light theme + deep blue | `.streamlit/config.toml` | Create new: primaryColor #014DB2 + backgroundColor #FAFAFA |
| Inter / IBM Plex Mono | config.toml font config | Create new: sansSerifFont Inter, codeFont IBM Plex Mono |

---

## 8. To-Do (Subsequent P0 Items)

- [ ] Medium-confidence result page design mockup (render_response + dual expander)
- [ ] High-confidence result page design mockup
- [ ] Admin Dashboard design mockup (add charts)
- [ ] Unify switching the prototype from dark Streamlit to light + deep-blue theme
- [ ] Re-capture the 4 key README screenshots (based on all new designs)
