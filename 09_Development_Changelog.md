# 09. Development Changelog — Bug-Fix & Debugging Trail

> Purpose: This document records the **iterative engineering process** behind *AI Trust Layer*, not just its final state.
> Each entry follows a consistent structure: **Phenomenon → Root cause → Fix → Verification**, so a reviewer can see how problems were diagnosed and resolved.
> All commit hashes reference the `master` branch of this repository.

---

## 0. Environment & tooling context

- **Runtime**: Python 3.12.10 in a local `.venv`; Streamlit 1.60.0; OpenAI / Pydantic / python-dotenv.
- **Demo safety**: `MOCK_LLM_MODE` lets the app run with zero API keys by serving three canned, schema-valid responses (High / Medium / Low confidence).
- **Verification method (reusable)**: because Streamlit's hot-reload is unreliable for `app.py`/`config.py`-level changes, every UI fix was verified by (a) `py_compile`, (b) killing the old Streamlit process and restarting, and — for DOM/CSS questions — (c) driving **headless Chrome** (local install) via `puppeteer-core` to read the *real rendered DOM* and computed styles. This last step is what finally exposed several wrong CSS selectors (see §3, §4, §5).

---

## 1. Forced demo mode — the "all answers turn red" bug

- **Phenomenon**: When the app was run locally *without* setting `MOCK_LLM_MODE` and *without* an OpenAI key, every answer fell back to **LOW confidence (all red)** and the home page sometimes showed *"Sorry, the response could not be parsed."*
- **Root cause**: `config.py` defaulted `MOCK_LLM_MODE = true`, but the user's shell/`.env` had overridden it to `false`. `llm_api.py` then took the **real OpenAI branch**; with no key the call failed/timeout'd, and `models.py: create_fallback_response` *always* wrote `confidence_level = LOW`. The "could not be parsed" text is exactly that fallback message.
- **Fix** (`4f4596b`): in `config.py`, added `if not OPENAI_API_KEY: MOCK_LLM_MODE = True`. No key ⇒ demo mode, guaranteed to run out of the box, independent of environment variables.
- **Verification**: local run now auto-enters demo mode; the three demo scenarios render green/orange/red correctly; `py_compile` clean.

---

## 2. Inter webfont for consistent rendering

- **Phenomenon**: The preview HTML and the live Streamlit page rendered with *different* fonts depending on the machine's available fonts.
- **Fix** (`4f4596b`): inject the **Inter** webfont (`<link>` to Google Fonts CDN) in both `app.py` (after `set_page_config`) and `admin_dashboard_preview.html`; gracefully fall back to the system sans-serif when offline.
- **Verification**: both surfaces now resolve to the same font stack.

---

## 3. Search-box idle gray border — the selector saga

This single visual detail went through four iterations because the documented Streamlit selectors were stale for v1.60.

| Commit | Attempt | Why it was wrong |
|---|---|---|
| `28eccde` | Added idle gray border on the input | Targeted the wrong DOM node — border never painted |
| `3ddef8d` | Moved border to the *visible* box, fixed double focus ring | Still used `div[data-baseweb="input"]` |
| `afe82d1` | Deepened color `#D4D4D8` | Same stale `data-baseweb` selector — still no hit |
| `fd6525d` | **Real fix** | See below |

- **Phenomenon (final diagnosis)**: after a *fully clean* restart (closed tabs → `run.bat` → new tab → hard refresh), the idle gray border **still did not appear**.
- **Root cause** (`fd6525d`): **Streamlit 1.60 has no `data-baseweb="input"` attribute.** The real wrapper is `[data-testid="stTextInputRootElement"]` (the `<input>` lives inside it). The old selector matched nothing, so the "default" border was effectively invisible (`rgb(249,249,251)`, near-transparent).
- **Fix**: paint the idle gray border `#C4C4C8` + `12px` radius on `stTextInputRootElement`, and a blue `:focus-within` border + soft glow on focus.
- **Verification**: headless Chrome confirmed the idle gray border and focus ring render in the real DOM.

> **Lesson (reusable)**: never trust stale framework selectors — verify against the actually-rendered DOM.

---

## 4. "Press Enter to submit form" hint overlapping the placeholder

- **Phenomenon**: The search placeholder *"Ask me anything about your project documents"* overlapped the Streamlit-generated hint *"Press Enter to submit form"*.
- **Root cause** (`afe82d1` mis-diagnosed): the hint lives **not** under `stFormSubmitButton` but at `[data-testid="stTextInput"] > [data-testid="InputInstructions"] > span`. The earlier `[data-testid="stFormSubmitButton"] small` selector matched nothing.
- **Fix** (`fd6525d`): hide `[data-testid="InputInstructions"]` via a scoped `<style>` block. The Enter-to-submit *behaviour* is preserved by `st.form` (the search box + button share one `st.form`), only the redundant hint text is removed.
- **Verification**: headless Chrome confirmed the hint node is hidden and Enter still submits.

---

## 5. Recent Queries table borders

Three sub-problems, each fixed in turn:

1. **Last-row bottom seam lost** (`3ddef8d`): the white card's `border-radius` + `overflow:hidden` clipped the last `<tr>` bottom border. Fixed by dropping the last row's `border-bottom` and letting the card's own border close the section.
2. **Inline `!important` stripped** (`fd6525d`): the HTML sanitizer (DOMPurify) **strips `!important` from element-level `style` attributes**, so the last-row inline fix silently failed and fell back to Streamlit's default `table td` border. **Scoped `<style>` blocks, however, keep `!important`.** Fix: move all table rules into a scoped `.tl-rq-table` style (`border-collapse:separate; border-spacing:0`, non-last rows get a `1px` bottom hairline).
3. **Inconsistent vertical column lines** (`1bdeba7`): the scoped style reset `td` borders but **not** `th` — Streamlit's default `table th` carried vertical borders, so the header had column lines while data rows did not. Final fix: `th, td { border-left:none; border-right:none }` (all vertical lines removed), keep only horizontal hairlines; last row closes cleanly.

- **Verification** (`1bdeba7`): headless Chrome confirmed `th`/`td` left/right = `0px`, bottom hairline on header + data rows, none on the last row.

---

## 6. No-documents fallback banner

- **Phenomenon**: when a query matched no document, the UI gave no clear signal, or (worse) showed the red LOW-confidence alert even though *no source* existed to flag.
- **Fix**:
  - `3ddef8d` introduced `render_no_docs_banner()` — an **amber** warning shown when `response.sources` is empty.
  - `49b6f15` made the logic precise: the **red** alert banner appears only when `level == LOW **and** sources exist`; with no sources, only the amber "no documents" banner shows. Unmatched queries fall back to a `nomatch` mock (`sources=[]`).
  - Later refinement: `render_response` early-returns and renders *only* the amber banner for `nomatch`, avoiding a duplicate banner; the copy was expanded to a project-specific long form.
- **Verification**: the three core demo scenarios (signaling / budget / switch machine) are unaffected; empty-source queries show exactly one amber banner.

---

## 7. `run.bat` launcher for Windows CMD users

- **Phenomenon**: Users on **Windows CMD** (no Git Bash) could not follow `source .venv/Scripts/activate` instructions ("'source' is not recognized"). Separately, a *stale* Streamlit process holding the port made restarts appear to "do nothing."
- **Fix** (`1a255c8`): added `ai_trust_layer/run.bat` — pure ASCII, `cd /d %~dp0` (avoids Chinese-path encoding issues), `call .venv\Scripts\activate.bat`, `taskkill /F /IM streamlit.exe` (kill stale process), then `streamlit run app.py --server.port 8600`. Double-click to launch, no manual commands.
- **Verification**: double-click launch succeeds; killing the old process guarantees the new code is served.

---

## 8. Empty-state demo control (Path A)

- **Phenomenon**: A PRD acceptance criterion requires *"no queries → dashboard shows '暂无数据，请先在前台进行查询'"*. In practice this branch was **dead code** — `app.py` auto-seeds 7 demo entries on every startup, so the empty state could never be reached by a normal user.
- **Decision**: Rather than remove the auto-seed (which would break the out-of-the-box demo), add an **explicit, low-risk control** so the empty state is *demonstrable on demand* without affecting any other data path (~10 lines, no regression to seeded flows).
- **Fix** (`bdb1a7f`): a seed-gate flag (`demo_data_cleared` + `_request_seed`). The Admin page gains a bilingual **"Clear demo data / 清空演示数据"** button (and a **"Restore demo data / 恢复演示数据"** button when empty). Default behaviour still seeds; clearing makes the empty state reachable; restoring brings the demo back.
- **Verification**: headless Chrome confirmed Clear → empty info + Restore button (no Recent Queries) → Restore → metrics and Clear button return.

---

## 9. Admin Dashboard P1 — visual-analytics redesign (ardot ↔ code sync)

The Admin Dashboard was upgraded from native Streamlit components to a custom, on-brand visual-analytics surface. Key milestones (branch `p1-admin-dashboard`, merged to `master` via fast-forward at `d29a37d`):

- Added three charts — **Trust Health trend** (cumulative verification-click rate), **Confidence Distribution donut**, **Jargon Term Heat** bar — paired *one-to-one* with their raw-data tables.
- Removed redundancy: charts absorb the percentages/values; the right column becomes a PRD-driven **interpretation card** ("Reading the Distribution", "Glossary Candidates").
- Removed **PRD F7 internal requirement labels** that had leaked into the UI (Wang Fang, the dashboard user, should never see internal requirement IDs).
- Rebuilt the donut / bar / trend as **inline SVG** (replacing Altair) for pixel-level control and ardot-mockup fidelity; fixed the donut center text, legend clipping, and ring thickness.
- Aligned every section eyebrow, title, subtitle, and the Recent Queries **pagination** to the ardot mockup; added a unified footer matching the home page.
- Resolved a circular flexbox dependency in the mockup (decorative accent bar using `fill_container` inside a `hug_contents` parent) via absolute positioning + `clipsContent`.

---

## 10. Font unification (stability decision)

The numbers and technical labels on the Admin page went through several iterations:

1. Initially **IBM Plex Mono** for all numbers/eyebrows (matching the home page hero labels).
2. User requested a **single black-letter (sans) font for all numbers** ("lock it down") → switched to a `_NUM` sans stack.
3. After reviewing the live preview, the user decided the Admin font must **match the home page** → reverted to Mono.
4. **Final (user's latest, authoritative)**: a single locked sans/黑体 stack `_NUM = 'Inter','PingFang SC','Heiti SC','Microsoft YaHei',sans-serif` for *all* numbers; `Inter` (`_SANS`) for eyebrows; IBM Plex Mono removed from the runtime UI. A global CSS rule forces `st.metric` values to the same font.

> This back-and-forth is documented explicitly because it shows the iteration discipline: the *latest* explicit user instruction overrides earlier ones, and the final state is internally consistent across home, Admin, and the ardot source.

---

## Appendix — Consolidated commit reference

| Commit | Area | Summary |
|---|---|---|
| `4f4596b` | core | Force `MOCK_LLM_MODE` when no API key; load Inter webfont |
| `28eccde` | frontend | Idle gray border + no-doc fallback banner (first attempt) |
| `3ddef8d` | frontend/admin | Single focus border; `<td>`-level table bottom border |
| `49b6f15` | frontend/llm | Trigger no-docs banner on unmatched queries; suppress redundant LOW alert |
| `1a255c8` | tooling | `run.bat` launcher for CMD users |
| `afe82d1` | frontend/admin | Hide form-submit hint; deepen idle border (selector still wrong) |
| `fd6525d` | frontend/admin | **Correct** Streamlit 1.60 DOM selectors (search border, hint, table) |
| `1bdeba7` | admin | Remove vertical table lines; keep horizontal hairlines only |
| `d29a37d` | admin | P1 Admin Dashboard merged to `master` (fast-forward) |
| `bdb1a7f` | frontend/admin | Empty-state demo control (Path A) + `.gitignore` expansion |
