"""
dashboard/pages/page_duplicates.py
────────────────────────────────────
Duplicate Content — exact duplicates, near-duplicates, title duplicates.
"""

import streamlit as st
import pandas as pd

from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    kpi_card, empty_state, tip_box, styled_dataframe,
)


DUP_TYPE_LABELS = {
    "title_duplicate":       "Duplicate Title",
    "near_duplicate":        "Near-Duplicate Content",
    "near_duplicate_tfidf":  "Near-Duplicate (TF-IDF)",
    "exact":                 "Exact Duplicate",
}

DUP_TYPE_COLOR = {
    "title_duplicate":       "#FBBF24",
    "near_duplicate":        "#F87171",
    "near_duplicate_tfidf":  "#FB923C",
    "exact":                 "#EF4444",
}


def render():
    page_header("⧖", "Duplicate Content",
                "Identify exact, near-duplicate and title-duplicate pages")

    result = st.session_state.get("last_result")
    if result is None or result.duplicate_df.empty:
        empty_state("No duplicate data yet. Run a crawl to detect duplicates.", "⧖")
        return

    df = result.duplicate_df.copy()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    exact_dups  = len(df[df["duplicate_type"] == "title_duplicate"])
    near_dups   = len(df[df["duplicate_type"].isin(["near_duplicate","near_duplicate_tfidf"])])
    high_sim    = len(df[df["similarity_score"] >= 0.95])
    unique_urls = pd.unique(df[["url_a","url_b"]].values.ravel()).shape[0] if not df.empty else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("⧖",  "Duplicate Pairs",   f"{len(df):,}",    badge="Total")
    with c2: kpi_card("≡",  "Title Duplicates",  f"{exact_dups:,}", badge_type="down", badge="Error")
    with c3: kpi_card("~",  "Near-Duplicates",   f"{near_dups:,}",  badge_type="down", badge="Warn")
    with c4: kpi_card("📄", "Affected Pages",    f"{unique_urls:,}",badge_type="info", badge="URLs")

    gold_divider()

    # ── Type breakdown ────────────────────────────────────────────────────────
    col_chart, col_info = st.columns([3, 2])

    with col_chart:
        section_header("◎", "Duplicate Type Breakdown")
        type_dist = df["duplicate_type"].value_counts().reset_index()
        type_dist.columns = ["Type", "Count"]
        type_dist["Type"] = type_dist["Type"].map(lambda x: DUP_TYPE_LABELS.get(x, x))
        st.bar_chart(type_dist.set_index("Type"), color="#C9A84C", height=200)

    with col_info:
        section_header("◉", "Similarity Score Distribution")
        if "similarity_score" in df.columns:
            bins_labels = ["0.70–0.80","0.80–0.90","0.90–0.95","0.95–1.00"]
            bins_counts = [
                len(df[(df["similarity_score"]>=0.70)&(df["similarity_score"]<0.80)]),
                len(df[(df["similarity_score"]>=0.80)&(df["similarity_score"]<0.90)]),
                len(df[(df["similarity_score"]>=0.90)&(df["similarity_score"]<0.95)]),
                len(df[df["similarity_score"]>=0.95]),
            ]
            score_dist = pd.DataFrame({"Range":bins_labels,"Count":bins_counts})
            st.bar_chart(score_dist.set_index("Range"), color="#8B6914", height=200)

    gold_divider()

    # ── Filters + Table ───────────────────────────────────────────────────────
    section_header("⊹", "Filter Duplicates")
    f1, f2, f3 = st.columns(3)
    with f1:
        type_filter = st.multiselect(
            "Duplicate Type",
            options=list(DUP_TYPE_LABELS.values()),
            default=list(DUP_TYPE_LABELS.values()),
        )
    with f2:
        min_sim = st.slider("Min Similarity Score", 0.70, 1.00, 0.70, 0.01)
    with f3:
        search_url = st.text_input("Search URL", placeholder="Filter by URL…")

    type_reverse = {v: k for k, v in DUP_TYPE_LABELS.items()}
    selected_types = [type_reverse.get(t, t) for t in type_filter]

    filtered = df[df["duplicate_type"].isin(selected_types)].copy()
    filtered = filtered[filtered["similarity_score"] >= min_sim]
    if search_url:
        mask = (
            filtered["url_a"].str.contains(search_url, case=False, na=False) |
            filtered["url_b"].str.contains(search_url, case=False, na=False)
        )
        filtered = filtered[mask]

    filtered = filtered.sort_values("similarity_score", ascending=False)

    st.caption(f"Showing **{len(filtered):,}** pairs")
    gold_divider()

    # ── Colour-coded table ─────────────────────────────────────────────────────
    section_header("≡", "Duplicate Pairs")
    _render_dup_table(filtered.head(200))

    gold_divider()

    # ── High similarity alert ─────────────────────────────────────────────────
    critical = filtered[filtered["similarity_score"] >= 0.98]
    if not critical.empty:
        st.warning(f"⚠ {len(critical)} pairs have similarity ≥ 98% — consider canonical tags or consolidation.")

    tip_box("Use canonical tags or 301 redirects to resolve duplicate content issues and consolidate link equity.")

    gold_divider()

    # ── Export ────────────────────────────────────────────────────────────────
    csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 Export Duplicates CSV", csv, "duplicates.csv",
                       "text/csv", use_container_width=True)


def _render_dup_table(df: pd.DataFrame):
    if df.empty:
        st.info("No duplicates match the current filters.")
        return

    rows_html = ""
    for _, row in df.iterrows():
        dtype = row.get("duplicate_type","")
        color = DUP_TYPE_COLOR.get(dtype, "var(--white-muted)")
        label = DUP_TYPE_LABELS.get(dtype, dtype)
        score = float(row.get("similarity_score", 0))
        url_a = str(row.get("url_a",""))
        url_b = str(row.get("url_b",""))
        score_pct = int(score * 100)
        rows_html += f"""
        <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
          <td style="padding:0.6rem 0.75rem;font-size:0.75rem;color:var(--white-muted);
                     max-width:260px;overflow:hidden;text-overflow:ellipsis;
                     white-space:nowrap;" title="{url_a}">{url_a[-70:]}</td>
          <td style="padding:0.6rem 0.75rem;font-size:0.75rem;color:var(--white-dim);
                     max-width:260px;overflow:hidden;text-overflow:ellipsis;
                     white-space:nowrap;" title="{url_b}">{url_b[-70:]}</td>
          <td style="padding:0.6rem 0.75rem;white-space:nowrap;">
            <span style="background:rgba(255,255,255,0.05);color:{color};
                         font-size:0.7rem;padding:2px 8px;border-radius:20px;
                         border:1px solid {color}33;font-weight:600;">{label}</span>
          </td>
          <td style="padding:0.6rem 0.75rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <div style="height:4px;width:80px;background:var(--black-4);
                          border-radius:2px;">
                <div style="height:100%;width:{score_pct}%;
                            background:{color};border-radius:2px;"></div>
              </div>
              <span style="font-size:0.75rem;color:{color};font-weight:600;">
                {score:.3f}
              </span>
            </div>
          </td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table style="width:100%;border-collapse:collapse;font-family:'DM Sans',sans-serif;">
      <thead>
        <tr style="border-bottom:1px solid var(--gold-border);">
          <th style="padding:0.6rem 0.75rem;text-align:left;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">URL A</th>
          <th style="padding:0.6rem 0.75rem;text-align:left;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">URL B</th>
          <th style="padding:0.6rem 0.75rem;text-align:left;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">Type</th>
          <th style="padding:0.6rem 0.75rem;text-align:left;font-size:0.68rem;
                     letter-spacing:.1em;text-transform:uppercase;color:var(--gold);
                     background:var(--black-4);">Similarity</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)
