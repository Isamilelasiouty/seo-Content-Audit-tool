"""
dashboard/pages/page_clusters.py
──────────────────────────────────
Topic Clusters — semantic page groups with similarity scores.
"""

import streamlit as st
import pandas as pd

from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    kpi_card, empty_state, tip_box,
)


def render():
    page_header("⬡", "Topic Clusters",
                "Semantic grouping of pages by content similarity")

    result = st.session_state.get("last_result")
    if result is None or result.cluster_df.empty:
        empty_state("No cluster data yet. Run a crawl to generate topic clusters.", "⬡")
        tip_box("Topic clusters help you understand your site architecture and find internal linking opportunities between related content.")
        return

    df = result.cluster_df.copy()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    n_clusters  = df["cluster_id"].nunique() if "cluster_id" in df.columns else 0
    n_pages     = len(df)
    avg_size    = round(n_pages / max(n_clusters, 1), 1)
    largest_cls = df.groupby("cluster_id").size().max() if n_clusters > 0 else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("⬡",  "Total Clusters",  f"{n_clusters:,}",  badge="Groups")
    with c2: kpi_card("📄", "Pages Clustered", f"{n_pages:,}",     badge="All")
    with c3: kpi_card("≈",  "Avg Cluster Size", f"{avg_size}",     badge_type="info", badge="Pages")
    with c4: kpi_card("★",  "Largest Cluster",  f"{largest_cls:,}", badge_type="info", badge="Pages")

    gold_divider()

    # ── Cluster size distribution ──────────────────────────────────────────────
    col_chart, col_top = st.columns([3, 2])

    with col_chart:
        section_header("◎", "Cluster Size Distribution")
        size_dist = df.groupby("cluster_id").size().reset_index(name="pages")
        size_dist = size_dist.sort_values("pages", ascending=False).head(30)
        # Add cluster name if available
        if "cluster_name" in df.columns:
            name_map = df.drop_duplicates("cluster_id").set_index("cluster_id")["cluster_name"]
            size_dist["name"] = size_dist["cluster_id"].map(name_map)
            size_dist["label"] = size_dist["name"].str[:30]
        else:
            size_dist["label"] = size_dist["cluster_id"].astype(str)
        st.bar_chart(size_dist.set_index("label")["pages"], color="#C9A84C", height=220)

    with col_top:
        section_header("◈", "Top Clusters by Size")
        top_clusters = size_dist.head(10)[["label","pages"]].copy()
        top_clusters.columns = ["Cluster", "Pages"]
        st.dataframe(top_clusters, use_container_width=True, height=250, hide_index=True)

    gold_divider()

    # ── Filter + Browse ───────────────────────────────────────────────────────
    section_header("⬡", "Browse Clusters")

    f1, f2 = st.columns(2)
    with f1:
        search_cluster = st.text_input("Search Cluster Name", placeholder="Filter by topic…")
    with f2:
        min_size = st.number_input("Minimum Cluster Size", min_value=1, value=2)

    # Get cluster options
    if "cluster_name" in df.columns:
        cluster_summary = df.groupby(["cluster_id","cluster_name"]).size().reset_index(name="count")
        cluster_summary = cluster_summary[cluster_summary["count"] >= min_size]
        if search_cluster:
            cluster_summary = cluster_summary[
                cluster_summary["cluster_name"].str.contains(search_cluster, case=False, na=False)
            ]
        cluster_summary = cluster_summary.sort_values("count", ascending=False)
    else:
        cluster_summary = df.groupby("cluster_id").size().reset_index(name="count")
        cluster_summary = cluster_summary[cluster_summary["count"] >= min_size]
        cluster_summary["cluster_name"] = "Cluster " + cluster_summary["cluster_id"].astype(str)
        cluster_summary = cluster_summary.sort_values("count", ascending=False)

    if cluster_summary.empty:
        st.info("No clusters match the current filters.")
        return

    # Render each cluster as an expandable card
    for _, cls_row in cluster_summary.iterrows():
        cid   = cls_row["cluster_id"]
        cname = cls_row.get("cluster_name", f"Cluster {cid}")
        csize = cls_row["count"]

        pages_in_cluster = df[df["cluster_id"] == cid][["url","title"]].copy()

        with st.expander(f"⬡  {cname[:80]}  —  {csize} pages", expanded=False):
            _render_cluster_card(pages_in_cluster, cname)

    gold_divider()

    # ── Export full clusters table ─────────────────────────────────────────────
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 Export Clusters CSV", csv, "topic_clusters.csv",
                       "text/csv", use_container_width=True)


def _render_cluster_card(pages: pd.DataFrame, cluster_name: str):
    tip_box(f"These pages share semantic similarity and should be interlinked within the '{cluster_name}' cluster.")

    rows_html = ""
    for _, row in pages.iterrows():
        url   = str(row.get("url",""))
        title = str(row.get("title","")) or url[-60:]
        rows_html += f"""
        <div style="display:flex;align-items:flex-start;gap:0.75rem;
                    padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
          <span style="color:var(--gold);margin-top:2px;flex-shrink:0;">⬡</span>
          <div>
            <div style="font-size:0.82rem;color:var(--white);font-weight:500;">
              {title[:80]}
            </div>
            <div style="font-size:0.7rem;color:var(--white-muted);margin-top:2px;">
              {url}
            </div>
          </div>
        </div>"""

    st.markdown(f"""
    <div style="background:var(--black-4);border:1px solid rgba(255,255,255,0.06);
                border-radius:var(--radius-sm);padding:0.75rem 1rem;
                max-height:320px;overflow-y:auto;">
      {rows_html}
    </div>""", unsafe_allow_html=True)
