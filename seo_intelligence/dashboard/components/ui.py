"""
dashboard/components/ui.py
───────────────────────────
Reusable HTML/CSS component helpers.
All functions return HTML strings or call st.markdown directly.
"""

import streamlit as st
import pandas as pd
from typing import Optional


# ── Page Header ──────────────────────────────────────────────────────────────

def page_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
      <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.25rem;">
        <span style="font-size:1.6rem;">{icon}</span>
        <h1 class="page-title">{title}</h1>
      </div>
      {'<p class="page-subtitle">' + subtitle + '</p>' if subtitle else ''}
      <div class="gold-divider"></div>
    </div>""", unsafe_allow_html=True)


# ── KPI Card Row ─────────────────────────────────────────────────────────────

def kpi_card(icon: str, label: str, value, sub: str = "",
             badge: str = "", badge_type: str = "info"):
    badge_html = ""
    if badge:
        badge_html = f'<span class="kpi-badge badge-{badge_type}">{badge}</span>'

    st.markdown(f"""
    <div class="kpi-card">
      {badge_html}
      <span class="kpi-icon">{icon}</span>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {'<div class="kpi-sub">' + sub + '</div>' if sub else ''}
    </div>""", unsafe_allow_html=True)


# ── Section Header ────────────────────────────────────────────────────────────

def section_header(icon: str, title: str):
    st.markdown(f"""
    <div class="section-header">
      <div class="section-icon">{icon}</div>
      <h2>{title}</h2>
    </div>""", unsafe_allow_html=True)


# ── Gold Divider ─────────────────────────────────────────────────────────────

def gold_divider():
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)


# ── Status Badge ─────────────────────────────────────────────────────────────

def status_badge(value: str) -> str:
    """Return an HTML badge span for a relevance/status value."""
    css_map = {
        "relevant":          "status-relevant",
        "partially relevant":"status-partial",
        "irrelevant":        "status-irrelevant",
        "generic":           "status-generic",
        "optimal":           "status-optimal",
        "over_linked":       "status-over_linked",
        "under_linked":      "status-under_linked",
    }
    cls = css_map.get(str(value).lower(), "status-generic")
    return f'<span class="{cls}">{value}</span>'


# ── Styled DataFrame ──────────────────────────────────────────────────────────

def styled_dataframe(df: pd.DataFrame, height: int = 400):
    """Render a dataframe with the platform theme."""
    if df is None or df.empty:
        empty_state("No data available.")
        return
    st.dataframe(df, use_container_width=True, height=height,
                 hide_index=True)


# ── Empty State ───────────────────────────────────────────────────────────────

def empty_state(message: str = "No data yet.", icon: str = "◎"):
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem;
                border:1px dashed var(--gold-border);
                border-radius:var(--radius-md);
                background:var(--black-3);">
      <div style="font-size:2rem;margin-bottom:0.75rem;color:var(--gold-dim);">{icon}</div>
      <div style="color:var(--white-muted);font-size:0.85rem;">{message}</div>
    </div>""", unsafe_allow_html=True)


# ── Info / Tip Box ────────────────────────────────────────────────────────────

def tip_box(text: str):
    st.markdown(f'<div class="tip">💡 {text}</div>', unsafe_allow_html=True)


# ── Progress Step ─────────────────────────────────────────────────────────────

def progress_step(label: str, done: bool = False, active: bool = False):
    color = "#34D399" if done else ("var(--gold)" if active else "var(--white-muted)")
    icon  = "✓" if done else ("◉" if active else "○")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.6rem;
                padding:0.4rem 0;font-size:0.82rem;color:{color};">
      <span style="font-size:0.9rem;">{icon}</span>
      <span>{label}</span>
    </div>""", unsafe_allow_html=True)


# ── Opportunity Card ──────────────────────────────────────────────────────────

def opportunity_card(source_title: str, source_url: str,
                     target_title: str, target_url: str,
                     anchor: str, score: float):
    pct = int(score * 100)
    st.markdown(f"""
    <div class="opp-card">
      <div class="opp-arrow">→</div>
      <div style="flex:1;min-width:0;">
        <div class="opp-source" title="{source_url}">
          {source_title[:60] or source_url[:60]}
        </div>
        <div class="opp-target" title="{target_url}">
          ↳ {target_title[:70] or target_url[:70]}
        </div>
        <div style="display:flex;align-items:center;gap:0.75rem;margin-top:4px;">
          <span class="opp-anchor">"{anchor[:50]}"</span>
          <span class="opp-score">Similarity: {pct}%</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


# ── SEO Health Score Ring ─────────────────────────────────────────────────────

def health_score_ring(score: int):
    """Render an SVG ring showing the SEO health score (0-100)."""
    r      = 54
    circ   = 2 * 3.14159 * r
    dash   = (score / 100) * circ
    gap    = circ - dash
    color  = "#34D399" if score >= 70 else ("#FBBF24" if score >= 40 else "#F87171")

    st.markdown(f"""
    <div class="health-ring">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="{r}" fill="none"
                stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
        <circle cx="70" cy="70" r="{r}" fill="none"
                stroke="{color}" stroke-width="10"
                stroke-dasharray="{dash:.1f} {gap:.1f}"
                stroke-dashoffset="{circ/4:.1f}"
                stroke-linecap="round"/>
        <text x="70" y="65" text-anchor="middle" fill="{color}"
              font-family="Cormorant Garamond,serif"
              font-size="28" font-weight="700">{score}</text>
        <text x="70" y="84" text-anchor="middle"
              fill="rgba(255,255,255,0.45)"
              font-family="DM Sans,sans-serif" font-size="11">SEO HEALTH</text>
      </svg>
    </div>""", unsafe_allow_html=True)


# ── Mini Bar ──────────────────────────────────────────────────────────────────

def mini_bar(value: float, max_val: float = 1.0, color: str = "var(--gold)"):
    pct = min(int((value / max(max_val, 0.001)) * 100), 100)
    st.markdown(f"""
    <div style="height:6px;background:var(--black-4);
                border-radius:3px;overflow:hidden;">
      <div style="height:100%;width:{pct}%;
                  background:{color};border-radius:3px;
                  transition:width 0.4s ease;"></div>
    </div>""", unsafe_allow_html=True)


# ── Crawl Log Terminal ────────────────────────────────────────────────────────

def log_terminal(lines: list[str]):
    html_lines = []
    for line in lines[-40:]:
        if "ERROR" in line or "error" in line:
            cls = "log-err"
        elif "WARN" in line or "warn" in line:
            cls = "log-warn"
        elif "✓" in line or "complete" in line.lower() or "done" in line.lower():
            cls = "log-ok"
        else:
            cls = "log-info"
        html_lines.append(f'<div class="{cls}">{line}</div>')

    body = "\n".join(html_lines) or '<div class="log-info">Waiting for crawl…</div>'
    st.markdown(f'<div class="log-terminal">{body}</div>',
                unsafe_allow_html=True)
