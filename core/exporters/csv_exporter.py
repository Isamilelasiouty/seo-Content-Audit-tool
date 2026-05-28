"""
core/exporters/csv_exporter.py
────────────────────────────────
Exports each analysis result as a separate CSV file inside a zip archive.
"""

from __future__ import annotations

import io
import os
import zipfile
from datetime import datetime
from typing import Optional

import pandas as pd

from config.settings import EXPORT_DIR
from utils.logger import get_logger

log = get_logger(__name__)


def export_to_csv_zip(
    domain: str,
    pages_df:       Optional[pd.DataFrame] = None,
    meta_df:        Optional[pd.DataFrame] = None,
    anchor_df:      Optional[pd.DataFrame] = None,
    density_df:     Optional[pd.DataFrame] = None,
    opportunity_df: Optional[pd.DataFrame] = None,
    cluster_df:     Optional[pd.DataFrame] = None,
    duplicate_df:   Optional[pd.DataFrame] = None,
) -> str:
    """
    Create a ZIP archive containing one CSV per analysis module.
    Returns the path to the ZIP file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name  = f"seo_report_{domain}_{timestamp}.zip"
    zip_path  = os.path.join(EXPORT_DIR, zip_name)

    sheets = {
        "pages.csv":        pages_df,
        "meta_issues.csv":  meta_df,
        "anchors.csv":      anchor_df,
        "link_density.csv": density_df,
        "opportunities.csv":opportunity_df,
        "clusters.csv":     cluster_df,
        "duplicates.csv":   duplicate_df,
    }

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, df in sheets.items():
            if df is not None and not df.empty:
                buf = io.StringIO()
                df.to_csv(buf, index=False, encoding="utf-8-sig")
                zf.writestr(fname, buf.getvalue())

    log.info("CSV zip exported: %s", zip_path)
    return zip_path
