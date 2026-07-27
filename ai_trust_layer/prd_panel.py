"""
prd_panel.py - Interactive PRD sidebar for the AI Trust Layer prototype.

Renders a minimal-core product requirements document beside the live app.
Two-way linking:
  - Left -> Right: a prototype chip sets `_prd_focus` + opens this panel (see frontend.py)
  - Right -> Left: a "Run this scenario" button here runs the matching demo scenario
The card whose section id matches `st.session_state["_prd_focus"]` is highlighted.
"""

import streamlit as st
from frontend import _handle_query, SCENARIO_QUERIES


# (section_id, title, body_html, demo_scenario)
# demo_scenario must be a key in SCENARIO_QUERIES (high / medium / low).
_PRD_SECTIONS = [
    (
        "pain",
        "Pain Points",
        "Enterprise RAG answers arrive with no signal of whether to trust them. "
        "Users can&#8217;t see the source, can&#8217;t tell a confident fact from an inferred guess, "
        "and have no safe path when the answer is wrong. One bad answer erodes trust in the whole system.",
        "low",
    ),
    (
        "solution",
        "Solution",
        "The AI Trust Layer wraps every answer with source transparency "
        "(cited document, page, and match score) and a clear confidence label. "
        "Trust becomes traceable and legible at a glance &#8212; you always know where the "
        "answer came from and how much to rely on it.",
        "high",
    ),
    (
        "confidence",
        "Confidence Mechanism",
        "A three-tier calibration &#8212; High / Medium / Low &#8212; plus progressive disclosure. "
        "High needs no action; Medium recommends verification; Low blocks on a manual-check gate. "
        "Technical jargon auto-translates to plain language, with formal definitions one tap away.",
        "medium",
    ),
]


def render_prd_panel():
    """Render the interactive PRD panel (right column)."""
    # Panel header
    st.markdown(
        '<div style="border-bottom:1px solid #E4E4E7; margin-bottom:14px; padding-bottom:8px;">'
        '<p style="color:#3B82F6; font-size:11px; font-weight:600; letter-spacing:1.2px; '
        'margin:0 0 4px 0; text-transform:uppercase;">Product Requirements</p>'
        '<h3 style="font-size:18px; font-weight:800; color:#0A0A0B; margin:0;">AI Trust Layer</h3></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#71717A; font-size:12px; margin:0 0 14px 0; line-height:1.5;">'
        'Click a section to run its demo scenario on the left. Or click a prototype chip &#8212; '
        'this panel opens and the matching requirement highlights automatically.</p>',
        unsafe_allow_html=True,
    )

    focused = st.session_state.get("_prd_focus")

    for sid, title, body, scenario in _PRD_SECTIONS:
        is_focus = focused == sid
        bg = "#EFF4FF" if is_focus else "#FFFFFF"
        border = "#014DB2" if is_focus else "#E4E4E7"
        box_shadow = (
            "0 4px 14px rgba(1,77,178,0.12)" if is_focus else "0 2px 8px rgba(1,77,178,0.06)"
        )

        st.markdown(
            f'<div style="background:{bg}; border:1px solid {border}; border-radius:12px; '
            f'padding:14px 16px; margin-bottom:14px; box-shadow:{box_shadow};">',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<strong style="font-size:15px; color:#0A0A0B;">{title}</strong>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="color:#52525B; font-size:13px; line-height:1.6; margin:8px 0 12px 0;">{body}</div>',
            unsafe_allow_html=True,
        )
        if st.button("▶ Run this scenario", key=f"prd_run_{sid}", use_container_width=True):
            st.session_state["_prd_focus"] = sid
            _handle_query(SCENARIO_QUERIES[scenario])
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
