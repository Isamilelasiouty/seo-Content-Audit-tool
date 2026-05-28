"""
app.py
───────
SEO Intelligence Platform — Main Streamlit entry point.
Routes between pages using session_state.active_page.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title  = "SEO Intelligence Platform",
    page_icon   = "🔍",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from database.db          import init_db
from dashboard.styles.theme import inject_css
from dashboard.components.sidebar import render_sidebar

# ── Pages ─────────────────────────────────────────────────────────────────────
from dashboard.pages import (
    page_overview,
    page_crawl,
    page_meta,
    page_links,
    page_anchors,
    page_opportunities,
    page_duplicates,
    page_clusters,
    page_reports,
    page_team,
    page_settings,
    page_contact,
    page_404,
)

PAGE_MAP = {
    "overview":      page_overview,
    "crawl":         page_crawl,
    "meta":          page_meta,
    "links":         page_links,
    "anchors":       page_anchors,
    "opportunities": page_opportunities,
    "duplicates":    page_duplicates,
    "clusters":      page_clusters,
    "reports":       page_reports,
    "team":          page_team,
    "settings":      page_settings,
    "contact":       page_contact,
}

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
inject_css()

# ── Sidebar → active page key ─────────────────────────────────────────────────
active_page = render_sidebar()

# ── Render active page ────────────────────────────────────────────────────────
page_module = PAGE_MAP.get(active_page, page_404)
page_module.render()
