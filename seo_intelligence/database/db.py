"""
database/db.py
──────────────
Database access layer (DAL).
All DB interactions go through this module – modules never import models directly.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import (
    Base, get_engine, get_session_factory,
    CrawlSession, Page, InternalLink,
    MetaIssue, ContentCluster, LinkOpportunity, DuplicatePage,
)
from utils.logger import get_logger

log = get_logger(__name__)

# ─── Singleton session factory ────────────────────────────────────────────────
_SessionFactory = None


def init_db():
    """Create tables and initialise the session factory (call once at startup)."""
    global _SessionFactory
    engine = get_engine()
    Base.metadata.create_all(engine)
    _SessionFactory = get_session_factory()
    log.info("Database initialised at %s", engine.url)


@contextmanager
def get_db() -> Session:
    """Context manager that yields a DB session and auto-commits/rolls back."""
    if _SessionFactory is None:
        init_db()
    session: Session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception as exc:
        session.rollback()
        log.error("DB error: %s", exc)
        raise
    finally:
        session.close()


# ─── CrawlSession helpers ─────────────────────────────────────────────────────

def create_crawl_session(domain: str, language: str = "auto") -> int:
    with get_db() as db:
        cs = CrawlSession(domain=domain, language=language)
        db.add(cs)
        db.flush()
        return cs.id


def finish_crawl_session(session_id: int, total_pages: int, error: str = None):
    with get_db() as db:
        cs = db.query(CrawlSession).get(session_id)
        if cs:
            cs.finished_at = datetime.utcnow()
            cs.total_pages = total_pages
            cs.status = "failed" if error else "done"
            cs.error_msg = error


def list_crawl_sessions(domain: Optional[str] = None) -> List[dict]:
    with get_db() as db:
        q = db.query(CrawlSession)
        if domain:
            q = q.filter(CrawlSession.domain == domain)
        rows = q.order_by(CrawlSession.started_at.desc()).all()
        return [
            {
                "id":          r.id,
                "domain":      r.domain,
                "language":    r.language,
                "started_at":  r.started_at,
                "finished_at": r.finished_at,
                "total_pages": r.total_pages,
                "status":      r.status,
            }
            for r in rows
        ]


# ─── Page helpers ─────────────────────────────────────────────────────────────

def bulk_insert_pages(pages_data: List[dict]) -> List[int]:
    """Insert many pages at once; returns list of new IDs."""
    with get_db() as db:
        objs = [Page(**d) for d in pages_data]
        db.bulk_save_objects(objs, return_defaults=True)
        return [o.id for o in objs]


def get_pages_for_session(session_id: int) -> List[dict]:
    with get_db() as db:
        rows = db.query(Page).filter(Page.session_id == session_id).all()
        return [_page_to_dict(r) for r in rows]


def _page_to_dict(p: Page) -> dict:
    return {
        "id":               p.id,
        "url":              p.url,
        "title":            p.title,
        "meta_description": p.meta_description,
        "canonical":        p.canonical,
        "h1":               p.h1,
        "word_count":       p.word_count,
        "language":         p.language,
        "status_code":      p.status_code,
        "body_text":        p.body_text,
    }


# ─── InternalLink helpers ─────────────────────────────────────────────────────

def bulk_insert_links(links_data: List[dict]):
    with get_db() as db:
        db.bulk_insert_mappings(InternalLink, links_data)


def get_links_for_session(session_id: int) -> List[dict]:
    with get_db() as db:
        rows = db.query(InternalLink).filter(
            InternalLink.session_id == session_id
        ).all()
        return [
            {
                "source_page_id":   r.source_page_id,
                "target_url":       r.target_url,
                "anchor_text":      r.anchor_text,
                "anchor_relevance": r.anchor_relevance,
                "relevance_score":  r.relevance_score,
            }
            for r in rows
        ]


# ─── MetaIssue helpers ────────────────────────────────────────────────────────

def bulk_insert_meta_issues(issues: List[dict]):
    with get_db() as db:
        db.bulk_insert_mappings(MetaIssue, issues)


# ─── Cluster helpers ──────────────────────────────────────────────────────────

def save_clusters(clusters: List[dict]):
    with get_db() as db:
        db.bulk_insert_mappings(ContentCluster, clusters)


# ─── Opportunity helpers ──────────────────────────────────────────────────────

def save_opportunities(opportunities: List[dict]):
    with get_db() as db:
        db.bulk_insert_mappings(LinkOpportunity, opportunities)


# ─── Duplicate helpers ────────────────────────────────────────────────────────

def save_duplicates(duplicates: List[dict]):
    with get_db() as db:
        db.bulk_insert_mappings(DuplicatePage, duplicates)
