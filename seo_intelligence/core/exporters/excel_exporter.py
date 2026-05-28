"""
core/exporters/excel_exporter.py
──────────────────────────────────
Generates a professional, colour-coded Excel report.

Sheets
──────
1. Summary            – crawl stats at a glance
2. Pages              – all crawled pages with metadata
3. Meta Issues        – title/description problems
4. Anchor Analysis    – anchor text + relevance scores
5. Link Density       – internal link density per page
6. Link Opportunities – suggested new internal links
7. Content Clusters   – topic groups
8. Duplicates         – near-duplicate & duplicate pages
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import pandas as pd
import xlsxwriter

from config.settings import EXPORT_DIR
from utils.logger import get_logger

log = get_logger(__name__)

# ─── Color palette ────────────────────────────────────────────────────────────
COLORS = {
    "header_bg":     "#1A1A2E",
    "header_font":   "#FFFFFF",
    "alt_row":       "#F0F4FF",
    "error_bg":      "#FFDEDE",
    "warning_bg":    "#FFF3CD",
    "success_bg":    "#D4EDDA",
    "neutral_bg":    "#FFFFFF",
    "accent":        "#4A90D9",
    "sheet_tab_dark":"#1A1A2E",
}


class ExcelExporter:

    def __init__(
        self,
        domain: str,
        pages_df:        Optional[pd.DataFrame] = None,
        meta_df:         Optional[pd.DataFrame] = None,
        anchor_df:       Optional[pd.DataFrame] = None,
        density_df:      Optional[pd.DataFrame] = None,
        opportunity_df:  Optional[pd.DataFrame] = None,
        cluster_df:      Optional[pd.DataFrame] = None,
        duplicate_df:    Optional[pd.DataFrame] = None,
    ):
        self.domain         = domain
        self.pages_df       = pages_df
        self.meta_df        = meta_df
        self.anchor_df      = anchor_df
        self.density_df     = density_df
        self.opportunity_df = opportunity_df
        self.cluster_df     = cluster_df
        self.duplicate_df   = duplicate_df

    # ─── Public ───────────────────────────────────────────────────────────────

    def export(self) -> str:
        """Generate the Excel file and return its full path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"seo_report_{self.domain}_{timestamp}.xlsx"
        filepath  = os.path.join(EXPORT_DIR, filename)

        workbook  = xlsxwriter.Workbook(filepath, {"strings_to_urls": False})
        self._wb  = workbook
        self._define_formats()

        self._write_summary_sheet()
        self._write_df_sheet("Pages",             self.pages_df,
                              self._pages_columns())
        self._write_df_sheet("Meta Issues",        self.meta_df,
                              self._meta_columns(), conditional=True)
        self._write_df_sheet("Anchor Analysis",    self.anchor_df,
                              self._anchor_columns(), conditional=True)
        self._write_df_sheet("Link Density",       self.density_df,
                              self._density_columns(), conditional=True)
        self._write_df_sheet("Link Opportunities", self.opportunity_df,
                              self._opportunity_columns())
        self._write_df_sheet("Content Clusters",   self.cluster_df,
                              self._cluster_columns())
        self._write_df_sheet("Duplicates",         self.duplicate_df,
                              self._duplicate_columns(), conditional=True)

        workbook.close()
        log.info("Excel exported: %s", filepath)
        return filepath

    # ─── Format definitions ───────────────────────────────────────────────────

    def _define_formats(self):
        wb = self._wb
        self.fmt_header = wb.add_format({
            "bold": True, "font_color": COLORS["header_font"],
            "bg_color": COLORS["header_bg"],
            "border": 1, "align": "center", "valign": "vcenter",
            "text_wrap": True,
        })
        self.fmt_alt = wb.add_format({
            "bg_color": COLORS["alt_row"], "border": 1,
            "valign": "vcenter", "text_wrap": True,
        })
        self.fmt_normal = wb.add_format({
            "border": 1, "valign": "vcenter", "text_wrap": True,
        })
        self.fmt_error = wb.add_format({
            "bg_color": COLORS["error_bg"], "border": 1,
        })
        self.fmt_warning = wb.add_format({
            "bg_color": COLORS["warning_bg"], "border": 1,
        })
        self.fmt_success = wb.add_format({
            "bg_color": COLORS["success_bg"], "border": 1,
        })
        self.fmt_title = wb.add_format({
            "bold": True, "font_size": 16, "font_color": COLORS["header_bg"],
        })
        self.fmt_url = wb.add_format({
            "border": 1, "font_color": COLORS["accent"],
            "underline": True, "valign": "vcenter",
        })

    # ─── Summary sheet ────────────────────────────────────────────────────────

    def _write_summary_sheet(self):
        ws = self._wb.add_worksheet("Summary")
        ws.set_tab_color(COLORS["accent"])
        ws.set_column("A:A", 35)
        ws.set_column("B:B", 20)

        ws.write("A1", f"SEO Intelligence Report — {self.domain}", self.fmt_title)
        ws.write("A2", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        stats = [
            ("Total Pages Crawled",
             len(self.pages_df) if self.pages_df is not None else 0),
            ("Meta Issues",
             len(self.meta_df) if self.meta_df is not None else 0),
            ("Anchor Text Issues",
             (self.anchor_df["relevance"].isin(["Irrelevant","Generic"]).sum()
              if self.anchor_df is not None and "relevance" in self.anchor_df.columns else 0)),
            ("Link Opportunities",
             len(self.opportunity_df) if self.opportunity_df is not None else 0),
            ("Content Clusters",
             (self.cluster_df["cluster_id"].nunique()
              if self.cluster_df is not None and "cluster_id" in self.cluster_df.columns else 0)),
            ("Duplicate Page Pairs",
             len(self.duplicate_df) if self.duplicate_df is not None else 0),
        ]

        row = 4
        ws.write(row, 0, "Metric", self.fmt_header)
        ws.write(row, 1, "Value",  self.fmt_header)
        for i, (k, v) in enumerate(stats):
            fmt = self.fmt_alt if i % 2 else self.fmt_normal
            ws.write(row + 1 + i, 0, k, fmt)
            ws.write(row + 1 + i, 1, v, fmt)

    # ─── Generic DataFrame sheet writer ──────────────────────────────────────

    def _write_df_sheet(self, name: str, df: Optional[pd.DataFrame],
                        columns: list, conditional: bool = False):
        ws = self._wb.add_worksheet(name)
        ws.freeze_panes(1, 0)

        if df is None or df.empty:
            ws.write(0, 0, "No data available", self.fmt_normal)
            return

        # Filter & rename columns
        col_keys   = [c[0] for c in columns]
        col_labels = [c[1] for c in columns]
        col_widths = [c[2] for c in columns]

        avail = [c for c in col_keys if c in df.columns]
        df2   = df[avail].copy()

        for i, (key, label, width) in enumerate(columns):
            if key in df.columns:
                ws.set_column(i, i, width)
                ws.write(0, i, label, self.fmt_header)

        for row_idx, row in enumerate(df2.itertuples(index=False), start=1):
            base_fmt = self.fmt_alt if row_idx % 2 else self.fmt_normal
            for col_idx, key in enumerate(avail):
                val     = getattr(row, key, "")
                val_str = str(val) if val is not None else ""
                fmt     = self._conditional_fmt(key, val_str) if conditional else base_fmt
                ws.write(row_idx, col_idx, val_str, fmt)

    def _conditional_fmt(self, key: str, value: str):
        """Return a colour format based on the value's semantic meaning."""
        v = value.lower()
        # Severity-based
        if "error" in v:     return self.fmt_error
        if "warning" in v:   return self.fmt_warning
        # Relevance-based
        if v == "irrelevant" or v == "generic": return self.fmt_error
        if v == "partially relevant":           return self.fmt_warning
        if v == "relevant":                     return self.fmt_success
        # Status-based
        if v == "over_linked" or v == "under_linked": return self.fmt_warning
        if v == "optimal":                           return self.fmt_success
        return self.fmt_normal

    # ─── Column definitions ───────────────────────────────────────────────────

    def _pages_columns(self): return [
        ("url",              "URL",              50),
        ("title",            "Title",            40),
        ("meta_description", "Meta Description", 50),
        ("h1",               "H1",               40),
        ("word_count",       "Word Count",       12),
        ("language",         "Language",         10),
        ("status_code",      "Status Code",      12),
    ]

    def _meta_columns(self): return [
        ("_url",       "URL",        50),
        ("issue_type", "Issue",      30),
        ("value",      "Value",      50),
        ("severity",   "Severity",   12),
    ]

    def _anchor_columns(self): return [
        ("source_url",      "Source URL",      45),
        ("target_url",      "Target URL",      45),
        ("anchor_text",     "Anchor Text",     30),
        ("relevance",       "Relevance",       20),
        ("relevance_score", "Score",           10),
        ("is_generic",      "Generic?",        10),
    ]

    def _density_columns(self): return [
        ("url",                  "URL",              50),
        ("word_count",           "Words",            10),
        ("internal_link_count",  "Internal Links",   14),
        ("link_density_ratio",   "Density Ratio",    14),
        ("suggested_min_links",  "Min Suggested",    14),
        ("suggested_max_links",  "Max Suggested",    14),
        ("density_status",       "Status",           16),
    ]

    def _opportunity_columns(self): return [
        ("source_url",       "Source URL",       45),
        ("source_title",     "Source Title",     35),
        ("target_url",       "Target URL",       45),
        ("target_title",     "Target Title",     35),
        ("suggested_anchor", "Suggested Anchor", 30),
        ("similarity_score", "Similarity",       12),
    ]

    def _cluster_columns(self): return [
        ("url",          "URL",          50),
        ("title",        "Title",        40),
        ("cluster_id",   "Cluster ID",   12),
        ("cluster_name", "Cluster Name", 40),
    ]

    def _duplicate_columns(self): return [
        ("url_a",            "URL A",      45),
        ("url_b",            "URL B",      45),
        ("similarity_score", "Similarity", 12),
        ("duplicate_type",   "Type",       25),
    ]


# ─── Convenience function ─────────────────────────────────────────────────────

def export_to_excel(domain: str, **dataframes) -> str:
    """
    Wrapper for Streamlit / pipeline calls.

    dataframes keys must match ExcelExporter constructor kwargs:
      pages_df, meta_df, anchor_df, density_df,
      opportunity_df, cluster_df, duplicate_df
    """
    exporter = ExcelExporter(domain=domain, **dataframes)
    return exporter.export()
