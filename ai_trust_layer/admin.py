"""
admin.py - Admin Dashboard Rendering (Wang Fang's view)

Responsibilities: Render F7 monitoring dashboard - metrics + top jargon + recent queries
Corresponds to: PRD Step 4.6 F7 Admin Dashboard + Step 5.2.7

Visual language (mirrors frontend P0 + ardot design draft, item-by-item):
- Every visualization / insight block is wrapped in `_white_card` (white bg, 16px radius,
  soft blue shadow, hairline border) so all three sections read as ONE consistent system.
- Confidence donut + trend line + jargon bars are all inline SVG / responsive HTML, matching
  the ardot draft pixel-for-pixel where it matters.
- All inline numeric figures (#, response time, bar values, page indicator, metric cards,
  axis labels, legend %) use ONE locked 黑体 / sans font stack (consistent, never monospace).
"""

import streamlit as st
from collections import Counter
import math
from interaction_log import calculate_admin_metrics

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
_DEEP = "#014DB2"
_LIGHT = "#3B82F6"
_GREEN = "#10B981"
_ORANGE = "#F59E0B"
_RED = "#EF4444"
_TEXT = "#0A0A0B"
_MUTED = "#6B7280"
_TRACK = "#EEF2F7"
_CHIP_BG = "#EFF4FF"

# Shared numeric figure font — LOCKED to one 黑体 / sans stack so every number on the
# page renders identically (user requirement: "all numbers one font, just use 黑体").
_NUM = "'Inter', 'PingFang SC', 'Heiti SC', 'Microsoft YaHei', sans-serif"
_SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"


def render_admin():
    """Admin Dashboard main render function"""
    # Eyebrow + title (design-system consistent with frontend hero)
    st.markdown(
        '<p style="color:#3B82F6; font-size:13px; font-weight:600; letter-spacing:1.5px; margin-bottom:4px; font-family:{_SANS};">TRUST LAYER ANALYTICS</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h2 style="font-size:32px; font-weight:800; color:#0A0A0B; margin-top:0; margin-bottom:4px;">Admin Dashboard</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="color:#6B7280; font-size:13px; line-height:1.5; '
        f'margin:6px 0 20px 0; font-family:{_SANS};">'
        f'Monitor trust health, low-confidence rates, and '
        f'frequently-viewed jargon for system iteration.</p>',
        unsafe_allow_html=True,
    )

    # Lock every numeric figure (incl. st.metric values) to ONE 黑体 font stack, so the
    # three metric cards match the inline numbers elsewhere on the page.
    st.markdown(
        '<style>'
        '[data-testid="stMetricValue"]{'
        'font-family:"Inter","PingFang SC","Microsoft YaHei","Heiti SC",sans-serif !important;'
        'font-weight:700 !important;}'
        '</style>',
        unsafe_allow_html=True,
    )

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

    # P1: Visual analytics paired with raw data for stronger hierarchy
    render_section_query_trust(log, metrics)

    st.divider()

    render_section_confidence(log, metrics)

    st.divider()

    render_section_jargon(metrics)

    st.divider()
    _render_footer()


# ---------------------------------------------------------------------------
# Design language — shared white card
# ---------------------------------------------------------------------------
def _white_card(inner_html: str, padding: str = "24px"):
    """P0-style white card: 16px radius + soft blue shadow + hairline border.
    Used for EVERY visualization and insight block so the three sections
    read as one consistent system (matches the ardot design draft)."""
    return (
        f'<div style="background:#FFFFFF; border-radius:16px; padding:{padding}; '
        f'box-shadow:0 2px 8px rgba(1,77,178,0.06); '
        f'border:1px solid rgba(1,77,178,0.08);">{inner_html}</div>'
    )


# ---------------------------------------------------------------------------
# SVG chart builders — three visualizations share one visual treatment
# ---------------------------------------------------------------------------

def _build_trend_chart_html(log: list):
    """Trust Health trend — cumulative verification-click rate over query sequence.

    Rendered as inline SVG inside a white card (matches ardot draft), so it gets the
    exact same backing as the donut and the jargon bars.
    """
    cum = 0
    pts = []
    for i, e in enumerate(log, 1):
        if e.clicked_verification:
            cum += 1
        pts.append(round(cum / i * 100, 1))
    n = len(pts)
    if n == 0:
        return '<div style="color:#6B7280; font-size:13px; padding:20px 0;">No query data yet.</div>'

    W, H = 760, 280
    L, R, T, B = 48, 740, 24, 244          # plot area
    pw, ph = R - L, B - T

    def x(i):
        return L + (i / (n - 1)) * pw if n > 1 else L + pw / 2

    def y(p):
        return B - (p / 100) * ph

    # horizontal gridlines + y labels
    grid = ""
    for g in (0, 25, 50, 75, 100):
        gy = y(g)
        grid += (
            f'<line x1="{L}" y1="{gy:.1f}" x2="{R}" y2="{gy:.1f}" '
            f'stroke="rgba(128,128,128,0.15)" stroke-width="1"/>'
            f'<text x="{L - 8}" y="{gy + 4:.1f}" font-family="{_NUM}" '
            f'font-size="11" fill="#6B7280" text-anchor="end">{g}</text>'
        )

    coords = " ".join(f"{x(i):.1f},{y(p):.1f}" for i, p in enumerate(pts))
    area = f'<polygon points="{L},{B} {coords} {R},{B}" fill="rgba(59,130,246,0.10)"/>'
    line = (
        f'<polyline points="{coords}" fill="none" stroke="{_DEEP}" stroke-width="2.5" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    dots = "".join(
        f'<circle cx="{x(i):.1f}" cy="{y(p):.1f}" r="3.5" fill="{_DEEP}" '
        f'stroke="#FFFFFF" stroke-width="1.5"/>'
        for i, p in enumerate(pts)
    )
    xlabels = "".join(
        f'<text x="{x(i):.1f}" y="{B + 18:.1f}" font-family="{_NUM}" '
        f'font-size="11" fill="#6B7280" text-anchor="middle">Q{i + 1}</text>'
        for i in range(n)
    )

    svg = (
        f'<svg width="100%" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'style="display:block;">{grid}{area}{line}{dots}{xlabels}</svg>'
    )
    return svg


def _build_confidence_donut_html(log: list):
    """Confidence distribution donut as inline SVG — semantic triplet, centered total, HTML legend.

    Fixes three review-flagged bugs: too-thin ring (innerRadius too large),
    mis-centered center text, and a bottom legend clipped inside a 230px chart.
    Wrapped in the shared white card (min-height 360 to sit flush with the reading card).
    """
    counts = Counter(e.confidence_level for e in log)
    h, m, l = counts.get("high", 0), counts.get("medium", 0), counts.get("low", 0)
    total = h + m + l
    segs = [("High", h, _GREEN), ("Medium", m, _ORANGE), ("Low", l, _RED)]

    cx = cy = 140
    r = 88  # mid radius; stroke-width 44 -> outer 110, inner 66 (matches design draft)
    circ = 2 * math.pi * r
    offset = 0.0
    arcs = ""
    if total > 0:
        for _name, cnt, color in segs:
            if cnt <= 0:
                continue
            dash = cnt / total * circ
            arcs += (
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
                f'stroke-width="44" stroke-dasharray="{dash:.2f} {circ - dash:.2f}" '
                f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"/>'
            )
            offset += dash

    center = (
        f'<text x="{cx}" y="{cy - 4}" font-family="{_NUM}" font-size="54" '
        f'font-weight="700" fill="{_TEXT}" text-anchor="middle">{total}</text>'
        f'<text x="{cx}" y="{cy + 26}" font-family="{_SANS}" font-size="15" '
        f'font-weight="500" fill="{_MUTED}" text-anchor="middle">queries</text>'
    )

    legend_html = (
        '<div style="display:flex; gap:28px; justify-content:center; margin-top:18px; flex-wrap:wrap;">'
    )
    for name, cnt, color in segs:
        if total == 0:
            continue
        p = round(cnt / total * 100, 1)
        legend_html += (
            f'<span style="display:inline-flex; align-items:center; gap:8px; font-size:13px; '
            f'color:{_TEXT}; font-weight:500; font-family:{_NUM};">'
            f'<span style="width:12px; height:12px; border-radius:6px; background:{color}; '
            f'display:inline-block;"></span>{name} · {p}%</span>'
        )
    legend_html += "</div>"

    svg = (
        f'<svg width="280" height="280" viewBox="0 0 280 280" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:block; margin:0 auto;">'
        f'{arcs}{center}</svg>'
    )

    return _white_card(
        f'<div style="display:flex; flex-direction:column; align-items:center; '
        f'min-height:360px; justify-content:center;">{svg}{legend_html}</div>'
    )


def _build_jargon_bar_html(top_jargon: list):
    """Jargon-term heat as responsive horizontal bars — sorted descending, value at bar end.

    Responsive (flex track + percentage fill) so it never distorts at any browser zoom —
    unlike the earlier fixed-px SVG. Rendered inside the shared white card.
    """
    if not top_jargon:
        return '<div style="color:#6B7280; font-size:13px; padding:20px 0;">No jargon views recorded yet.</div>'

    items = sorted(top_jargon, key=lambda t: t[1], reverse=True)
    maxv = max(c for _, c in items) or 1

    rows = ""
    for term, views in items:
        pct = (views / maxv) * 100
        label = term if len(term) <= 26 else term[:24] + "…"
        rows += (
            '<div style="display:flex; align-items:center; gap:16px;">'
            f'<div style="flex:0 0 200px; font-size:13px; font-weight:500; color:{_TEXT}; '
            f'text-align:left; font-family:{_SANS};">{label}</div>'
            '<div style="flex:1 1 auto; height:28px; background:#EEF2F7; border-radius:6px; '
            'position:relative;">'
            f'<div style="position:absolute; left:0; top:0; height:28px; width:{pct:.1f}%; '
            f'background:{_DEEP}; border-radius:6px;"></div>'
            '</div>'
            f'<div style="flex:0 0 40px; text-align:right; font-family:{_NUM}; '
            f'font-size:13px; font-weight:600; color:{_TEXT};">{views}</div>'
            '</div>'
        )

    return f'<div style="display:flex; flex-direction:column; gap:16px;">{rows}</div>'


# ---------------------------------------------------------------------------
# Section + chart subtitle helpers (consistent across all three sections)
# ---------------------------------------------------------------------------

def _section_header(eyebrow: str, title: str, subtitle: str = ""):
    """Reusable section eyebrow + title + subtitle (uniform across sections)."""
    html = (
        '<div style="margin:4px 0 14px 0;">'
        f'<span style="color:#3B82F6; font-size:12px; font-weight:600; letter-spacing:1px; '
        f'font-family:{_SANS};">{eyebrow}</span>'
        f'<div style="color:#0A0A0B; font-size:20px; font-weight:700; margin-top:2px; '
        f'line-height:1.25; font-family:{_SANS};">{title}</div>'
    )
    if subtitle:
        html += f'<div style="color:#6B7280; font-size:13px; margin-top:4px; font-family:{_SANS};">{subtitle}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _chart_subtitle(title: str):
    """Small block subtitle with a blue vertical accent bar (P0 design language).
    Matches ardot: 4x18 #3B82F6 bar (radius 2) + Inter Bold 15 title, no secondary text."""
    html = (
        '<div style="display:flex; align-items:stretch; margin:8px 0 12px 0;">'
        '<div style="width:4px; background:#3B82F6; border-radius:2px; margin-right:8px; '
        'flex:0 0 auto;"></div>'
        f'<div style="flex:1 1 auto; color:#0A0A0B; font-size:15px; font-weight:700; '
        f'line-height:1.2; font-family:{_SANS};">{title}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_section_query_trust(log: list, metrics: dict):
    """Section 1 — Trust Health & Verification History.

    Structure (matches ardot): section header -> "Trust Health Trend" (blue-bar subtitle)
    -> trend white card -> "Recent Queries" (blue-bar subtitle) -> recent-queries white card.
    """
    _section_header(
        eyebrow="QUERY TRUST",
        title="Trust Health & Verification History",
        subtitle="Cumulative verification-click rate over the query sequence, with the full log below.",
    )

    _chart_subtitle("Trust Health Trend")
    st.markdown(_white_card(_build_trend_chart_html(log)), unsafe_allow_html=True)
    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)
    _chart_subtitle("Recent Queries")
    render_recent_queries(metrics["recent_queries"])


def render_section_confidence(log: list, metrics: dict):
    """Section 2 — High / Medium / Low Distribution.

    Layout: donut card (left) + reading card (right). The "Reading the Distribution"
    blue-bar title sits OUTSIDE the reading card (consistent with the other chart
    subtitles), and both cards share an identical 360px content min-height, so their
    outer frames are exactly the same height (360 + 48 padding = 408px).
    """
    _section_header(
        eyebrow="CONFIDENCE BREAKDOWN",
        title="High / Medium / Low Distribution",
        subtitle="Donut shows the share of each confidence level; the card reads what the split means for system iteration.",
    )

    c = Counter(e.confidence_level for e in log)
    total = max(metrics["total_queries"], 1)
    high = c.get("high", 0)
    medium = c.get("medium", 0)
    low = c.get("low", 0)
    high_pct = round(high / total * 100, 1)
    medium_pct = round(medium / total * 100, 1)
    low_pct = round(low / total * 100, 1)

    bullets = [
        f"High <b style=\"font-family:{_NUM}\">{high_pct}%</b> "
        f"(<span style=\"font-family:{_NUM}\">{high}</span>) — answers drawn directly from source documents",
        f"Medium <b style=\"font-family:{_NUM}\">{medium_pct}%</b> "
        f"(<span style=\"font-family:{_NUM}\">{medium}</span>) — partial coverage; monitor for escalation",
        f"Low <b style=\"font-family:{_NUM}\">{low_pct}%</b> "
        f"(<span style=\"font-family:{_NUM}\">{low}</span>) — coverage gap; add source docs for these topics",
    ]
    bullet_html = "".join(
        '<div style="display:flex; align-items:center; gap:8px;">'
        '<div style="width:6px; height:6px; border-radius:3px; background:#014DB2; '
        'flex:0 0 auto;"></div>'
        f'<div style="font-size:14px; color:#0A0A0B; font-family:{_SANS};">{b}</div>'
        '</div>'
        for b in bullets
    )

    # Blue-bar title OUTSIDE the reading card (same treatment as Trust Health Trend / etc.)
    reading_title = (
        '<div style="display:flex; align-items:stretch; margin:0 0 12px 0;">'
        '<div style="width:4px; background:#3B82F6; border-radius:2px; margin-right:8px; '
        'flex:0 0 auto;"></div>'
        f'<div style="flex:1 1 auto; color:#0A0A0B; font-size:15px; font-weight:700; '
        f'line-height:1.2; font-family:{_SANS};">Reading the Distribution</div>'
        '</div>'
    )

    reading_inner = (
        f'<div style="display:flex; flex-direction:column; min-height:360px;">'
        f'<div style="display:flex; flex-direction:column; gap:16px; '
        f'justify-content:center; flex:1 1 auto;">{bullet_html}</div>'
        f'<div style="margin-top:20px; border-top:1px solid rgba(1,77,178,0.10); '
        f'padding-top:12px; color:#6B7280; font-size:12px; font-family:{_SANS};">'
        f'A lower low-confidence rate means a healthier, better-covered system.</div>'
        f'</div>'
    )
    reading_card = _white_card(reading_inner, padding="24px")

    # Both cards: 360 content + 48 padding = 408px outer. Each column carries its own
    # blue-bar title OUTSIDE the card (donut -> "Confidence Levels", reading ->
    # "Reading the Distribution"), so the two card frames start at the same top edge
    # (no placeholder needed above the donut card).
    donut_title = (
        '<div style="display:flex; align-items:stretch; margin:0 0 12px 0;">'
        '<div style="width:4px; background:#3B82F6; border-radius:2px; margin-right:8px; '
        'flex:0 0 auto;"></div>'
        f'<div style="flex:1 1 auto; color:#0A0A0B; font-size:15px; font-weight:700; '
        f'line-height:1.2; font-family:{_SANS};">Confidence Levels</div>'
        '</div>'
    )
    section2 = (
        '<div style="display:flex; gap:24px; align-items:flex-start; flex-wrap:wrap;">'
        f'<div style="flex:1 1 360px; display:flex; flex-direction:column;">'
        f'{donut_title}{_build_confidence_donut_html(log)}</div>'
        f'<div style="flex:1 1 420px; display:flex; flex-direction:column;">'
        f'{reading_title}{reading_card}'
        '</div>'
        '</div>'
    )
    st.markdown(section2, unsafe_allow_html=True)


def render_section_jargon(metrics: dict):
    """Section 3 — Frequently-Viewed Jargon.

    Layout (top-bottom): "Jargon Term Views" (blue-bar subtitle) -> bar card,
    then "Glossary Candidates" (blue-bar subtitle, OUTSIDE its card) -> glossary card.
    """
    _section_header(
        eyebrow="VOCABULARY GAP",
        title="Frequently-Viewed Jargon",
        subtitle="Horizontal bars show how often users expanded a domain term; top candidates should be added to the system glossary to close the knowledge gap.",
    )

    jargon = metrics.get("top_jargon") or []
    if not jargon:
        st.info("No jargon views recorded yet. Make queries in the frontend to populate this list.")
        return

    _chart_subtitle("Jargon Term Views")
    st.markdown(_white_card(_build_jargon_bar_html(jargon)), unsafe_allow_html=True)

    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

    # Blue-bar subtitle OUTSIDE the glossary card (same treatment as Jargon Term Views).
    # The explanatory sentence now lives in the section subtitle above (per design spec).
    _chart_subtitle("Glossary Candidates")
    chips = "".join(
        f'<span style="display:inline-block; padding:10px 14px; border-radius:999px; '
        f'background:{_CHIP_BG}; color:#014DB2; font-size:13px; font-weight:500; '
        f'font-family:{_SANS}; white-space:nowrap;">{term} · {count}</span>'
        for term, count in jargon
    )
    glossary_html = (
        '<div style="background:#FFFFFF; border-radius:16px; padding:24px; '
        'box-shadow:0 2px 8px rgba(1,77,178,0.06); border:1px solid rgba(1,77,178,0.08);">'
        f'<div style="display:flex; flex-wrap:wrap; gap:10px;">{chips}</div>'
        '</div>'
    )
    st.markdown(glossary_html, unsafe_allow_html=True)


def render_metric_cards(metrics: dict):
    """Three metric cards (st.columns(3) + st.metric)."""
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


def render_recent_queries(queries: list, page_size: int = 4):
    """Recent query records as a paginated table (4 per page, newest first).

    Wrapped in the shared white card (rounded corners, soft shadow) so the table reads as
    ONE consistent element with the three visualizations — no more raw line-frame.
    Inline numeric figures (# and response time) use IBM Plex Mono SemiBold 13, matching
    the bar values and page indicator.
    """
    if not queries:
        st.info("No query records yet")
        return

    total = len(queries)
    n_pages = max(1, (total + page_size - 1) // page_size)

    # Page state in session
    page_key = "admin_query_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    page = st.session_state[page_key]
    if page >= n_pages:
        page = n_pages - 1
        st.session_state[page_key] = page

    # Newest first
    ordered = list(reversed(queries))
    start = page * page_size
    page_rows = ordered[start:start + page_size]

    conf_color = {"high": _GREEN, "medium": _ORANGE, "low": _RED}

    rows = ""
    n_rows = len(page_rows)
    for local_i, entry in enumerate(page_rows):
        seq = total - (start + local_i)
        conf = (
            f'<span style="color:{conf_color.get(entry.confidence_level, _TEXT)}; '
            f'font-weight:600; font-family:{_SANS};">{entry.confidence_level.capitalize()}</span>'
        )
        ver = (
            f'<span style="color:{_GREEN if entry.clicked_verification else _MUTED}; '
            f'font-weight:600; font-family:{_SANS};">'
            f'{"Verified" if entry.clicked_verification else "Not verified"}</span>'
        )
        query_display = entry.user_query[:42] + ("…" if len(entry.user_query) > 42 else "")
        rtime = f"{entry.response_time_ms / 1000:.1f}s"

        rows += (
            f'<tr>'
            f'<td style="text-align:left; padding:12px; font-family:{_NUM}; font-weight:600; '
            f'font-size:13px; color:{_MUTED};">{seq}</td>'
            f'<td style="text-align:left; padding:12px; font-family:{_SANS}; font-size:13px; color:{_TEXT};">'
            f'{query_display}</td>'
            f'<td style="text-align:left; padding:12px; font-size:13px;">{conf}</td>'
            f'<td style="text-align:left; padding:12px; font-family:{_NUM}; font-weight:600; '
            f'font-size:13px; color:{_TEXT};">{rtime}</td>'
            f'<td style="text-align:left; padding:12px; font-size:13px;">{ver}</td>'
            f'</tr>'
        )

    # Scoped CSS for the Recent Queries table. Streamlit's HTML sanitizer STRIPS inline
    # `!important` declarations from element style attributes, so the border rules must
    # live in a <style> block (which Streamlit preserves) and be scoped to .tl-rq-table.
    # We switch to `border-collapse: separate` and draw a separator ONLY between rows; the
    # LAST row gets none, so the table closes cleanly on the white card frame on every page
    # (no trailing rule, no clipping by overflow:hidden).
    table_html = f'''
    <style>
    .tl-rq-table table {{ border-collapse: separate; border-spacing: 0; }}
    /* No vertical lines anywhere — columns are separated by alignment only. */
    .tl-rq-table th, .tl-rq-table td {{ border-left: none !important; border-right: none !important; }}
    .tl-rq-table td {{ border-top: none !important; border-bottom: none !important; }}
    /* Horizontal separators only: one under the header, and between data rows
       (but not on the last row, so the table closes cleanly on the card frame). */
    .tl-rq-table th {{ border-bottom: 1px solid rgba(128,128,128,0.12) !important; }}
    .tl-rq-table tbody tr:not(:last-child) td {{ border-bottom: 1px solid rgba(128,128,128,0.12) !important; }}
    </style>
    <div class="tl-rq-table" style="border-radius:16px; overflow:hidden;">
      <table style="width:100%; font-family:{_SANS};">
        <thead>
          <tr style="background:#F9FAFB;">
            <th style="text-align:left; padding:12px; font-size:12px; font-weight:600; color:{_MUTED};">#</th>
            <th style="text-align:left; padding:12px; font-size:12px; font-weight:600; color:{_MUTED};">Query</th>
            <th style="text-align:left; padding:12px; font-size:12px; font-weight:600; color:{_MUTED};">Confidence</th>
            <th style="text-align:left; padding:12px; font-size:12px; font-weight:600; color:{_MUTED};">Response</th>
            <th style="text-align:left; padding:12px; font-size:12px; font-weight:600; color:{_MUTED};">Verification</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    '''
    st.markdown(_white_card(table_html, padding="0"), unsafe_allow_html=True)

    _render_pagination(page, n_pages, page_key)


def _render_pagination(page: int, n_pages: int, page_key: str):
    """Prev / Page x of y / Next — mirrors the ardot design draft.

    A 14px gap separates the table card from the controls so Prev/Next no longer
    touch the card edge.
    """
    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
    col_prev, col_info, col_next = st.columns([1, 1, 1])
    with col_prev:
        if st.button(
            "← Previous",
            key="q_prev",
            disabled=(page <= 0),
            use_container_width=True,
        ):
            st.session_state[page_key] = max(0, page - 1)
            st.rerun()
    with col_info:
        st.markdown(
            f'<div style="text-align:center; font-family:{_NUM}; '
            f'font-weight:600; font-size:13px; color:{_MUTED}; padding:8px 0;">'
            f'Page {page + 1} of {n_pages}</div>',
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button(
            "Next →",
            key="q_next",
            disabled=(page >= n_pages - 1),
            use_container_width=True,
        ):
            st.session_state[page_key] = min(n_pages - 1, page + 1)
            st.rerun()


def _render_footer():
    """Unified page footer — consistent with the frontend onboarding page."""
    st.markdown(
        '<div style="text-align:center; font-size:13px; color:#A1A1AA; '
        'padding:28px 0 4px 0; margin-top:8px; font-family:{_SANS};">'
        'Built for enterprise RAG systems&nbsp;&nbsp;·&nbsp;&nbsp;'
        'Designed by Shuting Fan&nbsp;&nbsp;·&nbsp;&nbsp;'
        'MSc Interaction &amp; Experience Design Portfolio</div>'.replace("{_SANS}", _SANS),
        unsafe_allow_html=True,
    )
