# Deploying AI Trust Layer — Streamlit Community Cloud

This repository runs as a **single, self-contained portfolio + design document + live demo** on Streamlit Community Cloud (free). The interactive PRD panel lives in the right-hand column (toggle it with the **PRD ▸** button in the top bar); the Admin dashboard opens with the **Admin** button.

## What a reviewer gets in one URL
- **Live demo** — the real AI Trust Layer prototype, running offline in `MOCK_LLM_MODE`.
- **Design document** — the PRD narrative + HCI design philosophy, navigable inside the app (Overview / Problem / Solution / Principles / Decisions / Demo).
- **Portfolio** — problem → solution → principles → decisions, presented as a coherent story rather than a pile of features.

## Prerequisites
- A GitHub account.
- A Streamlit account (free; sign in with GitHub at https://streamlit.io/cloud).

## Steps
1. **Create a GitHub repo** (e.g. `ai_trust_layer_prototype`) and push this folder:
   ```bash
   git remote add origin https://github.com/<you>/ai_trust_layer_prototype.git
   git push -u origin master
   ```
2. **(Optional)** In `ai_trust_layer/app.py`, replace `<YOUR_GITHUB_USERNAME>` in `REPO_URL` with your handle, so the top-right GitHub icon links home.
3. Go to **streamlit.io/cloud → New app** → connect GitHub → select the repo, branch `master`, and **Main file path: `ai_trust_layer/app.py`**.
4. **Advanced settings → Python version:** 3.12. **No secrets required** — `MOCK_LLM_MODE` defaults to `true`, so the demo runs with zero API keys.
   - To enable live OpenAI answers instead, add a secret `OPENAI_API_KEY=...` and set `MOCK_LLM_MODE=false` (via `.env` locally, or Streamlit secrets in the cloud UI).
5. **Deploy.** Your app goes live at `https://<app-name>.streamlit.app`.

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
