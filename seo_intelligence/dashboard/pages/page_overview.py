"""
dashboard/pages/page_overview.py
──────────────────────────────────
Dashboard Overview — KPIs, health score, recent sessions, activity feed.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from dashboard.components.ui import (
    page_header, kpi_card, section_header, gold_divider,
    empty_state, health_score_ring, styled_dataframe, tip_box,
)


def _compute_health(stats: dict) -> int:
    """Simple heuristic SEO health score 0-100."""
    if stats["total_pages"] == 0:
        return 0
    issue_ratio = stats["meta_issues"] / max(stats["total_pages"], 1)
    dup_ratio   = stats["duplicates"]  / max(stats["total_pages"], 1)
    score = 100 - int(issue_ratio * 40) - int(dup_ratio * 30)
    return max(0, min(100, score))


def render():
    page_header("◈", "Dashboard Overview",
                "Real-time snapshot of your website's SEO intelligence")

    # ── Load data ─────────────────────────────────────────────────────────
    result = st.session_state.get("last_result")
    sessions_data = _load_sessions()

    # Aggregate stats
    if result:
        stats = {
            "total_pages": len(result.pages_df),
            "internal_links": len(result.anchor_df) if not result.anchor_df.empty else 0,
            "meta_issues":    len(result.meta_df)   if not result.meta_df.empty   else 0,
            "duplicates":     len(result.duplicate_df) if not result.duplicate_df.empty else 0,
            "opportunities":  len(result.opportunity_df) if not result.opportunity_df.empty else 0,
            "clusters":       result.cluster_df["cluster_id"].nunique()
                              if (not result.cluster_df.empty and "cluster_id" in result.cluster_df.columns) else 0,
        }
    else:
        stats = {k: 0 for k in ["total_pages","internal_links","meta_issues",
                                  "duplicates","opportunities","clusters"]}

    health = _compute_health(stats)

    # ── KPI Row ────────────────────────────────────────────────────────────
    section_header("◈", "Key Metrics")
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        kpi_card("📄", "Pages Crawled",  f"{stats['total_pages']:,}",
                 badge="Live", badge_type="info")
    with c2:
        kpi_card("⇄",  "Internal Links", f"{stats['internal_links']:,}",
                 sub="across all pages")
    with c3:
        kpi_card("⚠",  "Meta Issues",    f"{stats['meta_issues']:,}",
                 badge=("High" if stats["meta_issues"] > 50 else "Low"),
                 badge_type=("down" if stats["meta_issues"] > 50 else "up"))
    with c4:
        kpi_card("⧖",  "Duplicates",     f"{stats['duplicates']:,}",
                 sub="page pairs")
    with c5:
        kpi_card("◆",  "Opportunities",  f"{stats['opportunities']:,}",
                 sub="link suggestions", badge="New", badge_type="up")
    with c6:
        kpi_card("⬡",  "Topic Clusters", f"{stats['clusters']:,}",
                 sub="semantic groups")

    gold_divider()

    # ── Health Score + Recent Sessions ────────────────────────────────────
    col_health, col_sessions = st.columns([1, 2])

    with col_health:
        section_header("◎", "SEO Health Score")
        health_score_ring(health)

        # Health breakdown
        st.markdown("""
        <div style="padding:0 0.5rem;">""", unsafe_allow_html=True)
        breakdown = [
            ("Meta Coverage",  max(0, 100 - int(stats["meta_issues"] / max(stats["total_pages"],1) * 100))),
            ("Link Quality",   75 if stats["internal_links"] > 0 else 0),
            ("Uniqueness",     max(0, 100 - int(stats["duplicates"] / max(stats["total_pages"],1) * 100))),
            ("Opportunities",  min(100, stats["opportunities"])),
        ]
        for label, val in breakdown:
            color = "#34D399" if val >= 70 else ("#FBBF24" if val >= 40 else "#F87171")
            st.markdown(f"""
            <div style="margin-bottom:0.6rem;">
              <div style="display:flex;justify-content:space-between;
                          font-size:0.75rem;margin-bottom:3px;">
                <span style="color:var(--white-muted);">{label}</span>
                <span style="color:{color};font-weight:600;">{val}%</span>
              </div>
              <div style="height:4px;background:var(--black-4);border-radius:2px;">
                <div style="height:100%;width:{val}%;background:{color};
                            border-radius:2px;transition:width 0.5s;"></div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_sessions:
        section_header("⟳", "Recent Crawl Sessions")
        if sessions_data:
            df = pd.DataFrame(sessions_data)
            # Format columns
            if "started_at" in df.columns:
                df["started_at"] = pd.to_datetime(df["started_at"]).dt.strftime("%Y-%m-%d %H:%M")
            display_cols = ["domain", "total_pages", "status", "language", "started_at"]
            display_cols = [c for c in display_cols if c in df.columns]
            styled_dataframe(df[display_cols], height=320)
        else:
            empty_state("No crawl sessions yet. Start your first analysis!", "⟳")

    gold_divider()

    # ── Quick Actions ─────────────────────────────────────────────────────
    section_header("◆", "Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)

    with qa1:
        if st.button("🚀  New Crawl", use_container_width=True):
            st.session_state.active_page = "crawl"
            st.rerun()
    with qa2:
        if st.button("📊  View Reports", use_container_width=True):
            st.session_state.active_page = "reports"
            st.rerun()
    with qa3:
        if st.button("⇄  Anchor Analysis", use_container_width=True):
            st.session_state.active_page = "anchors"
            st.rerun()
    with qa4:
        if st.button("◆  Opportunities", use_container_width=True):
            st.session_state.active_page = "opportunities"
            st.rerun()

    # ── Tip ───────────────────────────────────────────────────────────────
    if not result:
        tip_box("Start by going to Crawl Management and entering your website URL to run the first analysis.")


def _load_sessions():
    try:
        from database.db import list_crawl_sessions
        return list_crawl_sessions()
    except Exception:
        return []
