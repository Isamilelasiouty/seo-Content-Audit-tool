"""
dashboard/pages/page_settings.py
──────────────────────────────────
Settings — Crawl, NLP, Language, Cache, API settings.
"""

import streamlit as st
from dashboard.components.ui import (
    page_header, section_header, gold_divider, tip_box,
)


def render():
    page_header("⚙", "Settings",
                "Configure crawl behaviour, NLP thresholds, and integrations")

    tab_crawl, tab_nlp, tab_lang, tab_api, tab_cache = st.tabs([
        "⟳  Crawl",
        "◎  NLP / AI",
        "🌐  Language",
        "🔗  API",
        "⚡  Cache",
    ])

    # ── Crawl Settings ────────────────────────────────────────────────────────
    with tab_crawl:
        section_header("⟳", "Crawler Configuration")
        c1, c2 = st.columns(2)
        with c1:
            max_concurrent = st.number_input(
                "Max Concurrent Requests", 1, 30,
                value=st.session_state.get("cfg_concurrent", 10),
                help="Parallel async requests. Higher = faster but may overload server.",
            )
            timeout = st.number_input(
                "Request Timeout (seconds)", 5, 120,
                value=st.session_state.get("cfg_timeout", 20),
            )
            retries = st.number_input(
                "Retry Attempts", 1, 10,
                value=st.session_state.get("cfg_retries", 3),
            )
        with c2:
            rate_delay = st.number_input(
                "Rate Limit Delay (seconds)", 0.0, 5.0,
                value=st.session_state.get("cfg_rate_delay", 0.3),
                step=0.1,
                help="Delay between requests to the same domain.",
            )
            max_pages = st.number_input(
                "Default Max Pages", 10, 100_000,
                value=st.session_state.get("cfg_max_pages", 500),
                step=100,
            )
            respect_robots = st.checkbox(
                "Respect robots.txt", value=True,
            )

        gold_divider()
        if st.button("💾  Save Crawl Settings", use_container_width=True):
            st.session_state["cfg_concurrent"]   = int(max_concurrent)
            st.session_state["cfg_timeout"]      = int(timeout)
            st.session_state["cfg_retries"]      = int(retries)
            st.session_state["cfg_rate_delay"]   = float(rate_delay)
            st.session_state["cfg_max_pages"]    = int(max_pages)

            # Apply to live config
            from config import settings
            settings.CRAWLER["max_concurrent_requests"] = int(max_concurrent)
            settings.CRAWLER["request_timeout"]         = int(timeout)
            settings.CRAWLER["retry_attempts"]          = int(retries)
            settings.CRAWLER["rate_limit_delay"]        = float(rate_delay)
            settings.CRAWLER["max_pages"]               = int(max_pages)
            settings.CRAWLER["respect_robots_txt"]      = respect_robots
            st.success("✓ Crawl settings saved for this session.")

    # ── NLP Settings ──────────────────────────────────────────────────────────
    with tab_nlp:
        section_header("◎", "NLP & AI Thresholds")
        c1, c2 = st.columns(2)
        with c1:
            cluster_thresh = st.slider(
                "Cluster Similarity Threshold", 0.50, 0.99, 0.75, 0.01,
                help="Pages above this similarity are grouped into the same cluster.",
            )
            dup_thresh = st.slider(
                "Duplicate Detection Threshold", 0.70, 0.99, 0.92, 0.01,
                help="Pages above this similarity are flagged as near-duplicates.",
            )
        with c2:
            anchor_high = st.slider(
                "Anchor Relevance — High Threshold", 0.40, 0.99, 0.65, 0.01,
                help="Above this = 'Relevant'.",
            )
            anchor_low = st.slider(
                "Anchor Relevance — Low Threshold", 0.10, 0.60, 0.35, 0.01,
                help="Below this = 'Irrelevant'.",
            )

        tip_box("These thresholds affect how the NLP engine classifies content. Lower thresholds = more matches (possibly noisier). Higher = fewer but more precise.")

        gold_divider()
        if st.button("💾  Save NLP Settings", use_container_width=True):
            from config import settings
            settings.NLP["similarity_threshold_cluster"]   = cluster_thresh
            settings.NLP["similarity_threshold_duplicate"] = dup_thresh
            settings.NLP["anchor_relevance_high"]          = anchor_high
            settings.NLP["anchor_relevance_low"]           = anchor_low
            st.success("✓ NLP settings applied.")

    # ── Language Settings ─────────────────────────────────────────────────────
    with tab_lang:
        section_header("🌐", "Language Configuration")

        default_lang = st.selectbox(
            "Default Analysis Language",
            ["auto", "ar", "en"],
            format_func=lambda x: {"auto":"Auto-detect","ar":"Arabic (العربية)","en":"English"}[x],
            index=0,
        )
        st.markdown("""
        <div class="content-card">
          <div style="font-size:0.82rem;color:var(--white-muted);line-height:1.7;">
            <strong style="color:var(--gold);">Arabic (ar)</strong> — Full RTL support, Arabic NLP embeddings via
            <code>paraphrase-multilingual-MiniLM-L12-v2</code>.<br>
            <strong style="color:var(--gold);">English (en)</strong> — Standard LTR crawl and analysis.<br>
            <strong style="color:var(--gold);">Auto-detect</strong> — Language detected per page using
            <code>langdetect</code>. Best for mixed-language sites.
          </div>
        </div>""", unsafe_allow_html=True)

        gold_divider()
        if st.button("💾  Save Language Settings", use_container_width=True):
            st.session_state["crawl_lang"] = default_lang
            st.success(f"✓ Default language set to '{default_lang}'.")

    # ── API Settings ──────────────────────────────────────────────────────────
    with tab_api:
        section_header("🔗", "API Integrations")

        st.markdown("""
        <div class="content-card" style="margin-bottom:1rem;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;
                      color:var(--white);margin-bottom:0.75rem;">
            Connect External APIs
          </div>
          <div style="font-size:0.78rem;color:var(--white-muted);">
            Link your Google Search Console, Ahrefs, or SEMrush accounts
            to enrich the analysis with real traffic and ranking data.
          </div>
        </div>""", unsafe_allow_html=True)

        integrations = [
            ("Google Search Console", "GSC_API_KEY",   "🔍"),
            ("Ahrefs",                "AHREFS_API_KEY", "📈"),
            ("SEMrush",               "SEMRUSH_KEY",    "📊"),
        ]

        for name, key, icon in integrations:
            val = st.text_input(
                f"{icon}  {name} API Key",
                type="password",
                placeholder="Enter API key…",
                key=f"api_{key}",
            )
            if val:
                st.session_state[f"api_key_{key}"] = val

        gold_divider()
        if st.button("💾  Save API Keys", use_container_width=True):
            st.success("✓ API keys saved to session (will be used in next analysis).")
        tip_box("API keys are stored in session memory only. They are not persisted to disk.")

    # ── Cache Settings ─────────────────────────────────────────────────────────
    with tab_cache:
        section_header("⚡", "Cache & Storage")

        try:
            from database.db import list_crawl_sessions
            sessions = list_crawl_sessions()
            total_sessions = len(sessions)
            total_pages    = sum(s.get("total_pages",0) for s in sessions)
        except Exception:
            total_sessions, total_pages = 0, 0

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1rem;">
          <div style="background:var(--black-4);border:1px solid var(--gold-border);
                      border-radius:var(--radius-sm);padding:1rem;">
            <div style="font-size:0.65rem;color:var(--white-muted);
                        text-transform:uppercase;letter-spacing:.1em;">Crawl Sessions</div>
            <div style="font-size:1.8rem;font-family:'Cormorant Garamond',serif;
                        color:var(--gold-light);">{total_sessions}</div>
          </div>
          <div style="background:var(--black-4);border:1px solid var(--gold-border);
                      border-radius:var(--radius-sm);padding:1rem;">
            <div style="font-size:0.65rem;color:var(--white-muted);
                        text-transform:uppercase;letter-spacing:.1em;">Total Pages Stored</div>
            <div style="font-size:1.8rem;font-family:'Cormorant Garamond',serif;
                        color:var(--gold-light);">{total_pages:,}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        gold_divider()
        if st.button("🗑️  Clear Session State", use_container_width=True):
            keys = ["last_result","last_session_id","crawl_running",
                    "crawl_logs","crawl_step","crawl_step_done","crawl_progress"]
            for k in keys:
                st.session_state.pop(k, None)
            st.success("✓ Session state cleared.")
            st.rerun()

        tip_box("The SQLite database is stored locally and persists across Streamlit restarts. To migrate to PostgreSQL, update DATABASE['url'] in config/settings.py.")
