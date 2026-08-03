# Deploying AI Trust Layer — Streamlit Community Cloud

This repository runs as a **single, self-contained interactive portfolio prototype** on Streamlit Community Cloud (free). It runs the real AI Trust Layer demo offline (no API key needed) and links back to the full design documentation on GitHub. The Admin dashboard opens with the **Admin** button in the top bar.

**Live URL:** [aitrustlayerprototype-202608.streamlit.app](https://aitrustlayerprototype-202608.streamlit.app/)

**Static mirror (GitHub Pages, no setup required):** [blueruins42.github.io/AI_Trust_Layer_prototype](https://blueruins42.github.io/AI_Trust_Layer_prototype/) — a fully interactive HTML build covering all four answer states, the Admin dashboard, and the document-verification views. Useful when the Streamlit app is unavailable.

## What a reviewer gets in one URL
- **Live demo** — the real AI Trust Layer prototype, running offline in `MOCK_LLM_MODE`.
- **Portfolio** — problem → solution → principles → decisions, presented as a coherent story rather than a pile of features.
- **Source & docs** — the top-right GitHub icon links to the repository, where the full PRD and HCI design notes live.

## Prerequisites
- A GitHub account.
- A Streamlit account (free; sign in with GitHub at https://streamlit.io/cloud).

## Steps
1. **Push this folder to your GitHub repo** (`AI_Trust_Layer_prototype`):
   ```bash
   git remote add origin https://github.com/blueruins42/AI_Trust_Layer_prototype.git
   git push -u origin master
   ```
2. Go to **streamlit.io/cloud → New app** → connect GitHub → select the repo, branch `master`, and **Main file path: `ai_trust_layer/app.py`**.
3. **Advanced settings → Python version:** 3.12. **No secrets required** — `MOCK_LLM_MODE` defaults to `true`, so the demo runs with zero API keys.
   - To enable live OpenAI answers instead, add a secret `OPENAI_API_KEY=...` and set `MOCK_LLM_MODE=false` (via `.env` locally, or Streamlit secrets in the cloud UI).
4. **Deploy.** Your app goes live at `https://<app-name>.streamlit.app`.

## Notes
- `requirements.txt` (repo root) pins the exact stack.
- `.streamlit/config.toml` carries the brand theme (primary `#014DB2`). A copy also lives at `ai_trust_layer/.streamlit/config.toml` for local runs.
- `.env` is git-ignored; `.env.example` is committed as a template.
- `mock_documents/` (10 simulated project documents) must stay committed — the demo retrieves from them.
- The repository is intentionally English-only; the Chinese PRD source files are kept outside the public repo.

## Run locally
```bash
cd ai_trust_layer
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env        # MOCK_LLM_MODE=true by default
streamlit run app.py        # http://localhost:8501
```
