"""
interaction_log.py - 交互日志记录与指标计算

职责：管理交互日志、计算 Admin Dashboard 指标
对应 PRD：Step 4.11 交互日志规格 + Step 5.2.8
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid


@dataclass
class InteractionLogEntry:
    """单次查询的交互日志条目"""
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
    初始化 st.session_state 中的日志相关变量。
    在 app.py 的 init_session_state() 中调用。
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
    创建日志条目并存入 st.session_state["interaction_log"]。
    在 frontend.py 每次查询后调用。
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
    # 重置当前查询的交互标记
    st.session_state["details_viewed"] = False


def update_jargon_view(term: str):
    """记录用户查看了某个术语"""
    import streamlit as st

    if term not in st.session_state["jargon_views"]:
        st.session_state["jargon_views"][term] = 0
    st.session_state["jargon_views"][term] += 1

    # 同时更新最近一条日志的 viewed_jargon
    if st.session_state["interaction_log"]:
        last_entry = st.session_state["interaction_log"][-1]
        if term not in last_entry.viewed_jargon:
            last_entry.viewed_jargon.append(term)


def update_verification_click():
    """记录用户点击了核实建议"""
    import streamlit as st

    st.session_state["verification_clicks"] += 1

    # 同时更新最近一条日志的 clicked_verification
    if st.session_state["interaction_log"]:
        st.session_state["interaction_log"][-1].clicked_verification = True


def update_details_viewed():
    """记录用户查看了详情"""
    import streamlit as st

    if not st.session_state.get("details_viewed", False):
        st.session_state["details_viewed"] = True
        if st.session_state["interaction_log"]:
            st.session_state["interaction_log"][-1].viewed_details = True


def calculate_admin_metrics(log: list) -> dict:
    """
    计算 Admin Dashboard 三项指标：
    - total_queries: 总查询数
    - trust_health: 核实点击率（越高=越不信任AI）
    - low_conf_rate: 低置信度触发率
    - top_jargon: 高频术语 Top 5
    - recent_queries: 最近 10 条
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

    # 术语查看统计
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
