"""
dashboard/pages/page_reports.py
─────────────────────────────────
Reports Center — generate and download Excel / CSV reports.
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime

from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    kpi_card, empty_state, tip_box,
)
from config.settings import EXPORT_DIR


def render():
    page_header("↓", "Reports Center",
                "Generate and download professional SEO analysis reports")

    result = st.session_state.get("last_result")

    # ── Generate new reports ───────────────────────────────────────────────────
    section_header("◆", "Generate Report")

    if result is None:
        empty_state("No analysis data available. Run a crawl first.", "↓")
        tip_box("Go to Crawl Management and run an analysis to unlock reports.")
        return

    # Stats preview
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("📄","Pages",         f"{len(result.pages_df):,}")
    with c2: kpi_card("⚠","Meta Issues",    f"{len(result.meta_df):,}")
    with c3: kpi_card("◆","Opportunities",  f"{len(result.opportunity_df):,}")
    with c4: kpi_card("⬡","Clusters",       f"{result.cluster_df['cluster_id'].nunique() if not result.cluster_df.empty and 'cluster_id' in result.cluster_df.columns else 0:,}")

    gold_divider()

    col_excel, col_csv = st.columns(2, gap="large")

    with col_excel:
        st.markdown("""
        <div class="content-card">
          <div style="font-size:1.5rem;margin-bottom:0.5rem;">📊</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;
                      color:var(--white);font-weight:600;margin-bottom:0.4rem;">
            Full Excel Report
          </div>
          <div style="font-size:0.78rem;color:var(--white-muted);line-height:1.5;">
            8 colour-coded sheets: Pages, Meta Issues, Anchor Analysis,
            Link Density, Opportunities, Clusters, Duplicates, Summary.
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("📊  Generate Excel Report", use_container_width=True, type="primary"):
            with st.spinner("Building Excel report…"):
                try:
                    from core.exporters.excel_exporter import export_to_excel
                    path = export_to_excel(
                        domain=result.domain,
                        pages_df=result.pages_df,
                        meta_df=result.meta_df,
                        anchor_df=result.anchor_df,
                        density_df=result.density_df,
                        opportunity_df=result.opportunity_df,
                        cluster_df=result.cluster_df,
                        duplicate_df=result.duplicate_df,
                    )
                    with open(path,"rb") as f:
                        st.download_button(
                            "⬇️  Download Excel",
                            data=f,
                            file_name=os.path.basename(path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                    st.success("✓ Excel report ready!")
                except Exception as e:
                    st.error(f"Export failed: {e}")

    with col_csv:
        st.markdown("""
        <div class="content-card">
          <div style="font-size:1.5rem;margin-bottom:0.5rem;">📁</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;
                      color:var(--white);font-weight:600;margin-bottom:0.4rem;">
            CSV Archive (ZIP)
          </div>
          <div style="font-size:0.78rem;color:var(--white-muted);line-height:1.5;">
            Individual CSV files for each module, zipped for easy sharing
            with developers or SEO tools.
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("📁  Generate CSV Archive", use_container_width=True):
            with st.spinner("Building CSV archive…"):
                try:
                    from core.exporters.csv_exporter import export_to_csv_zip
                    path = export_to_csv_zip(
                        domain=result.domain,
                        pages_df=result.pages_df,
                        meta_df=result.meta_df,
                        anchor_df=result.anchor_df,
                        density_df=result.density_df,
                        opportunity_df=result.opportunity_df,
                        cluster_df=result.cluster_df,
                        duplicate_df=result.duplicate_df,
                    )
                    with open(path,"rb") as f:
                        st.download_button(
                            "⬇️  Download ZIP",
                            data=f,
                            file_name=os.path.basename(path),
                            mime="application/zip",
                            use_container_width=True,
                        )
                    st.success("✓ CSV archive ready!")
                except Exception as e:
                    st.error(f"Export failed: {e}")

    gold_divider()

    # ── Saved reports (files on disk) ─────────────────────────────────────────
    section_header("◈", "Saved Reports")
    _list_saved_reports()


def _list_saved_reports():
    try:
        files = sorted(
            [f for f in os.listdir(EXPORT_DIR)
             if f.endswith((".xlsx",".zip",".csv"))],
            reverse=True,
        )
    except Exception:
        files = []

    if not files:
        empty_state("No saved reports yet.", "↓")
        return

    rows_html = ""
    for fname in files[:20]:
        fpath = os.path.join(EXPORT_DIR, fname)
        try:
            size_kb = os.path.getsize(fpath) // 1024
            mtime   = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M")
        except Exception:
            size_kb, mtime = 0, "—"

        icon = "📊" if fname.endswith(".xlsx") else ("📁" if fname.endswith(".zip") else "📄")
        rows_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.6rem 0.9rem;border-bottom:1px solid rgba(255,255,255,0.04);
                    font-size:0.8rem;">
          <div>
            <span style="margin-right:0.5rem;">{icon}</span>
            <span style="color:var(--white-dim);">{fname}</span>
          </div>
          <div style="display:flex;gap:1.5rem;color:var(--white-muted);font-size:0.72rem;">
            <span>{size_kb} KB</span>
            <span>{mtime}</span>
          </div>
        </div>"""

    st.markdown(f"""
    <div style="background:var(--black-3);border:1px solid var(--gold-border);
                border-radius:var(--radius-md);overflow:hidden;">
      {rows_html}
    </div>""", unsafe_allow_html=True)

    tip_box(f"{len(files)} reports saved locally. Reports persist between sessions.")
