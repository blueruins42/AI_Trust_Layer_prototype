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

    # Inject chart white-card style once per render
    _inject_chart_style()

    # Three metric cards
    render_metric_cards(metrics)

    st.divider()

    # P1: Visual analytics paired with raw data for stronger hierarchy
    render_section_query_trust(log, metrics)

    st.divider()

    render_section_confidence(log, metrics)

    st.divider()

    render_section_jargon(metrics)

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
    """Wrap every altair chart in a P0-style white card and center fixed-width charts."""
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
        div[data-testid="stAltairChart"] svg {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def _style(chart):
    """Apply P0 typography / axis treatment to an altair chart."""
    return (
        chart.properties(
            padding={"top": 18, "left": 6, "right": 6, "bottom": 6}
        )
        .configure_view(strokeWidth=0)
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
            offset=10,
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

    base = alt.Chart(df).properties(height=260)
    area = base.mark_area(color=_LIGHT, opacity=0.10).encode(
        x=alt.X("Query:Q", title="Query Sequence", axis=alt.Axis(grid=False)),
        y=alt.Y("Trust Health (%):Q", title="Verification Click Rate (%)", scale=alt.Scale(0, 100)),
    )
    line = base.mark_line(color=_DEEP, strokeWidth=2.5).encode(x="Query:Q", y="Trust Health (%):Q")
    points = base.mark_circle(color=_DEEP, size=55, stroke="#FFFFFF", strokeWidth=1.5).encode(
        x="Query:Q", y="Trust Health (%):Q"
    )
    chart = (area + line + points)
    return _style(chart)

def _build_confidence_donut(log: list):
    """Confidence distribution donut — semantic triplet, % baked into the legend + centered total."""
    counts = Counter(e.confidence_level for e in log)
    h, m, l = counts.get("high", 0), counts.get("medium", 0), counts.get("low", 0)
    total = h + m + l

    def pct(x):
        return round(x / total * 100, 1) if total else 0

    df = pd.DataFrame(
        [
            {"level": "High", "count": h, "label": f"High · {pct(h)}%"},
            {"level": "Medium", "count": m, "label": f"Medium · {pct(m)}%"},
            {"level": "Low", "count": l, "label": f"Low · {pct(l)}%"},
        ]
    )
    chart = (
        alt.Chart(df)
        .mark_arc(innerRadius=58, stroke="#FFFFFF", strokeWidth=2)
        .encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color(
                "label:N",
                scale=alt.Scale(
                    domain=[f"High · {pct(h)}%", f"Medium · {pct(m)}%", f"Low · {pct(l)}%"],
                    range=[_GREEN, _ORANGE, _RED],
                ),
                legend=alt.Legend(orient="bottom", title=None, labelFontSize=12.5, labelColor=_TEXT),
            ),
            tooltip=["level", "count"],
        )
        .properties(width=230, height=200)
    )
    # Centered total inside the donut hole
    center = (
        alt.Chart(pd.DataFrame({"t": [f"{total}"]}))
        .mark_text(align="center", baseline="middle", fontSize=26, fontWeight="bold", color=_TEXT)
        .encode(
            x=alt.value(115),
            y=alt.value(90),
            text=alt.Text("t:N"),
        )
    )
    sub = (
        alt.Chart(pd.DataFrame({"s": ["queries"]}))
        .mark_text(align="center", baseline="middle", fontSize=12, color=_MUTED)
        .encode(
            x=alt.value(115),
            y=alt.value(112),
            text=alt.Text("s:N"),
        )
    )
    return _style(chart + center + sub)

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
    chart = (bars + labels).properties(height=36 * n + 46)
    return _style(chart)

# ---------------------------------------------------------------------------
# P1: Visual analytics — each chart paired with its raw data source
# ---------------------------------------------------------------------------

def _section_header(eyebrow: str, title: str, subtitle: str = ""):
    """Reusable section eyebrow + title (big section title, no accent bar)."""
    html = (
        '<div style="margin:4px 0 14px 0;">'
        f'<span style="color:#3B82F6; font-size:12px; font-weight:600; letter-spacing:1px;">{eyebrow}</span>'
        f'<div style="color:#0A0A0B; font-size:20px; font-weight:700; margin-top:2px; line-height:1.25;">{title}</div>'
    )
    if subtitle:
        html += f'<div style="color:#6B7280; font-size:13px; margin-top:4px;">{subtitle}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def _chart_subtitle(title: str, subtitle: str = ""):
    """Small chart/block subtitle with a blue vertical accent bar (P0 design language)."""
    html = (
        '<div style="display:flex; align-items:stretch; margin:8px 0 10px 0;">'
        '<div style="width:4px; background:#3B82F6; border-radius:2px; margin-right:10px; flex:0 0 auto;"></div>'
        '<div style="flex:1 1 auto;">'
        f'<div style="color:#0A0A0B; font-size:15px; font-weight:700; line-height:1.2;">{title}</div>'
    )
    if subtitle:
        html += f'<div style="color:#6B7280; font-size:12px; margin-top:2px;">{subtitle}</div>'
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

def _insight_card(items: list, footer: str):
    """Light-blue insight/action card — PRD-driven interpretation, not a raw number repeat."""
    items_html = "".join(f'<li style="margin-bottom:6px;">{it}</li>' for it in items)
    st.markdown(
        f"""
        <div style="background:#F8FAFF; border:1px solid rgba(1,77,178,0.12); border-radius:14px; padding:16px 18px; height:100%;">
            <ul style="margin:0; padding-left:18px; color:#374151; font-size:13px; line-height:1.65;">{items_html}</ul>
            <div style="color:#6B7280; font-size:12px; margin-top:12px; border-top:1px solid rgba(1,77,178,0.10); padding-top:10px;">{footer}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_section_query_trust(log: list, metrics: dict):
    """Trust Health trend chart (full width) + raw recent query history (full width, below)."""
    _section_header(
        eyebrow="QUERY TRUST",
        title="Trust Health & Verification History",
        subtitle="Trend line shows cumulative verification-click rate over the query sequence; full log below.",
    )

    _chart_subtitle("Trust Health Trend", "Cumulative verification-click rate · lower = more trust")
    st.altair_chart(_build_trend_chart(log), use_container_width=True)
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
    _chart_subtitle("Recent Queries", "Full query log · newest first")
    render_recent_queries(metrics["recent_queries"])

def render_section_confidence(log: list, metrics: dict):
    """Confidence donut (with % baked in) + PRD-driven interpretation card."""
    _section_header(
        eyebrow="CONFIDENCE BREAKDOWN",
        title="High / Medium / Low Distribution",
        subtitle="Donut shows the share of each level; the card reads what the split means for iteration.",
    )

    col_chart, col_card = st.columns([1.3, 2])
    with col_chart:
        _chart_subtitle("Confidence Distribution", f"{metrics['total_queries']} queries")
        st.altair_chart(_build_confidence_donut(log), use_container_width=False)
    with col_card:
        _chart_subtitle("Reading the Distribution", "PRD F7 · drive iteration from the split")
        low_pct = metrics["low_conf_rate"]
        trust_pct = metrics["trust_health"]
        c = Counter(e.confidence_level for e in log)
        total = max(metrics["total_queries"], 1)
        high_pct = round(c.get("high", 0) / total * 100, 1)
        _insight_card(
            items=[
                f"Low <b>{low_pct}%</b> → coverage gap; add source docs for low-confidence topics",
                f"High <b>{high_pct}%</b> answers drawn directly from documents",
                f"Trust Health <b>{trust_pct}%</b> — optimization direction: lower rate as users trust the AI more (PRD F7)",
            ],
            footer="A lower low-confidence rate and trust-health rate means a healthier, better-covered system.",
        )

def render_section_jargon(metrics: dict):
    """Jargon term heat bar (with value labels) + glossary-candidate card."""
    _section_header(
        eyebrow="JARGON INSIGHTS",
        title="Term Heat & Glossary Candidates",
        subtitle="Bar shows view intensity; the card lists terms to preload into the glossary.",
    )

    col_chart, col_card = st.columns([2, 1])
    with col_chart:
        _chart_subtitle("Jargon Term Heat", "Most-viewed domain terms · ranked by views")
        bar = _build_jargon_bar(metrics["top_jargon"])
        if bar is not None:
            st.altair_chart(bar, use_container_width=True)
    with col_card:
        _chart_subtitle("Glossary Candidates", "PRD F7 · close the knowledge gap")
        jargon = metrics["top_jargon"]
        if jargon:
            items = [f"<b>{term}</b> ({count}×)" for term, count in jargon[:3]]
            footer = "Terms viewed ≥2× are the strongest candidates for the preset glossary (PRD F7)."
        else:
            items = ["No jargon views recorded yet."]
            footer = "Make queries in the frontend to populate this list."
        _insight_card(items=items, footer=footer)

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

def render_recent_queries(queries: list):
    """Recent 10 query records (rendered as a clean table)."""
    if not queries:
        st.info("No query records yet")
        return

    # Build HTML table with left-aligned # column (reverse order, newest first)
    rows = ""
    total = len(queries)
    for i, entry in enumerate(reversed(queries)):
        seq = total - i  # Sequential number (oldest = 1)
        if entry.clicked_verification:
            verified = '<span style="display:inline-block; padding:2px 9px; border-radius:999px; background:rgba(16,185,129,0.12); color:#10B981; font-weight:600; font-size:12px;">✓ Verified</span>'
        else:
            verified = '<span style="display:inline-block; padding:2px 9px; border-radius:999px; background:rgba(107,114,128,0.12); color:#6B7280; font-weight:600; font-size:12px;">Not verified</span>'
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
