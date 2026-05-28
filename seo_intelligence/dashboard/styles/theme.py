"""
dashboard/styles/theme.py
──────────────────────────
Complete CSS theme injection for the SEO Intelligence Platform.
Gold · Black · White — Premium SaaS aesthetic.
"""

GLOBAL_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=DM+Sans:wght@300;400;500;600&family=Cairo:wght@300;400;500;600;700&display=swap');

/* ── CSS Variables ────────────────────────────────────────────────────── */
:root {
  --gold:          #C9A84C;
  --gold-light:    #E8C96A;
  --gold-bright:   #FFD700;
  --gold-dim:      #8B6914;
  --gold-glow:     rgba(201, 168, 76, 0.25);
  --gold-border:   rgba(201, 168, 76, 0.35);
  --black:         #0A0A0A;
  --black-2:       #111111;
  --black-3:       #181818;
  --black-4:       #222222;
  --black-5:       #2A2A2A;
  --white:         #FFFFFF;
  --white-dim:     rgba(255,255,255,0.85);
  --white-muted:   rgba(255,255,255,0.55);
  --white-faint:   rgba(255,255,255,0.12);
  --radius-sm:     8px;
  --radius-md:     14px;
  --radius-lg:     20px;
  --shadow-gold:   0 4px 30px rgba(201,168,76,0.18);
  --shadow-dark:   0 8px 40px rgba(0,0,0,0.6);
  --transition:    all 0.25s cubic-bezier(0.4,0,0.2,1);
}

/* ── App Background ───────────────────────────────────────────────────── */
.stApp {
  background: var(--black) !important;
  font-family: 'DM Sans', 'Cairo', sans-serif !important;
  color: var(--white-dim) !important;
}

/* ── Hide Streamlit chrome ────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--black-2) !important;
  border-right: 1px solid var(--gold-border) !important;
  box-shadow: 4px 0 30px rgba(0,0,0,0.5) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding-top: 0 !important;
}

/* ── Main content padding ─────────────────────────────────────────────── */
.block-container {
  padding: 2rem 2.5rem 2rem 2.5rem !important;
  max-width: 1400px !important;
}

/* ── Scrollbar ────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--black-3); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ── KPI Cards ────────────────────────────────────────────────────────── */
.kpi-card {
  background: var(--black-3);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-md);
  padding: 1.4rem 1.6rem;
  position: relative;
  overflow: hidden;
  transition: var(--transition);
  box-shadow: var(--shadow-dark);
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.kpi-card:hover {
  border-color: var(--gold);
  box-shadow: var(--shadow-gold), var(--shadow-dark);
  transform: translateY(-2px);
}
.kpi-icon {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  display: block;
}
.kpi-label {
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--white-muted);
  margin-bottom: 0.3rem;
}
.kpi-value {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--gold-light);
  line-height: 1;
}
.kpi-sub {
  font-size: 0.75rem;
  color: var(--white-muted);
  margin-top: 0.4rem;
}
.kpi-badge {
  position: absolute;
  top: 1rem; right: 1rem;
  font-size: 0.65rem;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.badge-up   { background: rgba(52,211,153,0.15); color: #34D399; }
.badge-down { background: rgba(239,68,68,0.15);  color: #EF4444; }
.badge-info { background: var(--gold-glow);       color: var(--gold); }

/* ── Section Headers ──────────────────────────────────────────────────── */
.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--gold-border);
}
.section-header h2 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--white);
  margin: 0;
}
.section-icon {
  width: 36px; height: 36px;
  background: var(--gold-glow);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
}

/* ── Content Cards ────────────────────────────────────────────────────── */
.content-card {
  background: var(--black-3);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  margin-bottom: 1.25rem;
  box-shadow: var(--shadow-dark);
  transition: var(--transition);
}
.content-card:hover {
  border-color: var(--gold-border);
}

/* ── Status Badges ────────────────────────────────────────────────────── */
.status-relevant        { color: #34D399; background: rgba(52,211,153,0.12); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.status-partial         { color: #FBBF24; background: rgba(251,191,36,0.12); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.status-irrelevant      { color: #F87171; background: rgba(248,113,113,0.12); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.status-generic         { color: #94A3B8; background: rgba(148,163,184,0.12); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.status-optimal         { color: #34D399; background: rgba(52,211,153,0.12); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.status-over_linked     { color: #F87171; background: rgba(248,113,113,0.12); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.status-under_linked    { color: #FBBF24; background: rgba(251,191,36,0.12); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }

/* ── Streamlit Buttons ────────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, var(--gold-dim), var(--gold)) !important;
  color: var(--black) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  letter-spacing: 0.05em !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  padding: 0.55rem 1.4rem !important;
  transition: var(--transition) !important;
  box-shadow: 0 2px 15px rgba(201,168,76,0.3) !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, var(--gold), var(--gold-light)) !important;
  box-shadow: 0 4px 25px rgba(201,168,76,0.5) !important;
  transform: translateY(-1px) !important;
}

/* ── Streamlit Inputs ─────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
  background: var(--black-4) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--white) !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 2px var(--gold-glow) !important;
}

/* ── Streamlit Metrics ────────────────────────────────────────────────── */
[data-testid="metric-container"] {
  background: var(--black-3) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: var(--radius-md) !important;
  padding: 1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
  color: var(--white-muted) !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 2rem !important;
  color: var(--gold-light) !important;
}

/* ── DataFrames / Tables ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--gold-border) !important;
  border-radius: var(--radius-md) !important;
  overflow: hidden !important;
}
.stDataFrame thead tr th {
  background: var(--black-4) !important;
  color: var(--gold) !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid var(--gold-border) !important;
}
.stDataFrame tbody tr:hover { background: var(--white-faint) !important; }

/* ── Progress Bar ─────────────────────────────────────────────────────── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--gold-dim), var(--gold-bright)) !important;
  border-radius: 4px !important;
}
.stProgress > div > div {
  background: var(--black-4) !important;
  border-radius: 4px !important;
}

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--black-3) !important;
  border: 1px solid rgba(255,255,255,0.07) !important;
  border-radius: var(--radius-md) !important;
}
[data-testid="stExpander"]:hover {
  border-color: var(--gold-border) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--black-3) !important;
  border-radius: var(--radius-md) !important;
  padding: 4px !important;
  gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--white-muted) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  transition: var(--transition) !important;
}
.stTabs [aria-selected="true"] {
  background: var(--gold-glow) !important;
  color: var(--gold) !important;
  border: 1px solid var(--gold-border) !important;
}

/* ── Divider ──────────────────────────────────────────────────────────── */
hr {
  border-color: var(--gold-border) !important;
  margin: 1.5rem 0 !important;
}

/* ── Sidebar Nav Item ─────────────────────────────────────────────────── */
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--white-muted);
  margin-bottom: 2px;
  border: 1px solid transparent;
}
.nav-item:hover {
  background: var(--white-faint);
  color: var(--white);
}
.nav-item.active {
  background: var(--gold-glow);
  color: var(--gold);
  border-color: var(--gold-border);
}
.nav-item .nav-icon { font-size: 1rem; width: 20px; text-align: center; }

/* ── Sidebar section label ────────────────────────────────────────────── */
.nav-section {
  font-size: 0.62rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--white-muted);
  padding: 1rem 1rem 0.4rem 1rem;
  font-weight: 600;
}

/* ── Gold Divider ─────────────────────────────────────────────────────── */
.gold-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-border), transparent);
  margin: 0.75rem 0;
}

/* ── Page Title ───────────────────────────────────────────────────────── */
.page-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--white);
  margin: 0 0 0.25rem 0;
  line-height: 1.2;
}
.page-subtitle {
  font-size: 0.82rem;
  color: var(--white-muted);
  margin-bottom: 1.75rem;
}
.gold-accent { color: var(--gold); }

/* ── Alert/Info boxes ─────────────────────────────────────────────────── */
.stAlert {
  background: var(--black-4) !important;
  border-radius: var(--radius-sm) !important;
  border-left: 3px solid var(--gold) !important;
}

/* ── Sidebar radio buttons (hidden, replaced by custom nav) ───────────── */
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Tooltip-like small text ──────────────────────────────────────────── */
.tip {
  font-size: 0.72rem;
  color: var(--white-muted);
  background: var(--black-4);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-sm);
  padding: 0.5rem 0.75rem;
  margin-top: 0.5rem;
}

/* ── Health Score Ring ────────────────────────────────────────────────── */
.health-ring {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}
.health-ring svg { filter: drop-shadow(0 0 12px rgba(201,168,76,0.4)); }

/* ── Opportunity Card ─────────────────────────────────────────────────── */
.opp-card {
  background: var(--black-4);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: var(--radius-sm);
  padding: 0.9rem 1.1rem;
  margin-bottom: 0.6rem;
  transition: var(--transition);
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}
.opp-card:hover { border-color: var(--gold-border); background: var(--black-5); }
.opp-arrow {
  color: var(--gold);
  font-size: 1.1rem;
  margin-top: 2px;
  flex-shrink: 0;
}
.opp-source { font-size: 0.78rem; color: var(--white-muted); }
.opp-target { font-size: 0.85rem; color: var(--white); font-weight: 500; }
.opp-anchor { font-size: 0.75rem; color: var(--gold); font-style: italic; }
.opp-score  { font-size: 0.7rem; color: var(--white-muted); margin-top: 2px; }

/* ── Cluster pill ─────────────────────────────────────────────────────── */
.cluster-pill {
  display: inline-block;
  background: var(--gold-glow);
  border: 1px solid var(--gold-border);
  color: var(--gold);
  border-radius: 20px;
  padding: 2px 10px;
  font-size: 0.72rem;
  font-weight: 600;
}

/* ── Contact card ─────────────────────────────────────────────────────── */
.contact-card {
  background: linear-gradient(135deg, var(--black-3), var(--black-4));
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-lg);
  padding: 2.5rem;
  text-align: center;
  box-shadow: var(--shadow-gold), var(--shadow-dark);
  position: relative;
  overflow: hidden;
}
.contact-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--gold-dim), var(--gold-bright), var(--gold-dim));
}
.contact-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--white);
  margin: 0.75rem 0 0.25rem 0;
}
.contact-role {
  font-size: 0.82rem;
  color: var(--white-muted);
  line-height: 1.5;
  max-width: 380px;
  margin: 0 auto 1.5rem auto;
}
.contact-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  transition: var(--transition);
  margin: 0.3rem;
  cursor: pointer;
  border: none;
}
.contact-btn-wa {
  background: rgba(37,211,102,0.15);
  color: #25D366;
  border: 1px solid rgba(37,211,102,0.3);
}
.contact-btn-wa:hover { background: rgba(37,211,102,0.25); }
.contact-btn-li {
  background: rgba(10,102,194,0.15);
  color: #0A66C2;
  border: 1px solid rgba(10,102,194,0.3);
}
.contact-btn-li:hover { background: rgba(10,102,194,0.25); }

/* ── Sidebar logo area ────────────────────────────────────────────────── */
.sidebar-logo-wrap {
  padding: 1.5rem 1rem 0.75rem 1rem;
  border-bottom: 1px solid var(--gold-border);
  margin-bottom: 0.5rem;
  text-align: center;
}
.sidebar-brand {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--gold);
  letter-spacing: 0.05em;
  margin-top: 0.4rem;
}
.sidebar-version {
  font-size: 0.62rem;
  color: var(--white-muted);
  letter-spacing: 0.1em;
}

/* ── System status dot ────────────────────────────────────────────────── */
.status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 5px;
}
.dot-green  { background: #34D399; box-shadow: 0 0 6px #34D399; }
.dot-yellow { background: #FBBF24; box-shadow: 0 0 6px #FBBF24; }
.dot-red    { background: #F87171; box-shadow: 0 0 6px #F87171; }

/* ── Selectbox label ──────────────────────────────────────────────────── */
.stSelectbox label, .stTextInput label, .stNumberInput label,
.stSlider label, .stCheckbox label {
  color: var(--white-muted) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.05em !important;
}

/* ── Download button ──────────────────────────────────────────────────── */
.stDownloadButton > button {
  background: transparent !important;
  border: 1px solid var(--gold-border) !important;
  color: var(--gold) !important;
  font-weight: 600 !important;
}
.stDownloadButton > button:hover {
  background: var(--gold-glow) !important;
  border-color: var(--gold) !important;
}

/* ── RTL support ──────────────────────────────────────────────────────── */
.rtl { direction: rtl; text-align: right; }
.ltr { direction: ltr; text-align: left; }

/* ── Log terminal ─────────────────────────────────────────────────────── */
.log-terminal {
  background: var(--black);
  border: 1px solid var(--gold-border);
  border-radius: var(--radius-sm);
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: #A0AEC0;
  max-height: 220px;
  overflow-y: auto;
  line-height: 1.6;
}
.log-terminal .log-ok   { color: #34D399; }
.log-terminal .log-warn { color: #FBBF24; }
.log-terminal .log-err  { color: #F87171; }
.log-terminal .log-info { color: var(--gold); }
</style>
"""


def inject_css():
    """Call this at the top of every page."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
