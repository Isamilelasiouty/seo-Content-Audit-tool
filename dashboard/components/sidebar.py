"""
dashboard/components/sidebar.py
────────────────────────────────
Premium Gold/Black sidebar with logo, navigation, system status, quick stats.
"""

import base64
import os
import streamlit as st
from pathlib import Path

LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"

NAV_ITEMS = [
    # (key, icon, label, section)
    ("overview",      "◈",  "Dashboard Overview",   "MAIN"),
    ("crawl",         "⟳",  "Crawl Management",      "MAIN"),
    ("meta",          "◎",  "Meta Analyzer",         "ANALYSIS"),
    ("links",         "⇄",  "Internal Links",        "ANALYSIS"),
    ("anchors",       "⊹",  "Anchor Text Analysis",  "ANALYSIS"),
    ("opportunities", "◆",  "Link Opportunities",    "ANALYSIS"),
    ("duplicates",    "⧖",  "Duplicate Content",     "ANALYSIS"),
    ("clusters",      "⬡",  "Topic Clusters",        "ANALYSIS"),
    ("reports",       "↓",  "Reports Center",        "TOOLS"),
    ("team",          "⊞",  "Team Activity",         "TOOLS"),
    ("settings",      "⚙",  "Settings",              "TOOLS"),
    ("contact",       "✦",  "Contact",               "TOOLS"),
]


def _logo_b64() -> str | None:
    try:
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None


def render_sidebar() -> str:
    """Render sidebar and return the active page key."""
    if "active_page" not in st.session_state:
        st.session_state.active_page = "overview"

    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────
        b64 = _logo_b64()
        if b64:
            st.markdown(f"""
            <div class="sidebar-logo-wrap">
              <img src="data:image/png;base64,{b64}"
                   style="width:72px;height:72px;object-fit:contain;border-radius:12px;">
              <div class="sidebar-brand">SEO Intelligence</div>
              <div class="sidebar-version">v1.0 · PLATFORM</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="sidebar-logo-wrap">
              <div style="font-size:2.5rem;">🔍</div>
              <div class="sidebar-brand">SEO Intelligence</div>
              <div class="sidebar-version">v1.0 · PLATFORM</div>
            </div>""", unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────────────────────────
        current_section = None
        for key, icon, label, section in NAV_ITEMS:
            if section != current_section:
                current_section = section
                st.markdown(f'<div class="nav-section">{section}</div>',
                            unsafe_allow_html=True)

            active_cls = "active" if st.session_state.active_page == key else ""
            clicked = st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
            )
            if clicked:
                st.session_state.active_page = key
                st.rerun()

            # Inline style patch: highlight active button via JS-free CSS trick
            if active_cls:
                st.markdown(f"""
                <style>
                div[data-testid="stButton"] button[kind="secondary"]:last-child {{
                  background: var(--gold-glow) !important;
                  color: var(--gold) !important;
                  border: 1px solid var(--gold-border) !important;
                }}
                </style>""", unsafe_allow_html=True)

        # ── Gold divider ──────────────────────────────────────────────────
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

        # ── System Status ─────────────────────────────────────────────────
        db_ok = _check_db()
        st.markdown(f"""
        <div style="padding:0.75rem 1rem;">
          <div style="font-size:0.62rem;letter-spacing:0.12em;
                      text-transform:uppercase;color:var(--white-muted);
                      margin-bottom:0.5rem;">SYSTEM STATUS</div>
          <div style="font-size:0.78rem;color:var(--white-dim);margin-bottom:4px;">
            <span class="status-dot {'dot-green' if db_ok else 'dot-red'}"></span>
            Database {'Online' if db_ok else 'Offline'}
          </div>
          <div style="font-size:0.78rem;color:var(--white-dim);margin-bottom:4px;">
            <span class="status-dot dot-green"></span>
            NLP Engine Ready
          </div>
          <div style="font-size:0.78rem;color:var(--white-dim);">
            <span class="status-dot dot-green"></span>
            Crawler Online
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Quick Stats ───────────────────────────────────────────────────
        stats = _get_quick_stats()
        st.markdown(f"""
        <div class="gold-divider"></div>
        <div style="padding:0.75rem 1rem;">
          <div style="font-size:0.62rem;letter-spacing:0.12em;
                      text-transform:uppercase;color:var(--white-muted);
                      margin-bottom:0.6rem;">QUICK STATS</div>
          <div style="display:flex;justify-content:space-between;
                      font-size:0.78rem;margin-bottom:5px;">
            <span style="color:var(--white-muted);">Sessions</span>
            <span style="color:var(--gold);font-weight:600;">{stats['sessions']}</span>
          </div>
          <div style="display:flex;justify-content:space-between;
                      font-size:0.78rem;margin-bottom:5px;">
            <span style="color:var(--white-muted);">Pages Crawled</span>
            <span style="color:var(--gold);font-weight:600;">{stats['pages']:,}</span>
          </div>
          <div style="display:flex;justify-content:space-between;
                      font-size:0.78rem;">
            <span style="color:var(--white-muted);">Last Domain</span>
            <span style="color:var(--white-dim);font-size:0.72rem;
                         max-width:100px;overflow:hidden;
                         text-overflow:ellipsis;">{stats['last_domain']}</span>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Footer ────────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:0.75rem 1rem 1rem;text-align:center;">
          <div class="gold-divider"></div>
          <div style="font-size:0.65rem;color:var(--white-muted);margin-top:0.5rem;">
            Built by <span style="color:var(--gold);">Ismail El Asiouty</span>
          </div>
        </div>""", unsafe_allow_html=True)

    return st.session_state.active_page


def _check_db() -> bool:
    try:
        from database.db import init_db
        init_db()
        return True
    except Exception:
        return False


def _get_quick_stats() -> dict:
    try:
        from database.db import list_crawl_sessions, get_pages_for_session
        sessions = list_crawl_sessions()
        total_pages = sum(s.get("total_pages", 0) for s in sessions)
        last_domain = sessions[0]["domain"] if sessions else "—"
        return {"sessions": len(sessions), "pages": total_pages, "last_domain": last_domain}
    except Exception:
        return {"sessions": 0, "pages": 0, "last_domain": "—"}
