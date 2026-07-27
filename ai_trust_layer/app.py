"""
app.py - AI Trust Layer Streamlit Entry Point

Responsibilities: Page routing, session_state initialization, frontend/backend toggle
Corresponds to: PRD Step 5.2.1 + Step 5.7 Session State Architecture

Run: streamlit run app.py
"""

import streamlit as st
from frontend import render_frontend
from admin import render_admin
from prd_panel import render_prd_panel
from interaction_log import init_log, InteractionLogEntry
from models import ConfidenceLevel
from datetime import datetime

# Public source repository for this prototype.
# REPLACE <YOUR_GITHUB_USERNAME> with your GitHub handle before deploying.
# Streamlit Community Cloud derives the app URL from the repo name:
#   repo "ai_trust_layer_prototype" -> https://ai-trust-layer-prototype.streamlit.app
REPO_URL = "https://github.com/<YOUR_GITHUB_USERNAME>/ai_trust_layer_prototype"


def init_session_state():
    """
    Initialize all session_state variables.
    Corresponds to Step 5.7 Session State Architecture.
    """
    # --- Routing control ---
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "front"
    if "doc_view" not in st.session_state:
        st.session_state["doc_view"] = None

    # --- Interactive PRD panel state ---
    if "prd_open" not in st.session_state:
        st.session_state["prd_open"] = False
    if "_prd_focus" not in st.session_state:
        st.session_state["_prd_focus"] = None

    # --- Current response ---
    if "current_response" not in st.session_state:
        st.session_state["current_response"] = None
    if "current_query" not in st.session_state:
        st.session_state["current_query"] = ""

    # --- Interaction log ---
    init_log()

    # --- Demo-data seed gate (Path A) ---
    # `demo_data_cleared` is set True when the user clicks "Clear demo data" in Admin,
    # so the auto-seed below does NOT refill on the next rerun — making the empty-state
    # acceptance criterion reproducible on demand. `_request_seed` is set by Admin's
    # "Restore demo data" button and processed here (avoids a circular import).
    if "demo_data_cleared" not in st.session_state:
        st.session_state["demo_data_cleared"] = False
    if st.session_state.get("_request_seed"):
        _seed_log_data()
        st.session_state["demo_data_cleared"] = False
        st.session_state["_request_seed"] = False

    # Seed data (Step 6 requirement: ensure Admin Dashboard has data when toggled).
    # Only when the log is empty AND the user has not explicitly cleared it — this keeps
    # the impressive default dashboard while still allowing the empty state to be shown.
    if not st.session_state["interaction_log"] and not st.session_state["demo_data_cleared"]:
        _seed_log_data()


def _seed_log_data():
    """
    Pre-fill seed log entries covering high/medium/low confidence + verification clicks + varied jargon views.
    Enriches the distribution so Admin Dashboard charts (trend / donut / term-frequency) read as a credible
    monitoring view during demo. Frontend P0 visuals are untouched.
    """
    from interaction_log import InteractionLogEntry

    seeds = [
        InteractionLogEntry(
            query_id="seed-001", timestamp="2026-07-24T09:55:00",
            user_query="What signaling system does Project XX use?",
            confidence_level="high", response_time_ms=1200,
            viewed_details=True, viewed_jargon=["CBTC"],
            clicked_verification=False, documents_searched=10, documents_matched=2,
        ),
        InteractionLogEntry(
            query_id="seed-002", timestamp="2026-07-24T09:58:00",
            user_query="What are the technical parameters of ZDJ-200 switch machine?",
            confidence_level="medium", response_time_ms=1500,
            viewed_details=True, viewed_jargon=["CBTC", "Electric Switch Machine", "Switching Force"],
            clicked_verification=True, documents_searched=10, documents_matched=2,
        ),
        InteractionLogEntry(
            query_id="seed-003", timestamp="2026-07-24T10:01:00",
            user_query="What is the construction budget for YY Line?",
            confidence_level="low", response_time_ms=950,
            viewed_details=True, viewed_jargon=["Low-Voltage Integration"],
            clicked_verification=True, documents_searched=10, documents_matched=1,
        ),
        InteractionLogEntry(
            query_id="seed-004", timestamp="2026-07-24T10:05:00",
            user_query="What signaling system does Project XX use?",
            confidence_level="high", response_time_ms=1180,
            viewed_details=True, viewed_jargon=["CBTC"],
            clicked_verification=False, documents_searched=10, documents_matched=2,
        ),
        InteractionLogEntry(
            query_id="seed-005", timestamp="2026-07-24T10:09:00",
            user_query="What are the technical parameters of ZDJ-200 switch machine?",
            confidence_level="medium", response_time_ms=1420,
            viewed_details=True, viewed_jargon=["Electric Switch Machine"],
            clicked_verification=False, documents_searched=10, documents_matched=2,
        ),
        InteractionLogEntry(
            query_id="seed-006", timestamp="2026-07-24T10:14:00",
            user_query="What is the construction budget for YY Line?",
            confidence_level="low", response_time_ms=980,
            viewed_details=True, viewed_jargon=["Low-Voltage Integration", "Traction Power Supply"],
            clicked_verification=True, documents_searched=10, documents_matched=1,
        ),
        InteractionLogEntry(
            query_id="seed-007", timestamp="2026-07-24T10:20:00",
            user_query="What signaling system does Project XX use?",
            confidence_level="high", response_time_ms=1150,
            viewed_details=True, viewed_jargon=["CBTC"],
            clicked_verification=False, documents_searched=10, documents_matched=2,
        ),
    ]

    st.session_state["interaction_log"] = seeds
    st.session_state["query_count"] = len(seeds)
    # Jargon view tally mirrors the per-query viewed_jargon above (descending distribution).
    st.session_state["jargon_views"] = {
        "CBTC": 4, "Electric Switch Machine": 3, "Low-Voltage Integration": 2,
        "Switching Force": 1, "Traction Power Supply": 1,
    }
    st.session_state["verification_clicks"] = sum(1 for e in seeds if e.clicked_verification)


def main():
    """
    Main function:
    1. st.set_page_config(title, icon, layout)
    2. init_session_state()
    3. Render frontend or admin based on view_mode
    4. Provide toggle button
    """
    st.set_page_config(
        page_title="AI Trust Layer",
        page_icon="🛡️",
        layout="wide",
    )

    # Load Inter so the design's font stack renders deterministically and matches the
    # static preview. Falls back to the system sans-serif if offline.
    st.markdown(
        '<link rel="stylesheet" '
        'href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">',
        unsafe_allow_html=True,
    )

    init_session_state()

    # Top navigation bar (design-system consistent — small SVG shield + wordmark + admin pill)
    # Top navigation bar: logo | PRD toggle | GitHub icon | Admin/Frontend switch
    nav_left, nav_prd, nav_github, nav_right = st.columns([3, 0.8, 0.5, 1])

    with nav_left:
        st.markdown(
            '<div style="display:flex; align-items:center; gap:10px; padding:4px 0;">'
            '<svg width="28" height="28" viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg">'
            '<circle cx="14" cy="14" r="14" fill="#014DB2"/>'
            '<path d="M9 14l3 3 6-6" stroke="#FFFFFF" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg>'
            '<span style="color:#0A0A0B; font-size:18px; font-weight:600;">AI Trust Layer</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    with nav_prd:
        label = "PRD ▸" if not st.session_state.get("prd_open") else "PRD ◂"
        if st.button(label, key="prd_toggle", type="secondary", use_container_width=True):
            st.session_state["prd_open"] = not st.session_state.get("prd_open", False)
            st.rerun()

    with nav_github:
        st.markdown(
            f'<a href="{REPO_URL}" target="_blank" rel="noopener noreferrer" '
            f'title="View source on GitHub" '
            f'style="display:flex; justify-content:flex-end; align-items:center; height:38px;">'
            f'<svg height="22" width="22" viewBox="0 0 16 16" fill="#0A0A0B" '
            f'aria-label="GitHub repository" role="img" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 '
            f'0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53'
            f'.63-.01 1.22.47 1.36.58.78 1.21 2.05.87 2.55.66.01-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 '
            f'0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 '
            f'1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 '
            f'3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8'
            f'c0-4.42-3.58-8-8-8z"></path></svg></a>',
            unsafe_allow_html=True,
        )

    with nav_right:
        if st.session_state["view_mode"] == "front":
            if st.button("Admin", key="nav_switch", type="secondary", use_container_width=True):
                st.session_state["view_mode"] = "admin"
                st.rerun()
        else:
            if st.button("Frontend", key="nav_switch", type="secondary", use_container_width=True):
                st.session_state["view_mode"] = "front"
                st.rerun()

    st.divider()

    # Routing - split into app + PRD panel when the PRD is open; full-width otherwise.
    if st.session_state.get("prd_open"):
        app_col, prd_col = st.columns([2.5, 1])
        with app_col:
            if st.session_state["view_mode"] == "front":
                render_frontend()
            else:
                render_admin()
        with prd_col:
            render_prd_panel()
    else:
        if st.session_state["view_mode"] == "front":
            render_frontend()
        else:
            render_admin()


if __name__ == "__main__":
    main()
