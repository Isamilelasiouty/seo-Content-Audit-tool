"""Fallback page for unknown routes."""
import streamlit as st
from dashboard.components.ui import empty_state, gold_divider, page_header

def render():
    page_header("◌", "Page Not Found", "")
    empty_state("This page doesn't exist yet.", "◌")
    gold_divider()
    if st.button("← Back to Overview"):
        st.session_state.active_page = "overview"
        st.rerun()
