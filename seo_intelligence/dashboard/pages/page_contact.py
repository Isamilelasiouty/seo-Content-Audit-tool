"""
dashboard/pages/page_contact.py
─────────────────────────────────
Contact — Premium Gold/Black card for Ismail El Asiouty.
"""

import base64
import streamlit as st
from pathlib import Path
from dashboard.components.ui import page_header, gold_divider


LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"


def _logo_b64() -> str:
    try:
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def render():
    page_header("✦", "Contact",
                "Get in touch with the platform creator")

    b64 = _logo_b64()
    logo_html = (
        f'<img src="data:image/png;base64,{b64}" '
        f'style="width:90px;height:90px;object-fit:contain;'
        f'border-radius:16px;border:2px solid var(--gold-border);'
        f'box-shadow:0 0 30px rgba(201,168,76,0.3);">'
        if b64 else
        '<div style="font-size:4rem;">🔍</div>'
    )

    # ── Main contact card ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="contact-card">
      {logo_html}
      <div class="contact-name">Ismail El Asiouty</div>
      <div class="contact-role">
        SEO Specialist &nbsp;·&nbsp; User Experience Analysis<br>
        Building SEO Tools with Python &amp; AI &nbsp;·&nbsp; Content Optimization
      </div>

      <div style="display:flex;justify-content:center;gap:0.75rem;
                  flex-wrap:wrap;margin-bottom:1.5rem;">
        <a href="https://wa.me/201014672352" target="_blank"
           class="contact-btn contact-btn-wa">
          <span>💬</span> WhatsApp
        </a>
        <a href="https://www.linkedin.com/in/ismailelasiouty/" target="_blank"
           class="contact-btn contact-btn-li">
          <span>in</span> LinkedIn
        </a>
      </div>

      <div style="font-size:0.7rem;color:var(--white-muted);letter-spacing:0.05em;">
        Platform built with Python · Streamlit · Sentence Transformers · SQLite
      </div>
    </div>""", unsafe_allow_html=True)

    gold_divider()

    # ── About the platform ─────────────────────────────────────────────────────
    col_about, col_stack = st.columns(2, gap="large")

    with col_about:
        st.markdown("""
        <div class="content-card">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;
                      color:var(--white);margin-bottom:0.75rem;font-weight:600;">
            About This Platform
          </div>
          <div style="font-size:0.82rem;color:var(--white-muted);line-height:1.8;">
            SEO Intelligence is a production-grade tool built for SEO teams
            working on large-scale Arabic and English websites. It automates
            the most time-consuming parts of technical SEO — internal link
            auditing, content clustering, duplicate detection — using modern
            NLP and AI.<br><br>
            Built to scale to 50,000+ pages with async crawling, semantic
            embeddings, and professional reporting.
          </div>
        </div>""", unsafe_allow_html=True)

    with col_stack:
        stack = [
            ("🐍", "Python 3.12",           "Core language"),
            ("🚀", "Streamlit",             "Dashboard UI"),
            ("🤖", "Sentence Transformers", "Multilingual NLP"),
            ("🔍", "BeautifulSoup4 + lxml", "HTML parsing"),
            ("⚡", "aiohttp",              "Async crawling"),
            ("📊", "pandas + scikit-learn", "Data processing"),
            ("💾", "SQLite / PostgreSQL",   "Storage"),
            ("📈", "XlsxWriter",           "Excel reports"),
        ]
        rows = ""
        for icon, tech, role in stack:
            rows += f"""
            <div style="display:flex;align-items:center;gap:0.75rem;
                        padding:0.45rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
              <span style="font-size:1rem;width:24px;text-align:center;">{icon}</span>
              <div>
                <div style="font-size:0.8rem;color:var(--white);font-weight:500;">{tech}</div>
                <div style="font-size:0.68rem;color:var(--white-muted);">{role}</div>
              </div>
            </div>"""

        st.markdown(f"""
        <div class="content-card">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;
                      color:var(--white);margin-bottom:0.75rem;font-weight:600;">
            Tech Stack
          </div>
          {rows}
        </div>""", unsafe_allow_html=True)

    gold_divider()

    # ── Version info ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;">
      <div style="font-size:0.72rem;color:var(--white-muted);">
        SEO Intelligence Platform
        <span style="color:var(--gold);margin:0 0.4rem;">·</span>
        v1.0.0
        <span style="color:var(--gold);margin:0 0.4rem;">·</span>
        Built by Ismail El Asiouty
        <span style="color:var(--gold);margin:0 0.4rem;">·</span>
        <a href="https://github.com/" target="_blank"
           style="color:var(--gold);text-decoration:none;">GitHub ↗</a>
      </div>
    </div>""", unsafe_allow_html=True)
