"""
app.py
───────
Streamlit entry point.

Current scope: input form only.
Full Dashboard will be built in the next phase.
"""

import sys
import os

# Ensure the project root is on sys.path when running from Streamlit Cloud
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from database.db    import init_db
from core.pipeline  import AnalysisPipeline
from config.settings import SUPPORTED_LANGUAGES

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEO Intelligence Tool",
    page_icon="🔍",
    layout="wide",
)

# ─── Init DB ──────────────────────────────────────────────────────────────────
init_db()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    max_pages = st.number_input(
        "Max Pages to Crawl",
        min_value=10,
        max_value=100_000,
        value=500,
        step=100,
        help="Set to a lower number for testing. Use 50,000+ for full site analysis.",
    )

# ─── Main area ────────────────────────────────────────────────────────────────
st.title("🔍 SEO Intelligence Tool")
st.markdown(
    "Crawl your entire website, analyse internal links, "
    "detect duplicates, and discover link opportunities — automatically."
)
st.divider()

col1, col2 = st.columns([3, 1])
with col1:
    url_input = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        label_visibility="visible",
    )
with col2:
    lang_options = list(SUPPORTED_LANGUAGES.keys())
    lang_labels  = list(SUPPORTED_LANGUAGES.values())
    selected_lang_label = st.selectbox("Language", lang_labels)
    selected_lang = lang_options[lang_labels.index(selected_lang_label)]

run_btn = st.button("🚀 Run Full Analysis", type="primary", use_container_width=True)

# ─── Run pipeline ─────────────────────────────────────────────────────────────
if run_btn:
    if not url_input or not url_input.startswith("http"):
        st.error("Please enter a valid URL starting with http:// or https://")
        st.stop()

    # ── Progress UI ────────────────────────────────────────────────────────
    progress_bar  = st.progress(0)
    status_text   = st.empty()

    STEPS = ["Crawling", "Meta Analysis", "Link Density",
             "Anchor NLP", "Clustering", "Duplicates", "Opportunities"]
    step_index    = {"name": "", "count": 0}

    def progress_cb(step: str, current: int, total: int):
        if step != step_index["name"]:
            step_index["name"]  = step
            step_index["count"] = STEPS.index(step) if step in STEPS else 0
        overall = int(
            (step_index["count"] / len(STEPS) + (current / max(total, 1)) / len(STEPS)) * 100
        )
        progress_bar.progress(min(overall, 100))
        status_text.markdown(f"**{step}** — {current} / {total}")

    # ── Execute ────────────────────────────────────────────────────────────
    with st.spinner("Analysis in progress …"):
        try:
            pipeline = AnalysisPipeline(
                base_url=url_input,
                language=selected_lang,
                max_pages=int(max_pages),
                progress_cb=progress_cb,
            )
            result = pipeline.run()
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    progress_bar.progress(100)
    status_text.markdown("✅ **Analysis complete!**")

    # ── Quick summary stats ────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Results Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pages Crawled",    len(result.pages_df))
    c2.metric("Meta Issues",      len(result.meta_df))
    c3.metric("Link Opportunities", len(result.opportunity_df))
    c4.metric("Duplicate Pairs",  len(result.duplicate_df))

    st.divider()

    # ── Export buttons ─────────────────────────────────────────────────────
    st.subheader("📥 Export Results")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        if st.button("📊 Export to Excel", use_container_width=True):
            with st.spinner("Generating Excel report …"):
                path = result.export_excel()
            with open(path, "rb") as f:
                st.download_button(
                    "⬇️ Download Excel",
                    data=f,
                    file_name=os.path.basename(path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

    with exp_col2:
        if st.button("📁 Export to CSV (ZIP)", use_container_width=True):
            with st.spinner("Generating CSV archive …"):
                path = result.export_csv_zip()
            with open(path, "rb") as f:
                st.download_button(
                    "⬇️ Download ZIP",
                    data=f,
                    file_name=os.path.basename(path),
                    mime="application/zip",
                    use_container_width=True,
                )

    # ── Raw data previews (collapsible) ───────────────────────────────────
    st.divider()
    with st.expander("🔗 Anchor Analysis Preview"):
        if not result.anchor_df.empty:
            st.dataframe(result.anchor_df.head(100), use_container_width=True)
        else:
            st.info("No anchor data.")

    with st.expander("🏷️ Content Clusters Preview"):
        if not result.cluster_df.empty:
            st.dataframe(result.cluster_df.head(100), use_container_width=True)
        else:
            st.info("No cluster data.")

    with st.expander("⚠️ Meta Issues Preview"):
        if not result.meta_df.empty:
            st.dataframe(result.meta_df.head(100), use_container_width=True)
        else:
            st.info("No meta issues found.")

    # Store result in session state for future dashboard use
    st.session_state["last_result"] = result
    st.session_state["last_session_id"] = result.session_id
