"""
app.py - AI Trust Layer Streamlit Entry Point

Responsibilities: Page routing, session_state initialization, frontend/backend toggle
Corresponds to: PRD Step 5.2.1 + Step 5.7 Session State Architecture

Run: streamlit run app.py
"""

import streamlit as st
from frontend import render_frontend
from admin import render_admin
from interaction_log import init_log, InteractionLogEntry
from models import ConfidenceLevel
from datetime import datetime


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

    # --- Current response ---
    if "current_response" not in st.session_state:
        st.session_state["current_response"] = None
    if "current_query" not in st.session_state:
        st.session_state["current_query"] = ""

    # --- Interaction log ---
    init_log()

    # --- Seed data (Step 6 requirement: ensure Admin Dashboard has data when toggled) ---
    if not st.session_state["interaction_log"]:
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
    nav_left, nav_right = st.columns([3, 1])
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

    # Routing
    if st.session_state["view_mode"] == "front":
        render_frontend()
    else:
        render_admin()


if __name__ == "__main__":
    main()
