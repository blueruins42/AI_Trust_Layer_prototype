"""
interaction_log.py - Interaction logging and metric computation

Responsibility: manage interaction logs, compute Admin Dashboard metrics
Maps to PRD: Step 4.11 interaction log spec + Step 5.2.8
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid


@dataclass
class InteractionLogEntry:
    """Interaction log entry for a single query"""
    query_id: str
    timestamp: str
    user_query: str
    confidence_level: str
    response_time_ms: int
    viewed_details: bool = False
    viewed_jargon: list = field(default_factory=list)
    clicked_verification: bool = False
    documents_searched: int = 0
    documents_matched: int = 0


def init_log():
    """
    Initialise the log-related variables in st.session_state.
    Called from init_session_state() in app.py.
    """
    import streamlit as st

    if "interaction_log" not in st.session_state:
        st.session_state["interaction_log"] = []
    if "jargon_views" not in st.session_state:
        st.session_state["jargon_views"] = {}
    if "verification_clicks" not in st.session_state:
        st.session_state["verification_clicks"] = 0
    if "details_viewed" not in st.session_state:
        st.session_state["details_viewed"] = False
    if "query_count" not in st.session_state:
        st.session_state["query_count"] = 0


def log_interaction(response, user_query: str, response_time: int):
    """
    Create a log entry and store it in st.session_state["interaction_log"].
    Called after each query in frontend.py.
    """
    import streamlit as st

    entry = InteractionLogEntry(
        query_id=response.metadata.query_id,
        timestamp=response.metadata.timestamp,
        user_query=user_query,
        confidence_level=response.answer.confidence_level.value,
        response_time_ms=response.metadata.response_time_ms,
        viewed_details=False,
        viewed_jargon=[],
        clicked_verification=False,
        documents_searched=response.metadata.documents_searched,
        documents_matched=response.metadata.documents_matched,
    )

    st.session_state["interaction_log"].append(entry)
    st.session_state["query_count"] += 1
    # Reset the interaction flags for the current query
    st.session_state["details_viewed"] = False


def update_jargon_view(term: str):
    """Record that the user viewed a certain term"""
    import streamlit as st

    if term not in st.session_state["jargon_views"]:
        st.session_state["jargon_views"][term] = 0
    st.session_state["jargon_views"][term] += 1

    # Also update viewed_jargon of the most recent log entry
    if st.session_state["interaction_log"]:
        last_entry = st.session_state["interaction_log"][-1]
        if term not in last_entry.viewed_jargon:
            last_entry.viewed_jargon.append(term)


def update_verification_click():
    """Record that the user clicked the verification suggestion"""
    import streamlit as st

    st.session_state["verification_clicks"] += 1

    # Also update clicked_verification of the most recent log entry
    if st.session_state["interaction_log"]:
        st.session_state["interaction_log"][-1].clicked_verification = True


def update_details_viewed():
    """Record that the user viewed the details"""
    import streamlit as st

    if not st.session_state.get("details_viewed", False):
        st.session_state["details_viewed"] = True
        if st.session_state["interaction_log"]:
            st.session_state["interaction_log"][-1].viewed_details = True


def calculate_admin_metrics(log: list) -> dict:
    """
    Compute the three Admin Dashboard metrics:
    - total_queries: total number of queries
    - trust_health: verification click-through rate (higher = less trust in AI)
    - low_conf_rate: low-confidence trigger rate
    - top_jargon: top 5 most frequent terms
    - recent_queries: the 10 most recent entries
    """
    total_queries = len(log)

    if total_queries == 0:
        return {
            "empty": True,
            "total_queries": 0,
            "trust_health": 0,
            "low_conf_rate": 0,
            "top_jargon": [],
            "recent_queries": [],
        }

    verification_clicks = sum(1 for e in log if e.clicked_verification)
    low_conf_count = sum(1 for e in log if e.confidence_level == "low")

    # Term view statistics
    jargon_counter = Counter()
    for entry in log:
        for term in entry.viewed_jargon:
            jargon_counter[term] += 1

    return {
        "empty": False,
        "total_queries": total_queries,
        "trust_health": round(verification_clicks / total_queries * 100, 1),
        "low_conf_rate": round(low_conf_count / total_queries * 100, 1),
        "top_jargon": jargon_counter.most_common(5),
        "recent_queries": log[-10:],
    }
