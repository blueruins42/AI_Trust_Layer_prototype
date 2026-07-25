"""
frontend.py - Frontend Trust Interface Rendering (Li Ming's view)

Responsibilities: Render F1-F4 + low-confidence alert + progressive disclosure
Corresponds to: PRD Step 4.2-4.5 + Step 4.8 + Step 5.2.6

Bug fixes already built in:
- Bug 1: Never use st.button to control expand/collapse, use st.expander (persistent state control)
- Bug 2: Never use "half-expanded" concept, use dual expander strategy (sources expanded=True + jargon expanded=False)
"""

import streamlit as st
from models import TrustLayerResponse, ConfidenceLevel
from llm_api import call_llm_api
from interaction_log import (
    log_interaction,
    update_jargon_view,
    update_verification_click,
    update_details_viewed,
)
from mock_docs import get_document_page


def _inject_expander_css():
    """
    Style Streamlit expanders to match the trust-layer design system.
    Applied globally on the frontend page; Admin has no expanders, so unaffected.
    """
    st.markdown(
        """
        <style>
        .streamlit-expanderHeader {
            background-color: #FFFFFF !important;
            border: 1px solid #E4E4E7 !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            color: #0A0A0B !important;
        }
        .streamlit-expanderContent {
            background-color: #FFFFFF !important;
            border: 1px solid #E4E4E7 !important;
            border-top: none !important;
            border-radius: 0 0 12px 12px !important;
            padding: 24px !important;
        }

        /* Search input: single gray rounded border when idle.
           On focus the gray border becomes blue (design blue) with a soft glow — applied to the
           visible baseweb box so there is NEVER a double (gray + blue) border. */
        div[data-baseweb="input"] {
            border: 1px solid #E4E4E7 !important;
            border-radius: 12px !important;
            box-shadow: none !important;
        }
        div[data-baseweb="input"]:focus-within {
            border: 1px solid #3B82F6 !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
        }
        /* Neutralize the inner <input> so it never draws a second border on top of the box above. */
        .stTextInput input,
        .stTextInput input:focus {
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_frontend():
    """
    Frontend main render function — REDESIGNED (2026-07-25) with onboarding layer.
    Hero: value proposition + search + example chips + value cards.
    See 08_Design_Implementation_Notes.md §2 for design rationale.
    """
    _inject_expander_css()

    # If in document view mode, render document view
    if st.session_state.get("doc_view"):
        render_document_view(
            st.session_state["doc_view"]["doc_name"],
            st.session_state["doc_view"]["page"],
        )
        return

    # ── Hero / Onboarding layer (centered) ──
    st.markdown(
        '<div style="text-align:center; max-width:820px; margin:0 auto 24px auto;">'
        '<p style="color:#3B82F6; font-size:13px; font-weight:600; letter-spacing:1.5px; margin:0 0 10px 0;">TRUST INTERFACE FOR ENTERPRISE RAG</p>'
        '<h1 style="font-size:52px; font-weight:900; color:#0A0A0B; margin:0 0 14px 0; letter-spacing:-1.5px; line-height:1.05;">Every AI answer,<br>accountable.</h1>'
        '<p style="color:#52525B; font-size:18px; margin:0; line-height:1.5;">See where it comes from. Know how much to trust it. Verify when it matters.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Search box + button on the same row, centered (~50% width)
    _, search_center, _ = st.columns([1, 2, 1])
    with search_center:
        search_col, btn_col = st.columns([4, 1])
        with search_col:
            user_query = st.text_input(
                "Ask anything about your project documents:",
                placeholder="Ask anything about your project documents...",
                key="query_input",
                label_visibility="collapsed",
            )
        with btn_col:
            if st.button("Search", type="primary", use_container_width=True):
                if user_query.strip():
                    _handle_query(user_query.strip())
                else:
                    st.warning("Please enter a query")

    # Example query chips (centered)
    st.markdown(
        '<p style="color:#A1A1AA; font-size:12px; text-align:center; margin:20px 0 10px 0;">Try one of these:</p>',
        unsafe_allow_html=True,
    )
    _, chips_center, _ = st.columns([1, 2, 1])
    with chips_center:
        chip_cols = st.columns(3)
        examples = [
            "What signaling system does Project XX use?",
            "ZDJ-200 switch machine parameters",
            "YY Line construction budget",
        ]
        for col, example in zip(chip_cols, examples):
            with col:
                if st.button(example, key=f"chip_{example[:10]}", use_container_width=True):
                    _handle_query(example)

    # Value cards (only show when no current response, to keep focus on answer when querying)
    if not st.session_state.get("current_response"):
        st.markdown("---")
        st.markdown(
            '<p style="color:#3B82F6; font-size:13px; font-weight:600; letter-spacing:1.5px; margin-bottom:20px;">WHY TEAMS TRUST THIS LAYER</p>',
            unsafe_allow_html=True,
        )
        # Three value cards with inline SVG icons (matching the ardot design)
        card1, card2, card3 = st.columns(3)
        with card1:
            st.markdown(
                """
                <div style="background:#FFFFFF; border-radius:16px; padding:24px; border:1px solid #E4E4E7; box-shadow:0 2px 8px rgba(1,77,178,0.06); height:100%;">
                    <div style="width:44px; height:44px; border-radius:12px; background:#EFF6FF; display:flex; align-items:center; justify-content:center; margin-bottom:14px;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M14 3v5h5" stroke="#3B82F6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-5z" stroke="#3B82F6" stroke-width="1.8" stroke-linejoin="round"/>
                            <path d="M9 14l2 2 4-4" stroke="#3B82F6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <div style="color:#0A0A0B; font-size:20px; font-weight:700; margin-bottom:8px;">Source Transparency</div>
                    <div style="color:#52525B; font-size:15px; line-height:1.55;">Every answer cites its source document, page number, and match score — so trust is always traceable.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with card2:
            st.markdown(
                """
                <div style="background:#FFFFFF; border-radius:16px; padding:24px; border:1px solid #E4E4E7; box-shadow:0 2px 8px rgba(1,77,178,0.06); height:100%;">
                    <div style="width:44px; height:44px; border-radius:12px; background:#ECFDF5; display:flex; align-items:center; justify-content:center; margin-bottom:14px;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M4 18a8 8 0 0 1 16 0" stroke="#10B981" stroke-width="1.8" stroke-linecap="round"/>
                            <path d="M12 13l4-4" stroke="#10B981" stroke-width="1.8" stroke-linecap="round"/>
                            <circle cx="12" cy="13" r="1.6" fill="#10B981"/>
                        </svg>
                    </div>
                    <div style="color:#0A0A0B; font-size:20px; font-weight:700; margin-bottom:8px;">Confidence Calibration</div>
                    <div style="color:#52525B; font-size:15px; line-height:1.55;">Three-tier labels (High / Medium / Low) tell you when to trust freely, and when to slow down and verify.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with card3:
            st.markdown(
                """
                <div style="background:#FFFFFF; border-radius:16px; padding:24px; border:1px solid #E4E4E7; box-shadow:0 2px 8px rgba(1,77,178,0.06); height:100%;">
                    <div style="width:44px; height:44px; border-radius:12px; background:#FFFBEB; display:flex; align-items:center; justify-content:center; margin-bottom:14px;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M21 12a8 8 0 0 1-12 7l-5 1 1-4a8 8 0 1 1 16-4z" stroke="#F59E0B" stroke-width="1.8" stroke-linejoin="round"/>
                            <path d="M9 11h6M9 14h3" stroke="#F59E0B" stroke-width="1.8" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <div style="color:#0A0A0B; font-size:20px; font-weight:700; margin-bottom:8px;">Plain Language, On Demand</div>
                    <div style="color:#52525B; font-size:15px; line-height:1.55;">Technical jargon auto-translates to plain language. Formal definitions stay one tap away — never in the way.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Portfolio footer
        st.markdown(
            '<p style="color:#A1A1AA; font-size:13px; text-align:center; margin-top:40px;">'
            'Built for enterprise RAG systems  ·  Designed by Shuting Fan  ·  MSc Interaction & Experience Design Portfolio'
            '</p>',
            unsafe_allow_html=True,
        )

    # Render current response (if any)
    if st.session_state.get("current_response"):
        st.divider()
        render_response(st.session_state["current_response"])


def _handle_query(user_query: str):
    """Handle user query: call API + log interaction"""
    import time as _time

    start = _time.time()

    with st.spinner("Retrieving documents and generating answer..."):
        response = call_llm_api(user_query)

    elapsed_ms = int((_time.time() - start) * 1000)

    # Store in session_state
    st.session_state["current_response"] = response
    st.session_state["current_query"] = user_query

    # Log interaction
    log_interaction(response, user_query, elapsed_ms)


# -- Progressive Rendering Core ---------------------------------

def render_response(response: TrustLayerResponse):
    """
    Progressive rendering core function (Plan A: data already in memory, 0-latency expand).

    Render order:
    1. render_confidence_label()         - Confidence label (always shown)
    2. render_alert_banner()              - Low confidence alert (only when low)
    3. st.markdown(response.answer.text)  - AI answer text
    4. render_details_expander()          - Details expander (progressive disclosure core)
    """
    level = response.answer.confidence_level

    # 1. Confidence label
    render_confidence_label(level, response.answer.is_inferred)

    # 2. Low confidence alert (above answer) — suppressed when there are no source docs,
    #    since the no-docs banner below already communicates the problem (avoids a double banner).
    if level == ConfidenceLevel.LOW and response.sources:
        render_alert_banner(response.verification_advice, response.answer.confidence_score)

    # 3. AI answer text
    st.markdown(response.answer.text)

    # 3.5 Empty-retrieval fallback: surface a graceful warning if no source documents matched.
    if not response.sources:
        render_no_docs_banner()

    # 4. Details expander (progressive disclosure core)
    render_details_expander(response)


def render_confidence_label(level: ConfidenceLevel, is_inferred: bool):
    """
    Three-tier differentiated label — REDESIGNED (2026-07-25) as compact HTML pills.
    Replaces st.success/warning/error callouts for design-system consistency.
    Colors: #10B981 high / #F59E0B medium / #EF4444 low (semantic triplet).
    """
    config = {
        ConfidenceLevel.HIGH: ("High Confidence", "#10B981"),
        ConfidenceLevel.MEDIUM: ("Partial Match · Verify Recommended", "#F59E0B"),
        ConfidenceLevel.LOW: ("Low Confidence · Manual Verification Required", "#EF4444"),
    }
    label_text, color = config.get(level, ("Unknown", "#71717A"))

    inferred_badge = (
        ' <span style="background:#F3F4F6; color:#52525B; font-size:11px; font-weight:600; '
        'padding:3px 10px; border-radius:50px; margin-left:8px;">AI Inferred</span>'
        if is_inferred else ""
    )

    st.markdown(
        f'<div style="margin:8px 0;">'
        f'<span style="background:{color}; color:#FFFFFF; font-size:13px; font-weight:600; '
        f'padding:5px 14px; border-radius:50px; letter-spacing:0.3px;">{label_text}</span>'
        f'{inferred_badge}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_alert_banner(verification_advice, confidence_score=None):
    """
    Low confidence alert banner — REDESIGNED (2026-07-25).
    Visual anchors: left red accent bar + red warning icon + bold title + confidence pill + action button.
    See 08_Design_Implementation_Notes.md §3 for design rationale.
    3-color system: #FEF2F2 bg / #DC2626 primary / #FFFFFF contrast (red-family tints don't count as 4th color).
    """
    score_text = f"{int(confidence_score * 100)}% confidence" if confidence_score is not None else "Low confidence"
    fields = verification_advice.fields_to_check if verification_advice and verification_advice.fields_to_check else []
    fields_text = "  ·  ".join(fields) if fields else "construction cost  ·  budget approval number  ·  funding source"

    st.markdown(
        f"""
        <div style="
            display:flex; align-items:center; gap:20px;
            background-color:#FEF2F2; border-left:6px solid #DC2626;
            border-radius:12px; padding:20px 24px; margin:12px 0;
            box-shadow:0 6px 20px rgba(220,38,38,0.10);
        ">
            <div style="
                flex-shrink:0; width:44px; height:44px; border-radius:50%;
                background:#DC2626; display:flex; align-items:center; justify-content:center;
                box-shadow:0 2px 8px rgba(220,38,38,0.30);
            ">
                <span style="color:#FFFFFF; font-size:24px; font-weight:700; line-height:1;">!</span>
            </div>
            <div style="flex:1;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px; flex-wrap:wrap;">
                    <span style="color:#991B1B; font-size:18px; font-weight:700;">Manual verification required</span>
                    <span style="
                        background:#DC2626; color:#FFFFFF; font-size:11px; font-weight:600;
                        padding:3px 10px; border-radius:50px; letter-spacing:0.5px;
                    ">{score_text}</span>
                </div>
                <div style="color:#7F1D1D; font-size:14px; margin-bottom:4px; line-height:1.5;">
                    No fully matching spec found. This answer is AI-inferred — reference only.
                </div>
                <div style="color:#B91C1C; font-size:12px; font-weight:500;">
                    Verify: {fields_text}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Action link button (right-aligned, triggers source document view)
    if verification_advice and verification_advice.action_link:
        link = verification_advice.action_link
        _, btn_col = st.columns([3, 1])
        with btn_col:
            if st.button("View source document  →", key="alert_action_link", type="primary"):
                st.session_state["doc_view"] = {
                    "doc_name": link.document,
                    "page": link.page,
                }
                update_verification_click()
                st.rerun()


def render_no_docs_banner():
    """
    Fallback banner shown when the retrieved source list is empty (no matches from the
    mock database). Keeps the app from silently failing on zero-match queries — surfaces a
    graceful, on-design warning instead. Exact copy per requirement.
    """
    st.markdown(
        """
        <div style="
            display:flex; align-items:center; gap:16px;
            background-color:#FFFBEB; border-left:6px solid #F59E0B;
            border-radius:12px; padding:16px 20px; margin:12px 0;
            box-shadow:0 2px 8px rgba(245,158,11,0.08);
        ">
            <div style="
                flex-shrink:0; width:40px; height:40px; border-radius:50%;
                background:#F59E0B; display:flex; align-items:center; justify-content:center;
            ">
                <span style="color:#FFFFFF; font-size:22px; font-weight:700; line-height:1;">!</span>
            </div>
            <div style="flex:1;">
                <div style="color:#92400E; font-size:15px; font-weight:600; line-height:1.5;">
                    No relevant documents found in the database. Please try adjusting your keywords.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_details_expander(response: TrustLayerResponse):
    """
    Progressive disclosure — styled click-to-expand details panel.

    P0 interaction requirement:
        - Collapsed by default for all confidence levels (user must click to reveal).
        - Styled via _inject_expander_css() to match the trust-layer design system.
        - Content: sources, jargon glossary, verification advice.

    Logging:
        update_details_viewed() is called whenever the panel is expanded.
    """
    level = response.answer.confidence_level

    # P0: always start collapsed; user clicks to expand
    expanded = False

    with st.expander("Details · sources, jargon & verification", expanded=expanded):
        # Log that user viewed details
        update_details_viewed()

        # F1: Source annotations
        render_sources(response.sources)

        # F3: Jargon glossary (independent expander, always collapsed by default)
        if response.jargon_glossary:
            with st.expander("Jargon Glossary", expanded=False):
                render_jargon_glossary(response.jargon_glossary)

        # F4: Verification advice
        render_verification_advice(response.verification_advice, level)


# -- F1: Source Annotations -------------------------------------

def render_sources(sources: list):
    """F1 Source annotation rendering: sorted by match_score descending, each shows doc name + page + match score + excerpt"""
    if not sources:
        st.info("No specific documents referenced in this answer")
        return

    st.markdown(f"**Sources ({len(sources)} matching documents)**")

    # Sort by match_score descending
    sorted_sources = sorted(sources, key=lambda x: x.match_score, reverse=True)

    for i, src in enumerate(sorted_sources):
        page_str = f"Page {src.page_number}" if src.page_number > 0 else "Page not specified"
        match_pct = int(src.match_score * 100)

        st.markdown(f"**{src.document_name}** - {page_str}")
        st.markdown(f"Match Score: {match_pct}%")

        # Excerpt expand (nested expander, Bug 1 fix: use expander not button)
        if src.excerpt:
            with st.expander("View Excerpt", expanded=False, key=f"excerpt_{i}"):
                st.markdown(f"> {src.excerpt}")

        st.markdown("---")


# -- F3: Jargon Glossary ----------------------------------------

def render_jargon_glossary(jargon_glossary: list):
    """F3 Jargon glossary rendering: show plain language by default, formal definition on demand"""
    if not jargon_glossary:
        return

    for i, term in enumerate(jargon_glossary):
        st.markdown(f"**{term.term}**")
        st.markdown(f"💬 {term.plain_language}")

        # Log jargon view
        update_jargon_view(term.term)

        # Formal definition on demand (Bug 1 fix: use expander not button/checkbox)
        with st.expander("Formal Definition", expanded=False, key=f"jargon_def_{i}"):
            st.markdown(term.definition)

        st.markdown("")


# -- F4: Verification Advice -------------------------------------

def render_verification_advice(verification_advice, confidence_level: ConfidenceLevel):
    """F4 Verification advice rendering: needs_verification controls display, low confidence shows 'See alert above'"""
    if not verification_advice or not verification_advice.needs_verification:
        return

    # Low confidence: alert already contains verification info, don't repeat
    if confidence_level == ConfidenceLevel.LOW:
        st.info("See verification advice in the alert above")
        return

    st.markdown("**Verification Recommended**")
    st.markdown("The following fields should be manually verified:")

    if verification_advice.fields_to_check:
        for field in verification_advice.fields_to_check:
            st.markdown(f"- {field}")

    # Action link
    if verification_advice.action_link:
        link = verification_advice.action_link
        if st.button(f"{link.text} ->", key="verif_action_link"):
            st.session_state["doc_view"] = {
                "doc_name": link.document,
                "page": link.page,
            }
            update_verification_click()
            st.rerun()


# -- Document View ----------------------------------------------

def render_document_view(doc_name: str, page_number: int):
    """DOCUMENT_VIEW state rendering: show doc name + page + original content + back button"""
    st.markdown("### Document View")

    if st.button("<- Back to Answer"):
        st.session_state["doc_view"] = None
        st.rerun()

    st.markdown(f"**{doc_name}** - Page {page_number}")
    st.divider()

    content = get_document_page(doc_name, page_number)
    if content:
        st.markdown(content)
    else:
        st.error(f"Document {doc_name} page {page_number} content not found")

    if st.button("<- Back to Answer", key="doc_view_back_bottom"):
        st.session_state["doc_view"] = None
        st.rerun()
