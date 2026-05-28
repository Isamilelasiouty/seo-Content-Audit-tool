"""
dashboard/pages/page_links.py
──────────────────────────────
Internal Links — full table with density, search, filter, export.
"""

import streamlit as st
import pandas as pd

from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    kpi_card, styled_dataframe, empty_state, tip_box,
)


def render():
    page_header("⇄", "Internal Links",
                "Explore all internal links and link density across your site")

    result = st.session_state.get("last_result")

    if result is None:
        empty_state("Run a crawl first to see internal link data.", "⇄")
        return

    anchor_df  = result.anchor_df   if not result.anchor_df.empty   else pd.DataFrame()
    density_df = result.density_df  if not result.density_df.empty  else pd.DataFrame()

    # ── KPI Row ───────────────────────────────────────────────────────────────
    total_links = len(anchor_df)
    rel_count   = len(anchor_df[anchor_df["relevance"] == "Relevant"])       if not anchor_df.empty else 0
    irrel_count = len(anchor_df[anchor_df["relevance"] == "Irrelevant"])     if not anchor_df.empty else 0
    generic_cnt = len(anchor_df[anchor_df["relevance"] == "Generic"])        if not anchor_df.empty else 0
    over_linked = len(density_df[density_df["density_status"] == "over_linked"])  if not density_df.empty else 0
    under_linked= len(density_df[density_df["density_status"] == "under_linked"]) if not density_df.empty else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi_card("⇄",  "Total Links",    f"{total_links:,}", badge="All")
    with c2: kpi_card("✓",  "Relevant",        f"{rel_count:,}",   badge_type="up",   badge="Good")
    with c3: kpi_card("✗",  "Irrelevant",      f"{irrel_count:,}", badge_type="down", badge="Fix")
    with c4: kpi_card("○",  "Generic Anchors", f"{generic_cnt:,}", badge_type="info", badge="Warn")
    with c5: kpi_card("≈",  "Under-linked",    f"{under_linked:,}",badge_type="info", badge="Opp")

    gold_divider()

    # ── Tabs: Anchors | Density ───────────────────────────────────────────────
    tab_anchors, tab_density = st.tabs(["⊹  Anchor Text Analysis", "≋  Link Density"])

    # ─────────────────────────────────────────────────────────────────────────
    with tab_anchors:
        if anchor_df.empty:
            empty_state("No anchor data available.", "⊹")
        else:
            _anchor_tab(anchor_df)

    # ─────────────────────────────────────────────────────────────────────────
    with tab_density:
        if density_df.empty:
            empty_state("No density data available.", "≋")
        else:
            _density_tab(density_df)


# ─── Anchor tab ───────────────────────────────────────────────────────────────

def _anchor_tab(df: pd.DataFrame):
    section_header("⊹", "Anchor Text Relevance")

    f1, f2, f3 = st.columns(3)
    with f1:
        rel_filter = st.multiselect(
            "Relevance",
            ["Relevant","Partially Relevant","Irrelevant","Generic"],
            default=["Relevant","Partially Relevant","Irrelevant","Generic"],
        )
    with f2:
        search_src = st.text_input("Search Source URL", placeholder="Filter by source…")
    with f3:
        search_anc = st.text_input("Search Anchor Text", placeholder="Filter by anchor…")

    filtered = df.copy()
    if rel_filter:
        filtered = filtered[filtered["relevance"].isin(rel_filter)]
    if search_src:
        filtered = filtered[filtered["source_url"].str.contains(search_src, case=False, na=False)]
    if search_anc:
        filtered = filtered[filtered["anchor_text"].str.contains(search_anc, case=False, na=False)]

    st.caption(f"Showing {len(filtered):,} of {len(df):,} links")

    # Render with relevance colour badges via HTML table for first 200 rows
    _render_anchor_table(filtered.head(300))

    gold_divider()
    csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 Export Anchors CSV", csv, "anchor_analysis.csv",
                       "text/csv", use_container_width=True)


def _render_anchor_table(df: pd.DataFrame):
    BADGE = {
        "Relevant":           '<span class="status-relevant">Relevant</span>',
        "Partially Relevant": '<span class="status-partial">Partial</span>',
        "Irrelevant":         '<span class="status-irrelevant">Irrelevant</span>',
        "Generic":            '<span class="status-generic">Generic</span>',
    }
    rows_html = ""
    for _, row in df.iterrows():
        badge = BADGE.get(row.get("relevance",""), "—")
        src   = str(row.get("source_url",""))[-60:]
        tgt   = str(row.get("target_url",""))[-55:]
        anc   = str(row.get("anchor_text",""))[:45]
        score = row.get("relevance_score", 0)
        rows_html += f"""
        <tr>
          <td title="{row.get('source_url','')}" style="max-width:220px;overflow:hidden;
               text-overflow:ellipsis;white-space:nowrap;font-size:0.75rem;
               color:var(--white-muted);">…{src}</td>
          <td title="{row.get('target_url','')}" style="max-width:200px;overflow:hidden;
               text-overflow:ellipsis;white-space:nowrap;font-size:0.75rem;
               color:var(--white-dim);">…{tgt}</td>
          <td style="color:var(--gold);font-style:italic;font-size:0.78rem;">{anc}</td>
          <td>{badge}</td>
          <td style="font-size:0.75rem;color:var(--white-muted);text-align:right;">{score:.3f}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table style="width:100%;border-collapse:collapse;font-family:'DM Sans',sans-serif;">
      <thead>
        <tr style="border-bottom:1px solid var(--gold-border);">
          <th style="padding:0.6rem 0.75rem;text-align:left;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">Source URL</th>
          <th style="padding:0.6rem 0.75rem;text-align:left;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">Target URL</th>
          <th style="padding:0.6rem 0.75rem;text-align:left;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">Anchor Text</th>
          <th style="padding:0.6rem 0.75rem;text-align:left;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">Relevance</th>
          <th style="padding:0.6rem 0.75rem;text-align:right;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">Score</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)


# ─── Density tab ──────────────────────────────────────────────────────────────

def _density_tab(df: pd.DataFrame):
    section_header("≋", "Link Density per Page")

    f1, f2 = st.columns(2)
    with f1:
        status_filter = st.multiselect(
            "Density Status",
            ["optimal", "under_linked", "over_linked"],
            default=["optimal","under_linked","over_linked"],
        )
    with f2:
        search_url = st.text_input("Search URL", placeholder="Filter by URL…", key="density_url")

    filtered = df.copy()
    if status_filter:
        filtered = filtered[filtered["density_status"].isin(status_filter)]
    if search_url:
        filtered = filtered[filtered["url"].str.contains(search_url, case=False, na=False)]

    st.caption(f"Showing {len(filtered):,} pages")

    # Bar chart: distribution of statuses
    dist = df["density_status"].value_counts()
    st.bar_chart(dist, color="#C9A84C", height=160)

    gold_divider()
    styled_dataframe(filtered, height=380)

    gold_divider()
    csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 Export Density CSV", csv, "link_density.csv",
                       "text/csv", use_container_width=True)
