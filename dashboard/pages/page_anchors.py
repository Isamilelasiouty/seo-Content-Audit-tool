"""
dashboard/pages/page_anchors.py
────────────────────────────────
Anchor Text Analysis — deep dive with NLP scores, charts, per-page breakdown.
"""

import streamlit as st
import pandas as pd

from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    kpi_card, empty_state, tip_box, mini_bar,
)


def render():
    page_header("⊹", "Anchor Text Analysis",
                "NLP-powered relevance scoring for every internal link anchor")

    result = st.session_state.get("last_result")
    if result is None or result.anchor_df.empty:
        empty_state("No anchor data available. Run a crawl first.", "⊹")
        return

    df = result.anchor_df.copy()

    # ── KPI Row ───────────────────────────────────────────────────────────────
    total    = len(df)
    relevant = len(df[df["relevance"] == "Relevant"])
    partial  = len(df[df["relevance"] == "Partially Relevant"])
    irrel    = len(df[df["relevance"] == "Irrelevant"])
    generic  = len(df[df["relevance"] == "Generic"])
    avg_score= df["relevance_score"].mean() if "relevance_score" in df.columns else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi_card("⊹",  "Total Anchors",  f"{total:,}",      badge="Scanned")
    with c2: kpi_card("✓",  "Relevant",        f"{relevant:,}",   badge_type="up",   badge=f"{int(relevant/max(total,1)*100)}%")
    with c3: kpi_card("~",  "Partial",         f"{partial:,}",    badge_type="info", badge=f"{int(partial/max(total,1)*100)}%")
    with c4: kpi_card("✗",  "Irrelevant",      f"{irrel:,}",      badge_type="down", badge=f"{int(irrel/max(total,1)*100)}%")
    with c5: kpi_card("◌",  "Avg Score",       f"{avg_score:.2f}",badge_type="info", badge="NLP")

    gold_divider()

    # ── Distribution chart ────────────────────────────────────────────────────
    col_chart, col_dist = st.columns([3, 2])

    with col_chart:
        section_header("◎", "Relevance Distribution")
        dist_data = df["relevance"].value_counts().reset_index()
        dist_data.columns = ["Relevance", "Count"]
        st.bar_chart(dist_data.set_index("Relevance"), color="#C9A84C", height=200)

    with col_dist:
        section_header("≋", "Score Histogram")
        if "relevance_score" in df.columns:
            hist_df = df["relevance_score"].clip(0, 1)
            import numpy as np
            counts, bins = np.histogram(hist_df, bins=10, range=(0, 1))
            hist_data = pd.DataFrame({
                "Range": [f"{bins[i]:.1f}–{bins[i+1]:.1f}" for i in range(len(counts))],
                "Count": counts,
            })
            st.bar_chart(hist_data.set_index("Range"), color="#8B6914", height=200)

    gold_divider()

    # ── Top problematic anchors ───────────────────────────────────────────────
    section_header("⚠", "Anchors Needing Attention")

    bad = df[df["relevance"].isin(["Irrelevant", "Generic"])].copy()
    if bad.empty:
        st.success("✓ All anchors are relevant or partially relevant.")
    else:
        bad_sorted = bad.sort_values("relevance_score").head(50)
        tip_box(f"{len(bad):,} anchors flagged as Irrelevant or Generic — review and update.")

        for _, row in bad_sorted.iterrows():
            badge_cls = "status-irrelevant" if row["relevance"] == "Irrelevant" else "status-generic"
            src_short = str(row.get("source_url",""))[-65:]
            tgt_short = str(row.get("target_url",""))[-55:]
            anc       = str(row.get("anchor_text",""))[:50] or "(empty)"
            score     = float(row.get("relevance_score", 0))
            st.markdown(f"""
            <div style="background:var(--black-4);border:1px solid rgba(255,255,255,0.06);
                        border-radius:var(--radius-sm);padding:0.8rem 1rem;
                        margin-bottom:0.5rem;transition:all .2s;">
              <div style="display:flex;justify-content:space-between;
                          align-items:flex-start;gap:1rem;flex-wrap:wrap;">
                <div style="flex:1;min-width:0;">
                  <div style="font-size:0.72rem;color:var(--white-muted);
                              margin-bottom:3px;">…{src_short}</div>
                  <div style="font-size:0.82rem;color:var(--white);
                              font-weight:500;margin-bottom:4px;">
                    "<span style="color:var(--gold);font-style:italic;">{anc}</span>"
                    → …{tgt_short}
                  </div>
                  <div style="height:4px;background:var(--black-5);
                              border-radius:2px;width:120px;">
                    <div style="height:100%;width:{int(score*100)}%;
                                background:#F87171;border-radius:2px;"></div>
                  </div>
                </div>
                <span class="{badge_cls}">{row["relevance"]}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    gold_divider()

    # ── Per-page breakdown ────────────────────────────────────────────────────
    section_header("◈", "Per-Page Anchor Summary")

    if not df.empty and "source_url" in df.columns:
        page_summary = df.groupby("source_url").agg(
            total_anchors   = ("anchor_text",    "count"),
            relevant_count  = ("relevance",      lambda x: (x == "Relevant").sum()),
            avg_score       = ("relevance_score","mean"),
        ).reset_index()
        page_summary["relevant_%"] = (
            page_summary["relevant_count"] / page_summary["total_anchors"] * 100
        ).round(1)
        page_summary = page_summary.sort_values("avg_score").head(100)
        st.dataframe(page_summary, use_container_width=True, height=350, hide_index=True)

    gold_divider()
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 Export Full Anchor CSV", csv, "anchor_analysis.csv",
                       "text/csv", use_container_width=True)
