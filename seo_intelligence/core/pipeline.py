"""
core/pipeline.py
─────────────────
High-level analysis pipeline.
Runs all analysis modules in sequence after crawling is complete.
Returns a AnalysisResult dataclass for easy downstream use.

Usage
─────
    from core.pipeline import AnalysisPipeline

    pipeline = AnalysisPipeline(
        base_url="https://example.com",
        language="auto",
        progress_cb=my_callback,
    )
    result = pipeline.run()
    excel_path = result.export_excel()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import pandas as pd

from core.crawler.crawler_engine         import CrawlerEngine
from core.analyzers.meta_analyzer        import run_meta_analysis
from core.analyzers.link_density_analyzer import run_link_density_analysis
from core.nlp.anchor_analyzer            import run_anchor_analysis
from core.nlp.content_clustering         import run_content_clustering
from core.nlp.duplicate_detector         import run_duplicate_detection
from core.nlp.link_opportunity_engine    import run_link_opportunity_analysis
from core.exporters.excel_exporter       import export_to_excel
from core.exporters.csv_exporter         import export_to_csv_zip
from database.db                         import get_pages_for_session
from utils.helpers                       import get_domain
from utils.logger                        import get_logger

log = get_logger(__name__)


@dataclass
class AnalysisResult:
    session_id:      int
    domain:          str
    pages_df:        pd.DataFrame = field(default_factory=pd.DataFrame)
    meta_df:         pd.DataFrame = field(default_factory=pd.DataFrame)
    anchor_df:       pd.DataFrame = field(default_factory=pd.DataFrame)
    density_df:      pd.DataFrame = field(default_factory=pd.DataFrame)
    opportunity_df:  pd.DataFrame = field(default_factory=pd.DataFrame)
    cluster_df:      pd.DataFrame = field(default_factory=pd.DataFrame)
    duplicate_df:    pd.DataFrame = field(default_factory=pd.DataFrame)

    def export_excel(self) -> str:
        return export_to_excel(
            domain=self.domain,
            pages_df=self.pages_df,
            meta_df=self.meta_df,
            anchor_df=self.anchor_df,
            density_df=self.density_df,
            opportunity_df=self.opportunity_df,
            cluster_df=self.cluster_df,
            duplicate_df=self.duplicate_df,
        )

    def export_csv_zip(self) -> str:
        return export_to_csv_zip(
            domain=self.domain,
            pages_df=self.pages_df,
            meta_df=self.meta_df,
            anchor_df=self.anchor_df,
            density_df=self.density_df,
            opportunity_df=self.opportunity_df,
            cluster_df=self.cluster_df,
            duplicate_df=self.duplicate_df,
        )


class AnalysisPipeline:
    """
    Orchestrates:
      1. Crawl
      2. Meta analysis
      3. Link density
      4. Anchor NLP analysis
      5. Content clustering
      6. Duplicate detection
      7. Link opportunity finder
    """

    def __init__(
        self,
        base_url:     str,
        language:     str = "auto",
        max_pages:    Optional[int] = None,
        progress_cb:  Optional[Callable[[str, int, int], None]] = None,
    ):
        self.base_url    = base_url
        self.language    = language
        self.max_pages   = max_pages
        self.domain      = get_domain(base_url)
        # progress_cb(step_name, current, total)
        self._progress   = progress_cb or (lambda s, c, t: None)

    def run(self) -> AnalysisResult:
        log.info("=" * 60)
        log.info("Pipeline START: %s", self.base_url)
        log.info("=" * 60)

        # ── Step 1: Crawl ─────────────────────────────────────────────────────
        self._progress("Crawling", 0, 100)
        crawler = CrawlerEngine(
            base_url=self.base_url,
            language_filter=self.language,
            max_pages=self.max_pages,
            progress_cb=lambda c, t: self._progress("Crawling", c, t),
        )
        session_id = crawler.run()
        self._progress("Crawling", 100, 100)
        log.info("Crawl complete (session %d)", session_id)

        # ── Step 2: Load pages as DataFrame ──────────────────────────────────
        pages_data = get_pages_for_session(session_id)
        pages_df   = pd.DataFrame(pages_data)

        # ── Step 3: Meta analysis ─────────────────────────────────────────────
        self._progress("Meta Analysis", 0, 100)
        meta_df = run_meta_analysis(session_id)
        self._progress("Meta Analysis", 100, 100)

        # ── Step 4: Link density ──────────────────────────────────────────────
        self._progress("Link Density", 0, 100)
        density_df = run_link_density_analysis(session_id)
        self._progress("Link Density", 100, 100)

        # ── Step 5: Anchor analysis (NLP) ─────────────────────────────────────
        self._progress("Anchor NLP", 0, 100)
        anchor_df = run_anchor_analysis(session_id)
        self._progress("Anchor NLP", 100, 100)

        # ── Step 6: Content clustering ────────────────────────────────────────
        self._progress("Clustering", 0, 100)
        cluster_df = run_content_clustering(session_id)
        self._progress("Clustering", 100, 100)

        # ── Step 7: Duplicate detection ───────────────────────────────────────
        self._progress("Duplicates", 0, 100)
        duplicate_df = run_duplicate_detection(session_id)
        self._progress("Duplicates", 100, 100)

        # ── Step 8: Link opportunities ────────────────────────────────────────
        self._progress("Opportunities", 0, 100)
        opportunity_df = run_link_opportunity_analysis(session_id)
        self._progress("Opportunities", 100, 100)

        log.info("Pipeline DONE for session %d", session_id)

        return AnalysisResult(
            session_id=session_id,
            domain=self.domain,
            pages_df=pages_df,
            meta_df=meta_df,
            anchor_df=anchor_df,
            density_df=density_df,
            opportunity_df=opportunity_df,
            cluster_df=cluster_df,
            duplicate_df=duplicate_df,
        )
