"""
admin.py - Admin Dashboard Rendering (Wang Fang's view)

Responsibilities: Render F7 monitoring dashboard - metrics + top jargon + recent queries
Corresponds to: PRD Step 4.6 F7 Admin Dashboard + Step 5.2.7
"""

import streamlit as st
import altair as alt
import pandas as pd
from collections import Counter
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

    # P1: Visual analytics — trend line + confidence donut + term-frequency bar
    render_charts(log, metrics)

    st.divider()

    # Top 5 jargon terms
    render_top_jargon(metrics["top_jargon"])

    st.divider()

    # Recent query records
    render_recent_queries(metrics["recent_queries"])


# ---------------------------------------------------------------------------
# P1: Visual analytics charts (design-language consistent with frontend P0)
# Palette: deep blue #014DB2 / light blue #3B82F6, semantic green/orange/red
# White card + 16px radius + soft blue shadow (mirrors frontend hero cards)
# ---------------------------------------------------------------------------
_DEEP = "#014DB2"
_LIGHT = "#3B82F6"
_GREEN = "#10B981"
_ORANGE = "#F59E0B"
_RED = "#EF4444"
_TEXT = "#0A0A0B"
_MUTED = "#6B7280"


def _inject_chart_style():
    """Wrap every altair chart in a P0-style white card (once per render)."""
    st.markdown(
        """
        <style>
        div[data-testid="stAltairChart"] {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 16px 18px 8px 18px;
            box-shadow: 0 2px 8px rgba(1,77,178,0.06);
            margin-bottom: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _style(chart):
    """Apply P0 typography / axis treatment to an altair chart."""
    return (
        chart.configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=_MUTED,
            titleColor=_TEXT,
            titleFontWeight="bold",
            titleFontSize=12,
            gridColor="rgba(128,128,128,0.15)",
            domainColor="rgba(128,128,128,0.3)",
            tickColor="rgba(128,128,128,0.3)",
        )
        .configure_title(
            anchor="start",
            fontSize=16,
            fontWeight="bold",
            color=_TEXT,
            subtitleColor=_MUTED,
            subtitleFontSize=12,
        )
        .configure_legend(labelColor=_MUTED, titleColor=_TEXT)
    )


def _build_trend_chart(log: list):
    """Trust Health trend — cumulative verification-click rate over query sequence."""
    cum_clicks = 0
    rows = []
    for i, e in enumerate(log, 1):
        if e.clicked_verification:
            cum_clicks += 1
        rows.append({"Query": i, "Trust Health (%)": round(cum_clicks / i * 100, 1)})
    df = pd.DataFrame(rows)

    base = alt.Chart(df).properties(height=240)
    area = base.mark_area(color=_LIGHT, opacity=0.10).encode(
        x=alt.X("Query:Q", title="Query Sequence", axis=alt.Axis(grid=False)),
        y=alt.Y("Trust Health (%):Q", title="Verification Click Rate (%)", scale=alt.Scale(0, 100)),
    )
    line = base.mark_line(color=_DEEP, strokeWidth=2.5).encode(x="Query:Q", y="Trust Health (%):Q")
    points = base.mark_circle(color=_DEEP, size=55, stroke="#FFFFFF", strokeWidth=1.5).encode(
        x="Query:Q", y="Trust Health (%):Q"
    )
    chart = (area + line + points).properties(
        title=alt.TitleParams(
            text="Trust Health Trend",
            subtitle="Cumulative verification-click rate · lower = more trust",
            anchor="start",
        )
    )
    return _style(chart)


def _build_confidence_donut(log: list):
    """Confidence distribution donut — semantic triplet (green/orange/red)."""
    counts = Counter(e.confidence_level for e in log)
    df = pd.DataFrame(
        [
            {"level": "High", "count": counts.get("high", 0)},
            {"level": "Medium", "count": counts.get("medium", 0)},
            {"level": "Low", "count": counts.get("low", 0)},
        ]
    )
    total = int(df["count"].sum())
    chart = (
        alt.Chart(df)
        .mark_arc(innerRadius=58, stroke="#FFFFFF", strokeWidth=2)
        .encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color(
                "level:N",
                scale=alt.Scale(domain=["High", "Medium", "Low"], range=[_GREEN, _ORANGE, _RED]),
                legend=alt.Legend(orient="bottom", title=None),
            ),
            tooltip=["level", "count"],
        )
        .properties(
            height=240,
            title=alt.TitleParams(
                text="Confidence Distribution",
                subtitle=f"{total} queries · High / Medium / Low",
                anchor="start",
            ),
        )
    )
    return _style(chart)


def _build_jargon_bar(top_jargon: list):
    """
    Jargon-term heat — OPTIMIZED for differentiation.

    Mock data is sparse and term-view counts run close together, so raw vertical
    bars look near-identical. Optimizations:
      - Horizontal bars (easier rank comparison than vertical)
      - Sorted descending so the leader sits on top
      - Numeric value label at each bar end (differentiation is explicit)
      - Blue intensity gradient (deeper = more viewed) draws the eye to the leader
    """
    if not top_jargon:
        return None
    df = pd.DataFrame(top_jargon, columns=["term", "views"])
    df = df.sort_values("views", ascending=True)  # horizontal bar: largest ends on top
    n = len(df)

    if df["views"].nunique() == 1:
        color_scale = alt.Scale(range=[_DEEP, _DEEP])
    else:
        color_scale = alt.Scale(domain=[df["views"].min(), df["views"].max()], range=["#93C5FD", _DEEP])

    bars = (
        alt.Chart(df)
        .mark_bar(size=22, cornerRadiusEnd=3)
        .encode(
            y=alt.Y(
                "term:N",
                title=None,
                sort=None,
                axis=alt.Axis(labelLimit=260, labelFontSize=12.5, labelColor=_TEXT),
                scale=alt.Scale(padding=0.35),
            ),
            x=alt.X("views:Q", title="Views", axis=alt.Axis(grid=True)),
            color=alt.Color("views:Q", scale=color_scale, legend=None),
        )
    )
    labels = alt.Chart(df).mark_text(dx=7, color=_TEXT, fontWeight="bold", fontSize=12.5).encode(
        y="term:N", x="views:Q", text="views:Q"
    )
    chart = (bars + labels).properties(
        height=36 * n + 46,
        title=alt.TitleParams(
            text="Jargon Term Heat",
            subtitle="Most-viewed domain terms · ranked by views",
            anchor="start",
        ),
    )
    return _style(chart)


def render_charts(log: list, metrics: dict):
    """Render the three P1 analytics charts under a consistent eyebrow/title block."""
    _inject_chart_style()
    st.markdown(
        '<div style="margin:4px 0 14px 0;">'
        '<span style="color:#3B82F6; font-size:12px; font-weight:600; letter-spacing:1px;">VISUAL ANALYTICS</span>'
        '<div style="color:#0A0A0B; font-size:20px; font-weight:700; margin-top:2px;">Trust Metrics at a Glance</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    col_trend, col_donut = st.columns([2, 1])
    with col_trend:
        st.altair_chart(_build_trend_chart(log), use_container_width=True)
    with col_donut:
        st.altair_chart(_build_confidence_donut(log), use_container_width=True)

    bar = _build_jargon_bar(metrics["top_jargon"])
    if bar is not None:
        st.altair_chart(bar, use_container_width=True)


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
