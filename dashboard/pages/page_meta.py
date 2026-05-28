"""
dashboard/pages/page_meta.py
─────────────────────────────
Meta Analyzer — Title & Description issues with filters and export.
"""

import streamlit as st
import pandas as pd

from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    kpi_card, styled_dataframe, empty_state, tip_box,
)


ISSUE_LABELS = {
    "missing_title":           "Missing Title",
    "missing_description":     "Missing Description",
    "title_too_short":         "Title Too Short",
    "title_too_long":          "Title Too Long",
    "description_too_short":   "Description Too Short",
    "description_too_long":    "Description Too Long",
    "duplicate_title":         "Duplicate Title",
    "duplicate_description":   "Duplicate Description",
}

SEVERITY_COLOR = {
    "error":   "#F87171",
    "warning": "#FBBF24",
    "info":    "#94A3B8",
}


def render():
    page_header("◎", "Meta Analyzer",
                "Audit all Title and Description tags across your website")

    result = st.session_state.get("last_result")

    if result is None or result.meta_df.empty:
        empty_state("Run a crawl first to see meta tag analysis.", "◎")
        tip_box("Go to Crawl Management and start a new analysis.")
        return

    df = result.meta_df.copy()

    # ── KPI Row ───────────────────────────────────────────────────────────────
    errors   = len(df[df["severity"] == "error"])
    warnings = len(df[df["severity"] == "warning"])
    missing  = len(df[df["issue_type"].isin(["missing_title","missing_description"])])
    dups     = len(df[df["issue_type"].isin(["duplicate_title","duplicate_description"])])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("⚠",  "Total Issues",   len(df),     badge="All")
    with c2:
        kpi_card("🔴", "Errors",          errors,      badge_type="down", badge="Error")
    with c3:
        kpi_card("🟡", "Warnings",        warnings,    badge_type="info", badge="Warn")
    with c4:
        kpi_card("⧖",  "Duplicates",      dups,        badge_type="down" if dups else "up",
                 badge="High" if dups > 10 else "Low")

    gold_divider()

    # ── Issue breakdown chart (native Streamlit bar) ──────────────────────────
    section_header("◎", "Issue Breakdown")
    breakdown = df["issue_type"].value_counts().reset_index()
    breakdown.columns = ["Issue Type", "Count"]
    breakdown["Issue Type"] = breakdown["Issue Type"].map(
        lambda x: ISSUE_LABELS.get(x, x)
    )
    st.bar_chart(breakdown.set_index("Issue Type"), color="#C9A84C", height=220)

    gold_divider()

    # ── Filters ───────────────────────────────────────────────────────────────
    section_header("⊹", "Filter Issues")

    f1, f2, f3 = st.columns(3)
    with f1:
        sev_filter = st.multiselect(
            "Severity",
            ["error", "warning"],
            default=["error", "warning"],
        )
    with f2:
        type_filter = st.multiselect(
            "Issue Type",
            list(ISSUE_LABELS.values()),
            default=list(ISSUE_LABELS.values()),
        )
    with f3:
        search_url = st.text_input("Search URL", placeholder="Filter by URL…")

    # Apply filters
    filtered = df.copy()
    if sev_filter:
        filtered = filtered[filtered["severity"].isin(sev_filter)]

    type_reverse = {v: k for k, v in ISSUE_LABELS.items()}
    selected_types = [type_reverse.get(t, t) for t in type_filter]
    if selected_types:
        filtered = filtered[filtered["issue_type"].isin(selected_types)]

    if search_url:
        filtered = filtered[filtered.get("_url", filtered.get("url", "")).str.contains(
            search_url, case=False, na=False
        )]

    gold_divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    section_header("≡", f"Issues Table — {len(filtered):,} results")

    # Render with color-coded severity column
    display_df = filtered.copy()

    # Map columns for display
    col_map = {"_url": "URL", "issue_type": "Issue", "value": "Value", "severity": "Severity"}
    display_df = display_df.rename(columns=col_map)

    # Replace issue_type codes with labels
    if "Issue" in display_df.columns:
        display_df["Issue"] = display_df["Issue"].map(lambda x: ISSUE_LABELS.get(x, x))

    show_cols = [c for c in ["URL", "Issue", "Value", "Severity"] if c in display_df.columns]
    styled_dataframe(display_df[show_cols], height=420)

    gold_divider()

    # ── Export ────────────────────────────────────────────────────────────────
    section_header("↓", "Export")
    e1, e2 = st.columns(2)
    with e1:
        csv = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 Download CSV", csv, "meta_issues.csv",
                           "text/csv", use_container_width=True)
    with e2:
        tip_box(f"{len(filtered):,} issues ready to export. Full Excel available in Reports Center.")
