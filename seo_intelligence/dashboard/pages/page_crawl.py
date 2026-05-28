"""
dashboard/pages/page_crawl.py
──────────────────────────────
Crawl Management — URL input, settings, live progress monitor, logs.
"""

import time
import threading
import streamlit as st

from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    tip_box, progress_step, log_terminal, empty_state,
)
from config.settings import SUPPORTED_LANGUAGES


def render():
    page_header("⟳", "Crawl Management",
                "Configure and launch a full website crawl")

    result = st.session_state.get("last_result")

    # ── Two-column layout: Config left, Status right ───────────────────────
    col_cfg, col_status = st.columns([3, 2], gap="large")

    with col_cfg:
        section_header("◎", "Crawl Configuration")

        url = st.text_input(
            "Website URL",
            value=st.session_state.get("crawl_url", ""),
            placeholder="https://example.com",
        )

        lang_opts   = list(SUPPORTED_LANGUAGES.keys())
        lang_labels = list(SUPPORTED_LANGUAGES.values())
        lang_idx    = lang_opts.index(st.session_state.get("crawl_lang", "auto"))
        lang_sel    = st.selectbox("Content Language", lang_labels, index=lang_idx)
        lang_key    = lang_opts[lang_labels.index(lang_sel)]

        c1, c2 = st.columns(2)
        with c1:
            max_pages = st.number_input(
                "Max Pages",
                min_value=10, max_value=100_000,
                value=st.session_state.get("crawl_max_pages", 500),
                step=100,
                help="Safety cap. Set to 50,000+ for full site crawls.",
            )
        with c2:
            threads = st.number_input(
                "Concurrent Requests",
                min_value=1, max_value=20,
                value=10,
                help="Higher = faster but more server load.",
            )

        with st.expander("⚙ Advanced Options"):
            include_pattern = st.text_input(
                "Include URL Pattern (regex, optional)",
                placeholder=r"e\.g\. /blog/.*",
            )
            exclude_pattern = st.text_input(
                "Exclude URL Pattern (regex, optional)",
                placeholder=r"e\.g\. /tag/.*",
            )
            follow_noindex = st.checkbox("Crawl noindex pages", value=False)
            st.caption("These options are stored for future runs.")

        gold_divider()

        # ── Run button ─────────────────────────────────────────────────────
        run_disabled = bool(st.session_state.get("crawl_running"))
        if st.button(
            "🚀  Start Analysis" if not run_disabled else "⏳  Crawl in progress…",
            use_container_width=True,
            disabled=run_disabled,
            type="primary",
        ):
            if not url or not url.startswith("http"):
                st.error("Please enter a valid URL starting with https://")
            else:
                st.session_state["crawl_url"]       = url
                st.session_state["crawl_lang"]      = lang_key
                st.session_state["crawl_max_pages"] = int(max_pages)
                st.session_state["crawl_running"]   = True
                st.session_state["crawl_progress"]  = (0, 1)
                st.session_state["crawl_step"]      = "Starting…"
                st.session_state["crawl_logs"]      = []
                st.session_state["last_result"]     = None
                st.rerun()

    with col_status:
        section_header("◉", "Crawl Status")
        _render_status()

    # ── If currently running — execute pipeline ────────────────────────────
    if st.session_state.get("crawl_running"):
        _run_pipeline()


# ─── Status panel ─────────────────────────────────────────────────────────────

def _render_status():
    running = st.session_state.get("crawl_running", False)
    result  = st.session_state.get("last_result")

    STEPS = [
        "Crawling",
        "Meta Analysis",
        "Link Density",
        "Anchor NLP",
        "Clustering",
        "Duplicates",
        "Opportunities",
    ]
    current_step = st.session_state.get("crawl_step", "")
    step_done    = st.session_state.get("crawl_step_done", [])

    for step in STEPS:
        done   = step in step_done
        active = (step == current_step)
        progress_step(step, done=done, active=active)

    gold_divider()

    if running:
        current, total = st.session_state.get("crawl_progress", (0, 1))
        pct = int((current / max(total, 1)) * 100)
        st.progress(pct)
        st.caption(f"Step: **{current_step}** — {current:,} / {total:,}")
    elif result:
        st.success(f"✓ Analysis complete — {len(result.pages_df):,} pages processed")
        _show_summary(result)
    else:
        empty_state("No active crawl. Configure and start above.", "⟳")

    gold_divider()
    logs = st.session_state.get("crawl_logs", [])
    log_terminal(logs)


def _show_summary(result):
    st.markdown(f"""
    <div style="margin-top:0.75rem;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
        <div style="background:var(--black-4);border:1px solid var(--gold-border);
                    border-radius:var(--radius-sm);padding:0.6rem 0.9rem;">
          <div style="font-size:0.65rem;color:var(--white-muted);letter-spacing:.1em;
                      text-transform:uppercase;">Pages</div>
          <div style="font-size:1.4rem;font-family:'Cormorant Garamond',serif;
                      color:var(--gold-light);">{len(result.pages_df):,}</div>
        </div>
        <div style="background:var(--black-4);border:1px solid var(--gold-border);
                    border-radius:var(--radius-sm);padding:0.6rem 0.9rem;">
          <div style="font-size:0.65rem;color:var(--white-muted);letter-spacing:.1em;
                      text-transform:uppercase;">Meta Issues</div>
          <div style="font-size:1.4rem;font-family:'Cormorant Garamond',serif;
                      color:var(--gold-light);">{len(result.meta_df):,}</div>
        </div>
        <div style="background:var(--black-4);border:1px solid var(--gold-border);
                    border-radius:var(--radius-sm);padding:0.6rem 0.9rem;">
          <div style="font-size:0.65rem;color:var(--white-muted);letter-spacing:.1em;
                      text-transform:uppercase;">Opportunities</div>
          <div style="font-size:1.4rem;font-family:'Cormorant Garamond',serif;
                      color:var(--gold-light);">{len(result.opportunity_df):,}</div>
        </div>
        <div style="background:var(--black-4);border:1px solid var(--gold-border);
                    border-radius:var(--radius-sm);padding:0.6rem 0.9rem;">
          <div style="font-size:0.65rem;color:var(--white-muted);letter-spacing:.1em;
                      text-transform:uppercase;">Duplicates</div>
          <div style="font-size:1.4rem;font-family:'Cormorant Garamond',serif;
                      color:var(--gold-light);">{len(result.duplicate_df):,}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


# ─── Pipeline executor (blocking, with live progress) ─────────────────────────

def _run_pipeline():
    from core.pipeline import AnalysisPipeline

    url      = st.session_state["crawl_url"]
    lang     = st.session_state["crawl_lang"]
    max_pgs  = st.session_state["crawl_max_pages"]
    logs     = st.session_state.setdefault("crawl_logs", [])
    done_steps = st.session_state.setdefault("crawl_step_done", [])

    STEPS = ["Crawling","Meta Analysis","Link Density",
             "Anchor NLP","Clustering","Duplicates","Opportunities"]

    bar_placeholder  = st.empty()
    text_placeholder = st.empty()

    def progress_cb(step: str, current: int, total: int):
        st.session_state["crawl_step"]     = step
        st.session_state["crawl_progress"] = (current, total)
        if current >= total and step not in done_steps:
            done_steps.append(step)
        logs.append(f"[{step}] {current}/{total}")

    try:
        pipeline = AnalysisPipeline(
            base_url=url,
            language=lang,
            max_pages=max_pgs,
            progress_cb=progress_cb,
        )
        result = pipeline.run()
        st.session_state["last_result"]    = result
        st.session_state["last_session_id"]= result.session_id
        logs.append("✓ Analysis complete!")
    except Exception as e:
        logs.append(f"ERROR: {e}")
        st.error(f"Crawl failed: {e}")
    finally:
        st.session_state["crawl_running"]   = False
        st.session_state["crawl_step"]      = ""
        st.rerun()
