"""
dashboard/pages/page_team.py
──────────────────────────────
Team Management — placeholders for auth, roles, email login.
Architecture is ready; auth will be wired in a future phase.
"""

import streamlit as st
from dashboard.components.ui import (
    page_header, section_header, gold_divider,
    empty_state, tip_box,
)
from database.db import list_crawl_sessions


def render():
    page_header("⊞", "Team Activity",
                "Monitor your team's crawls, analyses and usage history")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_activity, tab_members, tab_auth = st.tabs([
        "◈  Activity Log",
        "⊞  Team Members",
        "🔑  Authentication",
    ])

    # ── Activity Log ──────────────────────────────────────────────────────────
    with tab_activity:
        section_header("◈", "Crawl History")
        sessions = []
        try:
            sessions = list_crawl_sessions()
        except Exception:
            pass

        if not sessions:
            empty_state("No crawl activity recorded yet.", "⟳")
        else:
            import pandas as pd
            df = pd.DataFrame(sessions)
            if "started_at" in df.columns:
                df["started_at"] = pd.to_datetime(df["started_at"]).dt.strftime("%Y-%m-%d %H:%M")
            if "finished_at" in df.columns:
                df["finished_at"] = pd.to_datetime(df["finished_at"]).dt.strftime("%Y-%m-%d %H:%M")

            # Status badge coloring via column config
            st.dataframe(df, use_container_width=True, height=400, hide_index=True)

            gold_divider()
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 Export Activity Log", csv, "crawl_history.csv",
                               "text/csv", use_container_width=True)

    # ── Team Members ──────────────────────────────────────────────────────────
    with tab_members:
        section_header("⊞", "Team Members")
        st.markdown("""
        <div class="content-card" style="text-align:center;padding:2.5rem;">
          <div style="font-size:2.5rem;margin-bottom:0.75rem;">⊞</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;
                      color:var(--white);margin-bottom:0.5rem;">
            Team Management
          </div>
          <div style="font-size:0.82rem;color:var(--white-muted);
                      max-width:400px;margin:0 auto 1.5rem;">
            Invite team members, assign roles (Admin / Analyst / Viewer),
            and manage access permissions.
          </div>
          <div style="display:inline-block;background:var(--gold-glow);
                      border:1px solid var(--gold-border);border-radius:20px;
                      padding:0.4rem 1.2rem;font-size:0.78rem;
                      color:var(--gold);font-weight:600;">
            🔒 Coming in Next Phase
          </div>
        </div>""", unsafe_allow_html=True)

        gold_divider()

        # Preview of what the table will look like
        st.caption("Preview — team member table (populated after auth is enabled):")
        import pandas as pd
        preview = pd.DataFrame([
            {"Name":"Ismail El Asiouty","Email":"ismail@example.com","Role":"Admin",  "Status":"Active","Last Active":"Today"},
            {"Name":"Team Member",       "Email":"team@example.com",  "Role":"Analyst","Status":"Invited","Last Active":"—"},
        ])
        st.dataframe(preview, use_container_width=True, hide_index=True)

    # ── Auth Setup ────────────────────────────────────────────────────────────
    with tab_auth:
        section_header("🔑", "Authentication Setup")
        st.markdown("""
        <div class="content-card">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;
                      color:var(--white);margin-bottom:1rem;">
            Authentication Architecture Ready
          </div>
          <div style="font-size:0.82rem;color:var(--white-muted);line-height:1.7;">
            The platform is architected to support:
          </div>
        </div>""", unsafe_allow_html=True)

        features = [
            ("📧", "Email / Password Login",        "Ready to wire"),
            ("🔑", "API Key Generation",             "Ready to wire"),
            ("⊞", "Role-Based Permissions",          "Admin / Analyst / Viewer"),
            ("🔒", "Session Management",              "JWT-based"),
            ("📊", "Per-user Analysis History",       "DB schema ready"),
            ("🔗", "API Integration (GSC, Ahrefs)",  "Future phase"),
        ]

        for icon, feature, note in features:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.65rem 0.9rem;border-bottom:1px solid rgba(255,255,255,0.04);
                        font-size:0.82rem;">
              <div>
                <span style="margin-right:0.6rem;">{icon}</span>
                <span style="color:var(--white);">{feature}</span>
              </div>
              <span style="background:var(--gold-glow);color:var(--gold);
                           font-size:0.7rem;padding:2px 8px;border-radius:20px;
                           border:1px solid var(--gold-border);">{note}</span>
            </div>""", unsafe_allow_html=True)

        gold_divider()
        tip_box("Email authentication will be added in the next development phase. The database schema and API endpoints are already designed.")
