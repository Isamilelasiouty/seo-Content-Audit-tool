"""
database/models.py
──────────────────
SQLAlchemy ORM models.
SQLite by default → switch to PostgreSQL by changing DATABASE["url"] in settings.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON, Index, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config.settings import DATABASE

Base = declarative_base()


# ─── Session ──────────────────────────────────────────────────────────────────

def get_engine():
    return create_engine(
        DATABASE["url"],
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE["url"] else {},
        pool_pre_ping=True,
    )


def get_session_factory():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


# ─── CrawlSession ─────────────────────────────────────────────────────────────

class CrawlSession(Base):
    """One crawl run for a given domain."""
    __tablename__ = "crawl_sessions"

    id          = Column(Integer, primary_key=True, index=True)
    domain      = Column(String(255), nullable=False, index=True)
    language    = Column(String(10), default="auto")
    started_at  = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    total_pages = Column(Integer, default=0)
    status      = Column(String(50), default="running")   # running|done|failed
    error_msg   = Column(Text, nullable=True)

    pages       = relationship("Page", back_populates="session",
                               cascade="all, delete-orphan")


# ─── Page ─────────────────────────────────────────────────────────────────────

class Page(Base):
    """One crawled page with all extracted metadata."""
    __tablename__ = "pages"

    id               = Column(Integer, primary_key=True, index=True)
    session_id       = Column(Integer, ForeignKey("crawl_sessions.id"), nullable=False)
    url              = Column(Text, nullable=False)
    status_code      = Column(Integer, nullable=True)
    title            = Column(Text, nullable=True)
    meta_description = Column(Text, nullable=True)
    canonical        = Column(Text, nullable=True)
    h1               = Column(Text, nullable=True)
    word_count       = Column(Integer, default=0)
    language         = Column(String(10), nullable=True)
    body_text        = Column(Text, nullable=True)   # raw page text for NLP
    crawled_at       = Column(DateTime, default=datetime.utcnow)

    session          = relationship("CrawlSession", back_populates="pages")
    internal_links   = relationship("InternalLink", back_populates="source_page",
                                    foreign_keys="InternalLink.source_page_id",
                                    cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_pages_session_url", "session_id", "url"),
    )


# ─── InternalLink ─────────────────────────────────────────────────────────────

class InternalLink(Base):
    """An internal link found on a page, with anchor text and relevance score."""
    __tablename__ = "internal_links"

    id               = Column(Integer, primary_key=True, index=True)
    session_id       = Column(Integer, ForeignKey("crawl_sessions.id"), nullable=False)
    source_page_id   = Column(Integer, ForeignKey("pages.id"), nullable=False)
    target_url       = Column(Text, nullable=False)
    anchor_text      = Column(Text, nullable=True)
    anchor_relevance = Column(String(30), nullable=True)  # Relevant / Partial / Irrelevant
    relevance_score  = Column(Float, nullable=True)
    link_position    = Column(Integer, nullable=True)     # position in content

    source_page      = relationship("Page", back_populates="internal_links",
                                    foreign_keys=[source_page_id])


# ─── MetaIssue ────────────────────────────────────────────────────────────────

class MetaIssue(Base):
    """Meta tag problem detected for a page."""
    __tablename__ = "meta_issues"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("crawl_sessions.id"), nullable=False)
    page_id    = Column(Integer, ForeignKey("pages.id"), nullable=False)
    issue_type = Column(String(100), nullable=False)   # e.g. "title_too_short"
    value      = Column(Text, nullable=True)
    severity   = Column(String(20), default="warning") # error|warning|info


# ─── ContentCluster ───────────────────────────────────────────────────────────

class ContentCluster(Base):
    """A group of semantically similar pages."""
    __tablename__ = "content_clusters"

    id           = Column(Integer, primary_key=True, index=True)
    session_id   = Column(Integer, ForeignKey("crawl_sessions.id"), nullable=False)
    cluster_name = Column(String(255), nullable=True)
    page_ids     = Column(JSON, default=list)   # list of page IDs
    centroid_url = Column(Text, nullable=True)  # representative page


# ─── LinkOpportunity ──────────────────────────────────────────────────────────

class LinkOpportunity(Base):
    """A suggested internal link that doesn't yet exist."""
    __tablename__ = "link_opportunities"

    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey("crawl_sessions.id"), nullable=False)
    source_page_id  = Column(Integer, ForeignKey("pages.id"), nullable=False)
    target_url      = Column(Text, nullable=False)
    suggested_anchor= Column(Text, nullable=True)
    similarity_score= Column(Float, nullable=True)


# ─── DuplicatePage ────────────────────────────────────────────────────────────

class DuplicatePage(Base):
    """A pair of pages with near-duplicate or duplicate content."""
    __tablename__ = "duplicate_pages"

    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey("crawl_sessions.id"), nullable=False)
    page_a_id       = Column(Integer, ForeignKey("pages.id"), nullable=False)
    page_b_id       = Column(Integer, ForeignKey("pages.id"), nullable=False)
    similarity_score= Column(Float, nullable=True)
    duplicate_type  = Column(String(50), default="near_duplicate")  # exact|near_duplicate|title_only
