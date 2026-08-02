"""
prd_panel.py - Interactive PRD + design-rationale sidebar for the AI Trust Layer.

This right-column panel (opens on demand from the top "PRD" toggle, or via a
prototype chip) turns the running prototype into a portfolio + design document +
live demo in one place. It is a structured, navigable DISTILLATION of the full
PRD (Step 1-5) and the HCI design philosophy - not the raw documents.

Two-way linking:
  - Left -> Right: a prototype chip sets `_prd_focus` + opens this panel at the
    Solution section (see frontend.py) so the matching card highlights.
  - Right -> Left: a "Run this scenario" button here runs the matching demo;
    the Admin card switches to the Admin view.
"""

import streamlit as st
from frontend import _handle_query, SCENARIO_QUERIES


# (card_id, title, body_html, demo_scenario)
# demo_scenario must be a key in SCENARIO_QUERIES (high / medium / low), or None for admin.
# Titles carry the PRD feature ID (F1-F4, F7) and the persona who owns that view.
_SCENARIO_CARDS = [
    (
        "high",
        "F1 &#183; Source Citation",
        "From Li Ming&#8217;s view: every answer carries a structured contract &#8212; source "
        "document, page, match score, and excerpt. The Pydantic schema enforces confidence, sources, "
        "jargon, and verification advice, so the interface never guesses what to show. High-confidence "
        "answers surface directly from matching documents.",
        "high",
    ),
    (
        "low",
        "F2 &#183; Confidence &amp; Alert",
        "From Li Ming&#8217;s view: trust is calibrated, not assumed. A three-tier score (High / "
        "Medium / Low) and fixed thresholds decide when the answer stands alone, when it recommends "
        "verification, and when it blocks with a manual-check alert. Low confidence is the only state "
        "that proactively warns.",
        "low",
    ),
    (
        "medium",
        "F3&#8211;F4 &#183; Jargon &amp; Verification",
        "From Li Ming&#8217;s view: dense technical detail lives one click away. The Details expander "
        "reveals sources, a jargon glossary, and verification advice only when wanted. Jargon "
        "auto-translates to plain language; the formal definition nests one tap deeper. Every answer "
        "ends with a clear &#8220;verify yourself&#8221; action link.",
        "medium",
    ),
    (
        "admin",
        "F7 &#183; Admin Dashboard",
        "From Wang Fang&#8217;s view: the system learns from interaction patterns &#8212; verification "
        "click-through rate, low-confidence triggers, and the most-viewed jargon. These signals help "
        "teams close knowledge gaps rather than blindly trusting the model.",
        None,
    ),
]


def _section_title(eyebrow, title):
    st.markdown(
        f'<p style="color:#3B82F6; font-size:11px; font-weight:600; letter-spacing:1.2px; '
        f'text-transform:uppercase; margin:0 0 4px 0;">{eyebrow}</p>'
        f'<h3 style="font-size:17px; font-weight:800; color:#0A0A0B; margin:0 0 12px 0;">{title}</h3>',
        unsafe_allow_html=True,
    )


def _para(text):
    st.markdown(
        f'<p style="color:#52525B; font-size:13px; line-height:1.6; margin:0 0 12px 0;">{text}</p>',
        unsafe_allow_html=True,
    )


def _bullet(items):
    lis = "".join(f'<li style="margin:0 0 6px 0;">{it}</li>' for it in items)
    st.markdown(
        f'<ul style="color:#52525B; font-size:13px; line-height:1.55; margin:0 0 12px 0; '
        f'padding-left:18px;">{lis}</ul>',
        unsafe_allow_html=True,
    )


def _render_toc():
    cur = st.session_state.get("_prd_section", "overview")
    r1 = st.columns(3)
    r2 = st.columns(3)
    pairs = [
        ("overview", "Overview", r1[0]),
        ("problem", "Problem", r1[1]),
        ("solution", "Solution", r1[2]),
        ("principles", "Principles", r2[0]),
        ("decisions", "Decisions", r2[1]),
        ("demo", "Explore", r2[2]),
    ]
    for key, label, col in pairs:
        active = cur == key
        with col:
            if st.button(
                label,
                key=f"toc_{key}",
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                st.session_state["_prd_section"] = key
                st.rerun()


def _render_overview():
    _section_title("Product Vision", "AI Trust Layer")
    _para(
        "Enable non-technical users not only to <strong>receive</strong> AI answers, but to "
        "<strong>understand, trust, and effectively use</strong> them."
    )
    _para(
        "It is a <strong>trust interface layer</strong> attached to the output end of a RAG system. "
        "It does not change the AI&#8217;s &#8220;brain&#8221; (model capability) &#8212; it "
        "redesigns the &#8220;face&#8221; of AI output so people can act on it."
    )
    _section_title("What It Enables", "Five Capabilities")
    _bullet(
        [
            "<strong>See the sources</strong> &#8212; know which page of which document each answer comes from.",
            "<strong>Perceive confidence</strong> &#8212; tell a high-confidence fact from low-confidence speculation.",
            "<strong>Understand jargon</strong> &#8212; translate engineering language into the user&#8217;s working language.",
            "<strong>Calibrate trust</strong> &#8212; know when to use directly and when human verification is required.",
            "<strong>Close the loop</strong> &#8212; let admins see trust health and continuously improve.",
        ]
    )
    _section_title("What it is &#8212; and isn&#8217;t", "Scope")
    _bullet(
        [
            "<strong>IS</strong> an interface-layer component on the RAG output end.",
            "<strong>IS NOT</strong> a standalone assistant or an answer-quality improver.",
            "<strong>IS</strong> trust presentation design + data contract + progressive disclosure.",
            "<strong>IS NOT</strong> a RAG retrieval algorithm or LLM training work.",
        ]
    )
    _para(
        "Positioning: the <em>translator and trust anchor for AI output</em> &#8212; the last mile "
        "from &#8220;technical success&#8221; to &#8220;user adoption.&#8221;"
    )


def _render_problem():
    _section_title("Problem Definition", "The Trust &amp; Comprehension Gap")
    _para(
        "Enterprise RAG systems deliver confident answers, but for the people who act on them there is "
        "no signal of <em>when</em> to trust and <em>when</em> to verify. We formalised four gaps:"
    )
    _bullet(
        [
            "<strong>Source Opacity</strong> &#8212; no citations; users can&#8217;t tell an "
            "authoritative document from model inference. &#8594; trust cannot form.",
            "<strong>Confidence Opacity</strong> &#8212; every answer looks equally certain; fact and "
            "speculation are indistinguishable. &#8594; trust all, or trust nothing.",
            "<strong>Trust Calibration Gap</strong> &#8212; the system never says &#8220;trust me now / "
            "verify yourself.&#8221; &#8594; trust stays binary, not calibrated.",
            "<strong>Cognitive Translation Gap</strong> &#8212; jargon users don&#8217;t understand; "
            "format ignores their workflow. &#8594; even correct info goes unused.",
        ]
    )
    _para(
        "<strong>Key insight:</strong> a technically perfect system failed completely on the user side. "
        "The problem was never model capability &#8212; it was that users could not understand, trust, "
        "and use the output."
    )


def _render_solution():
    _section_title("The Solution", "Five Trust Features")
    _para(
        "Five interface features close the gap. The four cards below are interactive &#8212; run a "
        "scenario, or click a prototype chip and this panel opens right here, highlighted."
    )
    focused = st.session_state.get("_prd_focus")
    for sid, title, body, scenario in _SCENARIO_CARDS:
        _scenario_card(sid, title, body, scenario, focused == sid)


def _scenario_card(sid, title, body, scenario, is_focus):
    bg = "#EFF4FF" if is_focus else "#FFFFFF"
    border = "#014DB2" if is_focus else "#E4E4E7"
    shadow = "0 4px 14px rgba(1,77,178,0.12)" if is_focus else "0 2px 8px rgba(1,77,178,0.06)"
    st.markdown(
        f'<div style="background:{bg}; border:1px solid {border}; border-radius:12px; '
        f'padding:13px 15px; margin-bottom:12px; box-shadow:{shadow};">',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<strong style="font-size:14px; color:#0A0A0B;">{title}</strong>',
        unsafe_allow_html=True,
    )
    if is_focus:
        st.markdown(
            '<span style="color:#014DB2; font-size:11px; font-weight:600; display:block; '
            'margin:2px 0 6px 0;">&#9679; Highlighted from prototype</span>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div style="color:#52525B; font-size:12.5px; line-height:1.55; margin:6px 0 10px 0;">'
        f"{body}</div>",
        unsafe_allow_html=True,
    )
    if scenario is None:
        if st.button("&#9654; Open Admin Dashboard", key=f"prd_run_{sid}", use_container_width=True):
            st.session_state["_prd_focus"] = sid
            st.session_state["view_mode"] = "admin"
            st.rerun()
    else:
        if st.button("&#9654; Run this scenario", key=f"prd_run_{sid}", use_container_width=True):
            st.session_state["_prd_focus"] = sid
            _handle_query(SCENARIO_QUERIES[scenario])
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _principle(num, title, body, anchor):
    st.markdown(
        f'<div style="border-left:3px solid #3B82F6; padding:2px 0 2px 12px; margin-bottom:14px;">'
        f'<div style="font-size:13px; font-weight:700; color:#0A0A0B; margin-bottom:3px;">'
        f"{num}. {title}</div>"
        f'<div style="color:#52525B; font-size:12.5px; line-height:1.55; margin-bottom:4px;">{body}</div>'
        f'<div style="color:#014DB2; font-size:11px; font-weight:600; letter-spacing:0.3px;">{anchor}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_principles():
    _section_title("Design Principles", "Five HCI Anchors")
    _principle(
        "1",
        "Progressive Disclosure",
        "Minimal by default, expand on demand. Default view shows &#8804;3 elements "
        "(answer + confidence + details). Low confidence is the only state that proactively "
        "pops an alert.",
        "Nielsen heuristic &#183; cuts cognitive load",
    )
    _principle(
        "2",
        "Calibration, Not Replacement",
        "Tell users <em>when</em> to trust, never decide for them. Three tiers with differentiated "
        "presentation and clear action guidance (use / verify / reference-only).",
        "Trust Calibration (Lee &amp; See, 2004)",
    )
    _principle(
        "3",
        "Plain Language First",
        "Speak the user&#8217;s language. Jargon shows its plain version by default; the formal "
        "definition nests one tap deeper. Every copy passes a &#8220;38-year-old specialist&#8221; "
        "readability test.",
        "Cognitive Load Theory (Sweller)",
    )
    _principle(
        "4",
        "Structured Data Contract",
        "Frontend and backend talk JSON Schema, not natural-language guessing. Every answer is "
        "structured (confidence, sources, jargon, verification) &#8212; the UI never infers.",
        "Explainable AI (XAI)",
    )
    _principle(
        "5",
        "Human-AI Co-evolution Loop",
        "Not a one-way tool: the Admin view exposes trust health, and every verification click "
        "is a signal for system improvement.",
        "Human-in-the-Loop",
    )


def _render_decisions():
    _section_title("Key Decisions", "Why This, Not That")
    _para(
        "<strong>Stack:</strong> Streamlit (pure Python, no HTML/CSS/JS) + OpenAI structured output "
        "+ Pydantic validation + an in-memory interaction log + a mock document store. Streamlit is "
        "the fastest path to a runnable, reviewable prototype."
    )
    _para(
        "<strong>Scope discipline:</strong> the MVP is deliberately tight. Explicitly deferred to V2 "
        "&#8212; F5 format adaptation, F6 full interaction log, F8 full trust-health, F9 jargon "
        "heatmap, N3 cost optimization, authentication, and multilingual support. Scope creep was the "
        "#1 project risk, so exclusion is the rule."
    )
    _para(
        "<strong>Bulletproof mock mode:</strong> <code>MOCK_LLM_MODE</code> returns deterministic "
        "static JSON at 0&#8201;ms with no API key. The prototype is always reviewable &#8212; and "
        "deployable to the cloud with zero secrets."
    )
    _para(
        "<strong>Latency model:</strong> a single request returns the full structured answer in "
        "&#8804;2s (N1 decision, Option A); detail expansion is instant because the data is already "
        "in memory. This replaced the earlier two-request progressive-loading sketch."
    )
    _para(
        "<strong>Data contract:</strong> every answer is structured (confidence, sources, jargon, "
        "verification advice). The interface renders by field, so behaviour is deterministic and "
        "testable."
    )


def _render_demo():
    _section_title("Using the Prototype", "How To Explore")
    _para(
        "The app runs in <strong>mock mode</strong> by default &#8212; no API key, fully offline and "
        "deterministic. Explore the three confidence scenarios below:"
    )
    _bullet(
        [
            "<strong>High confidence</strong> &#8212; &#8220;What signaling system does Project XX "
            "use?&#8221; Green label, collapsed details, clean sources.",
            "<strong>Medium confidence</strong> &#8212; &#8220;ZDJ-200 switch machine parameters&#8221; "
            "Yellow label, auto-expanded sources, collapsed jargon.",
            "<strong>Low confidence</strong> &#8212; &#8220;YY Line construction budget&#8221; "
            "Red alert banner, action link, inferred answer.",
        ]
    )
    _bullet(
        [
            "Toggle this panel with the top-right <strong>PRD &#9656;</strong> button.",
            "Switch to the <strong>Admin</strong> view (top-right) to see trust health.",
            "Type a query and press Enter, or tap a chip to quick-run a scenario.",
        ]
    )


def render_prd_panel():
    """Render the interactive PRD + design-rationale panel (right column)."""
    st.markdown(
        '<div style="border-bottom:1px solid #E4E4E7; margin-bottom:12px; padding-bottom:8px;">'
        '<p style="color:#3B82F6; font-size:11px; font-weight:600; letter-spacing:1.2px; '
        'text-transform:uppercase; margin:0 0 4px 0;">Design Document</p>'
        '<h3 style="font-size:18px; font-weight:800; color:#0A0A0B; margin:0;">AI Trust Layer</h3></div>',
        unsafe_allow_html=True,
    )
    _render_toc()
    section = st.session_state.get("_prd_section", "overview")
    if section == "problem":
        _render_problem()
    elif section == "solution":
        _render_solution()
    elif section == "principles":
        _render_principles()
    elif section == "decisions":
        _render_decisions()
    elif section == "demo":
        _render_demo()
    else:
        _render_overview()
