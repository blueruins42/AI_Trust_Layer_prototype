# AI Trust Layer — Demo Recording Walkthrough (OBS)

A precise, click-by-click script for recording a **real, cursor-driven** operation video of the
working prototype. Static screenshots cannot show the *expanded* interface (sources / jargon /
verification); this recording does — scroll slowly so the full expanded panel is captured.

> This file is intentionally **untracked** — it will NOT be pushed unless you `git add` it.
> The recorded video itself goes to `ai_trust_layer/videos/ai_trust_layer_demo_3min.mp4`
> (overwriting the placeholder) and is committed tomorrow.

---

## 0. Before you record

1. **Start the app** (demo mode works with no API key):
   ```bash
   cd ai_trust_layer
   streamlit run app.py --server.port 8600
   # or just double-click run.bat
   ```
2. **Open** http://localhost:8600 in a clean browser window (use incognito to hide
   extensions / bookmark bar). Zoom = 100%. Maximize or size to ~1400px wide.
3. **Reset state** once: in the app, top-right click **Admin → Clear demo data → Restore demo data**
   so the dashboard starts with the seeded data. (This is optional; seed data auto-loads anyway.)

---

## 1. OBS settings (one-time)

| Setting | Value |
|---|---|
| Source | **Window Capture** → select your browser window (e.g. `Chrome — AI Trust Layer`). Avoid Display Capture (it grabs the whole desktop). |
| **Capture Cursor** | ✅ TICKED — this is what shows your real mouse pointer. |
| Canvas / Output | **1920 × 1080**, **30 FPS**. |
| Output format | **MP4** (or MKV then Remux to MP4). Bitrate ~**10000 kbps** (or CQP 18–20 for quality). |
| Audio | None needed (silent is fine for a portfolio walkthrough). |
| Crop | Right-click source → **Transform → Fit to screen**, or just maximize the browser. Keep only the browser, no desktop. |
| Output path | Set to `ai_trust_layer/videos/` and name the file `ai_trust_layer_demo_3min.mp4` (overwrites placeholder). |

Click **Start Recording**, perform the walkthrough below, then **Stop Recording**.

---

## 2. The click-path (≈ 3 minutes)

Timings are a guide — move the mouse **deliberately**, pause ~1s on each key element, and
**click** (don't just hover).

### Scene 0 — Landing / value proposition  `0:00 – 0:15`
- Show the hero: **"Every AI answer, accountable."**
- Point at the search box + 3 example chips + the 3 value cards
  (Source Transparency / Confidence Calibration / Plain Language On Demand).
- Narrate: *"A trust interface on top of enterprise RAG — it tells non-technical users
  when to trust an AI answer and when to verify."*

### Scene 1 — High confidence (green) + full expansion  `0:15 – 0:55`
- Click the chip **"What signaling system does Project XX use?"**
  (or type it and press Enter).
- Show the **green "High Confidence"** pill + the answer text.
- **Click the "Details · sources, jargon & verification" expander** to open it.
- Inside: **Sources (2 matching documents)** with match scores → click **"View Excerpt"**
  to reveal the excerpt.
- Open **"Jargon Glossary"** → show **CBTC** plain-language line → click **"Formal Definition"**
  to reveal the technical definition.
- *This expanded view is exactly what static screenshots miss — scroll down slowly so it's all captured.*

### Scene 2 — Low confidence alert (red) + source drill-down  `0:55 – 1:35`
- Click the chip **"YY Line construction budget"** (or type a query containing *budget/cost*).
- Show the **red "Manual verification required" alert banner** with **28% confidence**
  and *"Verify: Specific cost amounts · Budget approval document number · Funding source"*.
- Click **"View source document →"** → the **Document View** (pricing_guide_2024.md, page 22) opens.
- Click **"← Back to Answer"** to return.

### Scene 3 — Medium confidence (yellow) progressive disclosure  `1:35 – 2:10`
- Click the chip **"ZDJ-200 switch machine parameters"** (or type *switch / ZDJ / parameter*).
- Show the **yellow "Partial Match · Verify Recommended"** pill + the technical-parameter answer.
- Open **Details** → **Sources (2 docs)** + open **Jargon Glossary** (3 terms:
  Electric Switch Machine / Switching Force / Operating Time, each with plain language) +
  **"Verification Recommended"** (Rated current value, Applicable rail types).

### Scene 4 — Graceful no-match (optional, builds credibility)  `2:10 – 2:25`
- Type something off-topic, e.g. **"What is the weather today?"** and submit.
- Show the **amber "I couldn't find any documents…"** banner — honest fallback, no false confidence.

### Scene 5 — Admin Dashboard (monitoring closure)  `2:25 – 2:55`
- Click the top-right **"Admin"** button.
- Show: metric cards → **Trust Health trend line** → **Confidence Distribution donut**
  → **Jargon Term Heat bar** → **Recent Queries** table (with pagination).
- Narrate: *"Ops can see trust health, confidence mix, and the vocabulary gap across real usage."*

### Scene 6 — Empty state (optional)  `2:55 – 3:10`
- In Admin, click **"Clear demo data"** → dashboard shows **"No data yet — please query the
  frontend first."** Then click **"Restore demo data"** to bring it back.
- Stop recording.

---

## 3. Query keyword triggers (so typed queries work too)

The demo mode matches keywords — if you type instead of using chips, these work:

| Type a query containing… | Triggers |
|---|---|
| `signal` `signaling` `CBTC` `system` `equipment` | **High** confidence (green) |
| `switch` `machine` `ZDJ` `parameter` `specification` | **Medium** confidence (yellow) |
| `budget` `cost` `price` `investment` | **Low** confidence (red alert) |
| anything else | **No-match** amber banner |

The three example chips already map to High / Low / Medium respectively.

---

## 4. Capturing the expanded view (the whole point)

- After clicking any **Details / View Excerpt / Jargon Glossary / Formal Definition** expander,
  **scroll down slowly** so the recording shows the full panel — not just the top.
- Keep the mouse cursor visible and moving; click expander headers (the text), not the empty space.
- If a panel runs below the fold, pause and scroll rather than resizing the window mid-record.

---

## 5. After recording — commit the video (tomorrow)

```bash
cd /e/新建文件夹/UL_Portfolio
git add ai_trust_layer/videos/ai_trust_layer_demo_3min.mp4   # + .webm if you exported one
git commit -m "Add 3-minute operation demo video (real cursor walkthrough)"
git push
```

The README already links this video, so it will render on GitHub once pushed.
