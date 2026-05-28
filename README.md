# 🔍 SEO Intelligence Tool

> Professional, scalable SEO analysis platform for large Arabic and English websites.  
> Built with Python · Streamlit · Sentence Transformers · SQLite/PostgreSQL

---

## ✨ Features

| Module | What it does |
|---|---|
| **Website Crawler** | Async crawl via sitemap.xml / sitemap_index.xml; fallback BFS crawl; Arabic + English |
| **Meta Analyzer** | Detects missing, short, long, and duplicate title/description tags |
| **Anchor Text Analyzer** | NLP-based relevance scoring for every internal link anchor |
| **Link Density Analyzer** | Checks internal link count vs word count per page |
| **Content Clustering** | Groups pages by semantic similarity using multilingual embeddings |
| **Link Opportunity Engine** | Suggests new internal links between related pages |
| **Duplicate Detector** | Finds exact and near-duplicate pages (TF-IDF + embeddings) |
| **Excel / CSV Export** | Professional multi-sheet report with colour coding |

---

## 🗂️ Project Structure

```
seo_intelligence/
├── app.py                        # Streamlit entry point
├── requirements.txt
├── config/
│   └── settings.py               # All tuneable parameters
├── core/
│   ├── pipeline.py               # Orchestrates all modules
│   ├── crawler/
│   │   ├── sitemap_parser.py     # Sitemap + robots.txt discovery
│   │   ├── page_fetcher.py       # Async HTTP fetcher
│   │   └── crawler_engine.py     # Full crawl orchestrator
│   ├── analyzers/
│   │   ├── meta_analyzer.py      # Meta tag analysis
│   │   └── link_density_analyzer.py
│   ├── nlp/
│   │   ├── embeddings.py         # Sentence-transformer wrapper
│   │   ├── anchor_analyzer.py    # Anchor relevance scoring
│   │   ├── content_clustering.py # Semantic topic clustering
│   │   ├── duplicate_detector.py # Near-duplicate detection
│   │   └── link_opportunity_engine.py
│   └── exporters/
│       ├── excel_exporter.py     # Multi-sheet Excel export
│       └── csv_exporter.py       # CSV zip export
├── database/
│   ├── models.py                 # SQLAlchemy ORM models
│   └── db.py                     # Data access layer
├── utils/
│   ├── helpers.py                # URL, text, HTTP utilities
│   └── logger.py                 # Rotating file + console logger
├── tests/
│   └── test_helpers.py
└── logs/                         # Auto-created at runtime
```

---

## 🚀 Quick Start

### Local

```bash
git clone https://github.com/your-username/seo-intelligence-tool.git
cd seo-intelligence-tool

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

### Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) → **New app**.
3. Select the repo, set **Main file path** to `app.py`.
4. Deploy.

---

## ⚙️ Configuration

All settings are in `config/settings.py`:

```python
CRAWLER = {
    "max_concurrent_requests": 10,
    "request_timeout":          20,
    "max_pages":             50_000,
    ...
}

NLP = {
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
    "similarity_threshold_cluster":   0.75,
    "similarity_threshold_duplicate": 0.92,
    ...
}
```

To switch to **PostgreSQL**, change in `config/settings.py`:
```python
DATABASE = {
    "url": "postgresql+psycopg2://user:password@host:5432/dbname"
}
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## 📦 Key Dependencies

- `sentence-transformers` — multilingual embeddings (Arabic + English)
- `scikit-learn` — TF-IDF, clustering
- `aiohttp` — async page fetching
- `xlsxwriter` — professional Excel reports
- `SQLAlchemy` — ORM (SQLite → PostgreSQL ready)
- `streamlit` — web UI

---

## 🗺️ Roadmap

- [x] Core crawl engine
- [x] Meta tag analysis
- [x] Anchor NLP scoring
- [x] Content clustering
- [x] Link opportunity engine
- [x] Duplicate detection
- [x] Excel / CSV export
- [ ] Full Dashboard UI (next phase)
- [ ] Team authentication
- [ ] Email login
- [ ] API integrations (GSC, Ahrefs)
- [ ] Scheduled crawls

---

## 📄 License

MIT
