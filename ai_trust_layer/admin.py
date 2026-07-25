"""
admin.py - Admin Dashboard Rendering (Wang Fang's view)

Responsibilities: Render F7 monitoring dashboard - metrics + top jargon + recent queries
Corresponds to: PRD Step 4.6 F7 Admin Dashboard + Step 5.2.7
"""

import streamlit as st
from interaction_log import calculate_admin_metrics


def render_admin():
    """Admin Dashboard main render function"""
    # Eyebrow + title (design-system consistent with frontend hero)
    st.markdown(
        '<p style="color:#3B82F6; font-size:13px; font-weight:600; letter-spacing:1.5px; margin-bottom:4px;">TRUST LAYER ANALYTICS</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h2 style="font-size:32px; font-weight:800; color:#0A0A0B; margin-top:0; margin-bottom:4px;">Admin Dashboard</h2>',
        unsafe_allow_html=True,
    )
    st.caption("Monitor trust health, low-confidence rates, and frequently-viewed jargon for system iteration.")

    # Get log data
    log = st.session_state.get("interaction_log", [])
    metrics = calculate_admin_metrics(log)

    # Empty data handling
    if metrics.get("empty"):
        st.info("No data yet. Please make queries in the frontend first.")
        return

    # Three metric cards
    render_metric_cards(metrics)

    st.divider()

    # Top 5 jargon terms
    render_top_jargon(metrics["top_jargon"])

    st.divider()

    # Recent query records
    render_recent_queries(metrics["recent_queries"])


def render_metric_cards(metrics: dict):
    """
    Three metric cards (st.columns(3) + st.metric):
    - Trust Health (verification click rate)
    - Low Confidence Rate
    - Total Queries
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        trust_pct = metrics["trust_health"]
        st.metric(
            label="Trust Health",
            value=f"{trust_pct}%",
            help="Verification click rate = verification clicks / total queries. Higher = users trust AI less. Optimization direction: decrease over time (trust is being built)",
        )
        st.caption("Verification Click Rate - Lower = More Trust")

    with col2:
        low_pct = metrics["low_conf_rate"]
        st.metric(
            label="Low Confidence Rate",
            value=f"{low_pct}%",
            help="Low confidence queries / total queries. Higher = RAG database coverage is insufficient. Optimization direction: decrease over time (data is being supplemented)",
        )
        st.caption("Lower = Better Coverage")

    with col3:
        total = metrics["total_queries"]
        st.metric(
            label="Total Queries",
            value=f"{total}",
            help="Total number of queries in the current session",
        )
        st.caption("Session Total")




def render_top_jargon(jargon_list: list):
    """Top 5 frequently viewed jargon terms"""
    st.markdown("### Frequently Viewed Jargon Terms (Top 5)")

    if not jargon_list:
        st.info("No jargon view records yet")
        return

    # Build HTML table with left-aligned columns
    rows = ""
    for i, (term, count) in enumerate(jargon_list, 1):
        rows += (
            f'<tr style="border-bottom: 1px solid rgba(128,128,128,0.2);">'
            f'<td style="text-align: left; padding: 6px 10px;">{i}</td>'
            f'<td style="text-align: left; padding: 6px 10px;">{term}</td>'
            f'<td style="text-align: left; padding: 6px 10px;">{count}</td>'
            f'</tr>'
        )

    st.markdown(
        f"""
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 2px solid rgba(128,128,128,0.4);">
                    <th style="text-align: left; padding: 6px 10px;">Rank</th>
                    <th style="text-align: left; padding: 6px 10px;">Term</th>
                    <th style="text-align: left; padding: 6px 10px;">Views</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def render_recent_queries(queries: list):
    """Recent 10 query records"""
    st.markdown(
        '<div style="margin:8px 0 16px 0;">'
        '<span style="color:#3B82F6; font-size:12px; font-weight:600; letter-spacing:1px;">QUERY HISTORY</span>'
        '<div style="color:#0A0A0B; font-size:20px; font-weight:700; margin-top:2px;">Recent Queries</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if not queries:
        st.info("No query records yet")
        return

    # Build HTML table with left-aligned # column (reverse order, newest first)
    rows = ""
    total = len(queries)
    for i, entry in enumerate(reversed(queries)):
        seq = total - i  # Sequential number (oldest = 1)
        verified = "Verified ✓" if entry.clicked_verification else "Not Verified"
        conf_display = {
            "high": '<span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#10B981; margin-right:6px; vertical-align:middle;"></span>High',
            "medium": '<span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#F59E0B; margin-right:6px; vertical-align:middle;"></span>Medium',
            "low": '<span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#EF4444; margin-right:6px; vertical-align:middle;"></span>Low',
        }.get(entry.confidence_level, entry.confidence_level)

        # Truncate query text
        query_display = entry.user_query[:35] + ("..." if len(entry.user_query) > 35 else "")

        rows += (
            f'<tr style="border-bottom: 1px solid rgba(128,128,128,0.2);">'
            f'<td style="text-align: left; padding: 6px 10px;">{seq}</td>'
            f'<td style="text-align: left; padding: 6px 10px;">{query_display}</td>'
            f'<td style="text-align: left; padding: 6px 10px;">{conf_display}</td>'
            f'<td style="text-align: left; padding: 6px 10px;">{entry.response_time_ms}ms</td>'
            f'<td style="text-align: left; padding: 6px 10px;">{verified}</td>'
            f'</tr>'
        )

    st.markdown(
        f"""
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 2px solid rgba(128,128,128,0.4);">
                    <th style="text-align: left; padding: 6px 10px;">#</th>
                    <th style="text-align: left; padding: 6px 10px;">Query</th>
                    <th style="text-align: left; padding: 6px 10px;">Confidence</th>
                    <th style="text-align: left; padding: 6px 10px;">Response Time</th>
                    <th style="text-align: left; padding: 6px 10px;">Verification</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
