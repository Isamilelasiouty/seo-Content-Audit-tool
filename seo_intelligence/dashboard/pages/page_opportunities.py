"""
dashboard/pages/page_opportunities.py
──────────────────────────────────────
Link Opportunities — suggested new internal links with similarity scores.
"""

import streamlit as st
import pandas as pd

from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    kpi_card, empty_state, tip_box, opportunity_card,
)


def render():
    page_header("◆", "Link Opportunities",
                "AI-discovered internal linking suggestions your site is missing")

    result = st.session_state.get("last_result")
    if result is None or result.opportunity_df.empty:
        empty_state("No opportunity data yet. Run a crawl to discover link gaps.", "◆")
        tip_box("The engine compares every page semantically and finds pages that should link to each other but don't.")
        return

    df = result.opportunity_df.copy()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    high_conf = len(df[df["similarity_score"] >= 0.85])
    med_conf  = len(df[(df["similarity_score"] >= 0.75) & (df["similarity_score"] < 0.85)])
    low_conf  = len(df[df["similarity_score"] < 0.75])

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("◆",  "Total Suggestions", f"{len(df):,}",   badge="AI-Found")
    with c2: kpi_card("★",  "High Confidence",   f"{high_conf:,}", badge_type="up",   badge="≥85%")
    with c3: kpi_card("◈",  "Medium Confidence", f"{med_conf:,}",  badge_type="info", badge="75-85%")
    with c4: kpi_card("○",  "Low Confidence",    f"{low_conf:,}",  badge_type="info", badge="<75%")

    gold_divider()

    # ── Filters ───────────────────────────────────────────────────────────────
    section_header("⚙", "Filter Opportunities")
    f1, f2, f3 = st.columns(3)
    with f1:
        min_score = st.slider("Minimum Similarity Score", 0.50, 0.99, 0.75, 0.01)
    with f2:
        search_src = st.text_input("Filter Source URL", placeholder="source…")
    with f3:
        search_tgt = st.text_input("Filter Target URL", placeholder="target…")

    filtered = df[df["similarity_score"] >= min_score].copy()
    if search_src:
        filtered = filtered[filtered["source_url"].str.contains(search_src, case=False, na=False)]
    if search_tgt:
        filtered = filtered[filtered["target_url"].str.contains(search_tgt, case=False, na=False)]
    filtered = filtered.sort_values("similarity_score", ascending=False)

    st.caption(f"Showing **{len(filtered):,}** opportunities (score ≥ {min_score:.0%})")

    gold_divider()

    # ── Cards view ────────────────────────────────────────────────────────────
    section_header("◆", "Opportunity Cards")

    tab_cards, tab_table = st.tabs(["◈  Card View", "≡  Table View"])

    with tab_cards:
        if filtered.empty:
            empty_state("No opportunities match your filters.", "◆")
        else:
            tip_box("Each card shows a source page that should link to the target, with a suggested anchor text.")
            for _, row in filtered.head(60).iterrows():
                opportunity_card(
                    source_title=row.get("source_title",""),
                    source_url  =row.get("source_url",""),
                    target_title=row.get("target_title",""),
                    target_url  =row.get("target_url",""),
                    anchor      =row.get("suggested_anchor",""),
                    score       =float(row.get("similarity_score",0)),
                )
            if len(filtered) > 60:
                st.caption(f"Showing top 60 of {len(filtered):,}. Download CSV for full list.")

    with tab_table:
        st.dataframe(filtered, use_container_width=True, height=440, hide_index=True)

    gold_divider()

    # ── Export ────────────────────────────────────────────────────────────────
    section_header("↓", "Export")
    e1, e2 = st.columns(2)
    with e1:
        csv = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 Export CSV", csv, "link_opportunities.csv",
                           "text/csv", use_container_width=True)
    with e2:
        tip_box("Share this file with your content team to action the linking suggestions.")
